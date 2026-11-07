"""Per-call state and the rules every agent tool goes through.

The prompt asks the model to behave; this module makes sure it does. Anything
that costs money or touches safety is checked here, and a refused action raises
ActionRefused with a message telling the model exactly what to fix.
"""

import re
from collections.abc import Callable, Iterable
from datetime import datetime, timedelta
from typing import Any

from summit import config
from summit.models import Appointment, Customer, Membership, Priority
from summit.notify import Notifier
from summit.scheduling import AppointmentChanged, Option, Scheduler, say_day, say_window
from summit.service_area import AreaCheck, area_name, check_town, check_zip, place_in, property_kind
from summit.speech import normalize_phone, normalize_zip, say_phone, spoken_digits
from summit.store import Store
from summit.claims import false_claims
from summit.hazard_words import cannot_leave, hazard_in, leaving
from summit.triage import EMERGENCY, Assessment, Facts, assess, cannot_leave_script, safety_script


class ActionRefused(Exception):
    """The backend won't do what the model asked. The message says what's missing."""


def caller_turn_to_screen(items: Iterable[object]) -> tuple[str | None, str]:
    """From the chat history about to go to the model: the caller's latest words, if
    this is the first reply to them, and everything the agent has said so far.

    After a tool call the history ends in tool output rather than the caller's
    message; that turn was already screened, so there's nothing new to check.
    Duck-typed on LiveKit's chat items (type, role, text_content).
    """
    items = list(items)
    said = " ".join(
        i.text_content or ""
        for i in items
        if getattr(i, "type", None) == "message" and getattr(i, "role", None) == "assistant"
    )
    for item in reversed(items):
        kind, role = getattr(item, "type", None), getattr(item, "role", None)
        if kind == "message" and role == "user":
            return item.text_content or "", said
        if (kind == "message" and role == "assistant") or kind in ("function_call", "function_call_output"):
            return None, said
        # System notes, handoffs and config updates aren't a reply; keep looking.
    return None, said


# A P0 that only the word list raised can be a false alarm ("I asked if it smells like
# gas and she said no"). It stays P0: undoing an emergency is the riskier mistake. The
# caller who wanted a visit gets a person to arrange it instead of a dead end.
_WORDS_ONLY_CALLBACK = (
    "If the caller says there's no hazard at all and they still want a visit, don't argue and don't "
    "book: offer a callback from the office to arrange it (request_callback)."
)


# Asking what a repair or part costs. Matched as whole words: "part" used to match
# "apartment", "fan" matched "infant" and "total" matched "totally".
_REPAIR_COST_WORDS = ("repair", "repairs", "fix", "fixing", "part", "parts", "replace", "replacing", "how much will", "total")
# Components: a question about one of these is a repair question, unless it's about the visit.
_COMPONENT_WORDS = (
    "capacitor", "compressor", "motor", "fan", "coil", "blower", "igniter", "ignitor", "thermostat",
    "sensor", "circuit board", "control board", "valve", "refrigerant", "freon", "recharge", "leak",
)  # fmt: skip
_SYSTEM_WORDS = (
    "new system", "new unit", "new furnace", "new boiler", "new ac", "new a/c", "new air conditioner",
    "new heat pump", "whole system", "system replacement", "replace the system", "replace my system",
    "replace the furnace", "replace my furnace", "replace the ac", "replace my ac", "install",
    "replacement", "estimate",
)  # fmt: skip
_AFTER_HOURS_WORDS = (
    "after hours", "after-hours", "weekend", "night", "tonight", "evening", "sunday", "saturday",
    "holiday", "late",
)  # fmt: skip
_VISIT_WORDS = ("diagnos", "service call", "visit", "come out", "trip", "look at", "send someone")


def _any_word(text: str, words: Iterable[str]) -> bool:
    return any(re.search(rf"\b{re.escape(w)}\b", text) for w in words)


def _squash(text: str) -> str:
    return " ".join("".join(ch for ch in text.lower() if ch.isalnum() or ch.isspace()).split())


class CallSession:
    def __init__(
        self,
        call_id: str,
        caller_id: str | None,
        store: Store,
        cfg: dict[str, Any],
        notifier: Notifier | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.call_id = call_id
        self.caller_id = normalize_phone(caller_id)
        self.store = store
        self.cfg = cfg
        self.scheduler = Scheduler(store, cfg)
        self.notifier = notifier or Notifier(store)
        self.tz = config.timezone(cfg)
        self._clock = clock or (lambda: datetime.now(self.tz))
        self.started_at = self.now()

        self.caller_match: Customer | None = None  # who caller ID suggests; not proof
        self.customer: Customer | None = None  # set only once identity is verified
        # Who the caller said they are not. After a "no", caller ID stops counting as
        # a factor, and this person's account stays closed for the rest of the call.
        self.denied: Customer | None = None
        self.caller_id_denied = False
        self.lookup_attempts = 0
        self.facts = Facts()
        self.assessment: Assessment | None = None
        self.heard: set[str] = set()  # hazards found in the caller's own words
        self.hazard_place: dict[str, str] = {}  # ZIP/town said alongside the hazard, if any
        self.p0_script: str | None = None  # the script as first read, so it's read once
        self.caller_leaving = False
        self.area: AreaCheck | None = None
        self.property = "unknown"
        self.offered: dict[str, Option] = {}
        # What each offered option was for: None for a new visit, or the appointment being moved.
        self.offered_for: dict[str, int | None] = {}
        self.booked: list[int] = []
        self.callbacks: list[int] = []
        self.notes: list[str] = []
        self.outcome: str | None = None
        self.tool_log: list[dict[str, Any]] = []
        # Fixed words for the agent's next turn, spoken instead of a model reply
        # (a booking confirmation, so the model can't word one when nothing was booked).
        self.announcement: str | None = None
        self.false_claims: list[str] = []
        # Everything the agent has said so far, updated before each model turn. Read-backs
        # are checked against it rather than taken on the model's word.
        self.agent_said = ""

    def now(self) -> datetime:
        return self._clock().astimezone(self.tz)

    @property
    def priority(self) -> Priority | None:
        return self.assessment.priority if self.assessment else None

    @property
    def is_member(self) -> bool:
        return self.customer is not None and self.customer.membership == Membership.ACTIVE

    @property
    def callback_phone(self) -> str | None:
        return self.customer.phone if self.customer else self.caller_id

    # Identity

    def prefetch_caller(self) -> None:
        """Look up caller ID before we speak. A shared household number matches
        several people, in which case we don't guess a name."""
        if not self.caller_id:
            return
        matches = self.store.customers_by_phone(self.caller_id)
        if len(matches) == 1:
            self.caller_match = matches[0]

    def greeting(self) -> str:
        company = self.cfg["company"]["name"]
        if self.caller_match:
            return f"Thanks for calling {company}. Am I speaking with {self.caller_match.first_name}?"
        return f"Thanks for calling {company}, you've reached our automated assistant. How can I help?"

    MAX_LOOKUP_ATTEMPTS = 3

    def lookup_customer(
        self,
        confirmed_name: bool | None = None,
        phone: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        zip_code: str | None = None,
    ) -> str:
        if self.customer:
            return self._account_summary()

        if confirmed_name and self.caller_match:
            return self._verify(self.caller_match)
        if confirmed_name is False:
            # "No, I'm her son." Whoever this is, caller ID is now evidence of nothing,
            # and the person they said they aren't stays unverifiable on this call.
            self.denied = self.denied or self.caller_match
            self.caller_match = None
            self.caller_id_denied = True
            if not (phone or last_name or zip_code):
                return (
                    "Understood: they aren't the account holder. Don't share anything about that "
                    "account. You can still help them as a new customer. If they have their own "
                    "account, ask for the phone number on it, their last name and their ZIP code."
                )

        if self.caller_id_denied:
            number = normalize_phone(phone)
            if not (number and last_name and zip_code):
                raise ActionRefused(
                    "They said they aren't the person caller ID matches, so the number they're calling "
                    "from doesn't count. To look up their own account, ask for the phone number on it, "
                    "their last name and their ZIP code. Don't share anything until this succeeds."
                )
        else:
            number = normalize_phone(phone) or self.caller_id
            if not number or not (last_name or zip_code):
                raise ActionRefused(
                    "To look up an account, ask for the phone number on the account plus their "
                    "last name or ZIP code."
                )

        if self.lookup_attempts >= self.MAX_LOOKUP_ATTEMPTS:
            raise ActionRefused(
                "Too many lookup attempts on this call; don't try again. Don't share anything about "
                "any account. Help them as a new customer, or offer a callback from the office."
            )
        self.lookup_attempts += 1

        candidates = self.store.customers_by_phone(number)
        if last_name:
            candidates = [c for c in candidates if c.last_name.lower() == last_name.strip().lower()]
        if zip_code:
            candidates = [c for c in candidates if c.zip == normalize_zip(zip_code)]
        if first_name and len(candidates) > 1:
            wanted = first_name.strip().lower()
            candidates = [c for c in candidates if c.first_name.lower() == wanted]

        if len(candidates) == 1 and self.denied and candidates[0].id == self.denied.id:
            self.note(f"caller said they weren't {self.denied.full_name}, then gave that account's details")
            return (
                f"They told you earlier they aren't {self.denied.first_name}, so that account stays closed "
                "on this call even with matching details. Don't share anything about it. Help them as a "
                f"new customer, or {self.denied.first_name} can call us directly."
            )
        if len(candidates) == 1:
            return self._verify(candidates[0])
        if len(candidates) > 1:
            raise ActionRefused("More than one person on that account matches. Ask for their first name.")
        return (
            "No account matches those details. Carry on as a new customer and don't share "
            "anything about existing accounts."
        )

    def _verify(self, customer: Customer) -> str:
        self.customer = customer
        # Don't make a known customer repeat an address we already serve.
        on_file = check_zip(customer.zip, self.cfg)
        if on_file.in_area and self.area is None:
            self.area = on_file
            self.property = "residential"
        return "Verified. " + self._account_summary()

    def _account_summary(self) -> str:
        c = self.customer
        assert c is not None
        lines = [f"{c.full_name}, {c.address}, ZIP {c.zip} ({area_name(c.county, self.cfg)})."]
        if c.membership == Membership.ACTIVE:
            lines.append(f"Active {self.cfg['membership']['name']} member: thank them for being a member.")
        elif c.membership == Membership.LAPSED:
            lines.append(
                "Their membership has lapsed. After their problem is handled, you can mention "
                "renewing once; don't push."
            )
        else:
            lines.append("Not a member.")
        upcoming = self.store.upcoming_appointments(c.id, self.now().date())
        for appt in upcoming:
            lines.append(
                f"Upcoming: appointment #{appt.id}, {appt.job_type}, "
                f"{say_day(appt.day, self.now().date())}, {say_window(appt.window)}."
            )
        if self.area and self.area.zip == c.zip:
            lines.append("If the work is at this address you don't need to check the address again.")
        return " ".join(lines)

    # Triage and eligibility

    def assess_situation(self, facts: Facts) -> str:
        self.facts = self.facts.updated_with(facts)
        fresh = assess(self.facts, self.cfg, heard=self.heard, today=self.now().date())
        previous = self.assessment

        if previous and previous.priority <= fresh.priority:
            # Never lower priority mid-call. Keep asking the follow-ups, though.
            previous.ask_next = fresh.ask_next if fresh.priority == previous.priority else []
            if previous.priority == fresh.priority == Priority.P0:
                # The model confirming a hazard the screen heard turns "(caller's words)" into a report.
                previous.reasons = fresh.reasons
                return self.emergency_note() or ""
            return self._describe(previous, changed=False)

        self.assessment = fresh
        if fresh.priority == Priority.P0:
            return self._safety_emergency(fresh)
        voided = self._void_offers() if previous else ""
        if fresh.priority == Priority.P1:
            return self._urgent(fresh) + voided
        return self._describe(fresh, changed=previous is not None) + voided

    def _safety_emergency(self, assessment: Assessment) -> str:
        script = self.safety_script()
        what = ", ".join(assessment.reasons)
        # A visit booked earlier on this call would send a technician to a reported gas
        # leak with a routine ticket. Hold it; the dispatcher decides what happens to it.
        held = [a for a in self.booked if self.store.hold_appointment(a, f"{what} after booking")]
        alert = f"P0 {what}: {self._who()}"
        if self.hazard_place and not self.area:
            place = " ".join(v for k, v in self.hazard_place.items() if k in ("town", "zip"))
            county = self.hazard_place.get("county")
            alert += f". Location given: {place}" + (f" ({area_name(county, self.cfg)})" if county else "")
        if self.facts.description:
            alert += f'. Caller said: "{self.facts.description[-300:]}"'
        if held:
            alert += f". Appointment {', '.join(f'#{a}' for a in held)} from this call put on hold"
            self.note(f"appointment {', '.join(f'#{a}' for a in held)} put on hold after the hazard")
        if self.customer:
            others = [
                a.id for a in self.store.upcoming_appointments(self.customer.id, self.now().date())
                if a.id not in held
            ]
            if others:
                alert += f". Customer also has upcoming appointment {', '.join(f'#{a}' for a in others)}"
        self.notifier.alert(self.call_id, "critical", alert)
        self.outcome = "safety_emergency"
        # Times offered before the hazard came up are void.
        self._void_offers()
        return (
            f"SAFETY EMERGENCY ({what}). The dispatcher has been alerted. "
            f'Read this to the caller word for word: "{script}" '
            "Then stop. Don't collect booking details, and if they want to hang up and leave, let them."
        )

    def safety_script(self) -> str:
        """The script for this P0 call, fixed the first time it's worked out, so a county
        learned later doesn't make it count as "not read yet" and get read twice."""
        assert self.assessment and self.assessment.priority == Priority.P0
        if self.p0_script is None:
            county = (
                (self.area and self.area.county)
                or (self.caller_match and self.caller_match.county)
                or self.hazard_place.get("county")
            )
            self.p0_script = safety_script(self.assessment.hazard or "", county or None, self.cfg)
        return self.p0_script

    @property
    def hazard_from_words_only(self) -> bool:
        """P0 came only from the word list, never from the model's own report. The one case
        where it might be a false alarm ("skunk under the porch")."""
        return (
            self.priority == Priority.P0
            and self.assessment is not None
            and all(r.endswith("(caller's words)") for r in self.assessment.reasons)
        )

    def _place_in(self, text: str) -> dict[str, str]:
        """A ZIP or one of our towns said in the same sentence as the hazard."""
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            if not hazard_in(sentence):
                continue
            place: dict[str, str] = {}
            named = place_in(sentence, self.cfg)
            if named:
                place["town"] = named[0]
                if named[1]:
                    place["county"] = named[1]
            zip_match = re.search(r"\b\d{5}\b", sentence)
            if zip_match:
                place["zip"] = zip_match[0]
                check = check_zip(zip_match[0], self.cfg)
                if check.in_area and check.county:
                    # A ZIP is more precise than a town name.
                    place["county"] = check.county
            if place:
                return place
        return {}

    # The caller's own words

    def screen_caller_turn(self, text: str, said_so_far: str = "") -> str | None:
        """Runs on each caller turn before the model answers it. Returns fixed words
        to say instead of a model reply, or None to let the model answer.

        Gas, CO or fire in the caller's words makes the call P0 here, whatever the
        model would have reported. Once a call is P0, the safety script is read verbatim
        if it hasn't been yet (`said_so_far` is everything the agent has said), and
        a caller who says they can't get out hears a fixed answer instead of an
        improvised one.
        """
        hazard = hazard_in(text)
        if hazard and self.priority != Priority.P0:
            self.heard.add(hazard)
            self.hazard_place = self._place_in(text)
            result = self.assess_situation(Facts(description=text.strip()))
            self.log_tool("hazard_screen", {"heard": text, "hazard": hazard, **self.hazard_place}, result)
        if self.priority != Priority.P0:
            return None

        script = self.safety_script()
        if _squash(script) not in _squash(said_so_far):
            return script
        if cannot_leave(text):
            assert self.assessment
            self.caller_leaving = False
            self.note("caller said they can't leave; told to call 911 from inside")
            return cannot_leave_script(self.assessment.hazard or "")
        if leaving(text):
            self.caller_leaving = True
        return None

    def emergency_note(self) -> str | None:
        """Standing orders for the model for the rest of a P0 call.

        This used to tell the model to bring every answer back to leaving and calling
        nine-one-one, so it repeated the script to callers who'd already said goodbye.
        The script has been read; the note is about not undoing it.
        """
        if self.priority != Priority.P0:
            return None
        assert self.assessment
        if self.caller_leaving:
            return (
                "SAFETY EMERGENCY: the caller has heard the safety instructions and is leaving. Say one "
                'short goodbye, like "Okay. Please stay safe. Goodbye.", and end the call (end_call). '
                "Don't repeat the instructions."
            )
        note = (
            f"SAFETY EMERGENCY on this call ({', '.join(self.assessment.reasons)}). The caller has "
            "already heard the safety instructions and the dispatcher has been alerted. Don't repeat the "
            "instructions unless they ask what to do or say they're staying inside. Don't ask for anything, "
            "don't offer times and don't book. Answer questions in one short sentence. If they say they're "
            "leaving or say goodbye, say one short goodbye and end the call (end_call). Say the number as "
            f'"{EMERGENCY}", never "911".'
        )
        if self.hazard_from_words_only:
            note += " " + _WORDS_ONLY_CALLBACK
        return note

    def _urgent(self, assessment: Assessment) -> str:
        now = self.now()
        after_hours = not config.office_open(self.cfg, now)
        # A flag for whoever is on call, on the dashboard (and Slack if configured). Nothing pages
        # a phone yet, so the caller isn't told anyone "has been alerted".
        note = " After hours: flag for the on-call technician." if after_hours else ""
        self.notifier.alert(
            self.call_id, "urgent", f"P1 {', '.join(assessment.reasons)}: {self._who()}.{note}"
        )
        text = self._describe(assessment, changed=True)
        if after_hours:
            text += (
                " The office is closed; this has been flagged for the on-call technician. Don't promise "
                "a call from them: book the window, or set an urgent callback if there isn't one."
            )
        return text

    def _describe(self, assessment: Assessment, changed: bool) -> str:
        priority = assessment.priority
        verb = "is now" if changed else "is"
        parts = [f"Priority {verb} {priority.label} ({', '.join(assessment.reasons)})."]
        if priority == Priority.P1:
            hours = self.cfg["triage"]["p1_within_hours"]
            parts.append(f"Offer the earliest window; it has to be within {hours} hours.")
        if assessment.ask_next:
            parts.append(
                "Ask about "
                + " and ".join(assessment.ask_next)
                + ", then call assess_situation again: the answers can make it urgent."
            )
        if self.area is None and priority != Priority.P0:
            parts.append("Next, check the service address.")
        return " ".join(parts)

    def check_service_address(
        self,
        zip_code: str | None = None,
        town: str | None = None,
        property_type: str | None = None,
    ) -> str:
        before = (self.area and (self.area.county, self.area.zip), self.property)
        message = self._check_service_address(zip_code, town, property_type)
        after = (self.area and (self.area.county, self.area.zip), self.property)
        if after != before:
            # Times offered for the old address or property don't apply to the new one.
            message += self._void_offers()
        return message

    def _check_service_address(self, zip_code: str | None, town: str | None, property_type: str | None) -> str:
        if property_type:
            kind = property_kind(property_type)
            if kind != "unknown":
                self.property = kind
        if self.property == "commercial":
            self._set_outcome_unless_decided("commercial_lead")
            return (
                "That's a commercial property. We only service homes, so don't book. Offer to have "
                "the office call them back about it (request_callback, reason starting 'commercial lead')."
            )

        if zip_code:
            check = check_zip(zip_code, self.cfg)
            if check.zip is None and town:
                # The ZIP didn't come through; the town may still settle it.
                check = check_town(town, self.cfg)
        elif town:
            check = check_town(town, self.cfg)
        else:
            raise ActionRefused("Ask for the ZIP code of the address where the work is (or the town).")

        if check.in_area:
            self.area = check
        elif check.outside:
            self.area = None
            self._set_outcome_unless_decided("out_of_area")

        message = check.message
        if check.in_area and self.property == "unknown":
            message += " Also confirm it's a home (house, condo or apartment), not a business."
        return message

    def _void_offers(self) -> str:
        """Forget times offered so far. Returns a line for the model if there were any."""
        if not self.offered:
            return ""
        self.offered.clear()
        self.offered_for.clear()
        return (
            " The times offered earlier no longer apply. Don't book them; call "
            "find_appointment_options again if you get that far."
        )

    def _set_outcome_unless_decided(self, outcome: str) -> None:
        # A booking or a safety emergency outranks "turned away"; the latest turn-away wins otherwise.
        if self.outcome in (None, "out_of_area", "commercial_lead"):
            self.outcome = outcome

    # Scheduling

    def _refuse_if_emergency(self) -> None:
        if self.priority == Priority.P0:
            message = (
                "This is a safety emergency. Don't book or move anything on this call; the caller "
                "should be leaving the house."
            )
            if self.hazard_from_words_only:
                message += " " + _WORDS_ONLY_CALLBACK
            raise ActionRefused(message)

    def find_appointment_options(self, reschedule_appointment_id: int | None = None) -> str:
        self._refuse_if_emergency()
        if reschedule_appointment_id is not None:
            appointment = self._own_appointment(reschedule_appointment_id)
            county, priority = appointment.county, appointment.priority
        else:
            self._check_ready_to_schedule()
            assert self.assessment and self.area and self.area.county
            county, priority = self.area.county, self.assessment.priority

        options = self.scheduler.find_options(county, priority, self.is_member, self.now())
        if not options:
            if priority == Priority.P1:
                return self._no_urgent_capacity()
            if priority == Priority.P2 and reschedule_appointment_id is None:
                return self._no_p2_capacity()
            return (
                f"No openings in the next {self.cfg['scheduling']['horizon_days']} days. "
                "Apologize and offer a callback from the office."
            )

        self.offered.update({o.option_id: o for o in options})
        self.offered_for.update({o.option_id: reschedule_appointment_id for o in options})
        today = self.now().date()
        lines = []
        for option in options:
            surcharge = (
                f" (after-hours visit, +${self.cfg['pricing']['after_hours_surcharge']})"
                if option.after_hours
                else ""
            )
            lines.append(f"- {option.option_id}: {option.speakable(today)}{surcharge}")
        return (
            "Offer these arrival windows, earliest first. The technician arrives within the window.\n"
            + "\n".join(lines)
            + "\nBook with the option_id the caller picks."
        )

    def _check_ready_to_schedule(self) -> None:
        if self.assessment is None:
            raise ActionRefused("Find out what's wrong and call assess_situation before looking for times.")
        if self.property == "commercial":
            raise ActionRefused("Commercial property: no booking. Offer a callback from the office instead.")
        if self.area is None:
            raise ActionRefused("Check the service address first (check_service_address).")
        if self.property == "unknown":
            raise ActionRefused(
                "Confirm the service address is a home, then call check_service_address with property_type."
            )

    def _no_urgent_capacity(self) -> str:
        self.notifier.alert(
            self.call_id,
            "urgent",
            f"No P1 capacity within {self.cfg['triage']['p1_within_hours']}h for {self._who()}. "
            "Needs a dispatcher.",
        )
        minutes = self.cfg["escalation"]["urgent_callback_minutes"]
        if not self.callback_phone:
            return (
                "No urgent window is open in the next 24 hours, and the dispatcher has been alerted. "
                "Ask for the best number to reach them, then call request_callback with urgent=true."
            )
        self._add_callback(self.callback_phone, "Urgent: no P1 capacity, dispatcher to arrange", urgent=True)
        return (
            "No urgent window is open in the next 24 hours. The dispatcher has been alerted and will "
            f"call {say_phone(self.callback_phone)} within {minutes} minutes to arrange it. "
            "Tell the caller exactly that."
        )

    def _no_p2_capacity(self) -> str:
        hours = self.cfg["triage"]["p2_within_hours"]
        self.notifier.alert(
            self.call_id, "urgent", f"No P2 capacity within {hours}h for {self._who()}. Needs a dispatcher."
        )
        if not self.callback_phone:
            return (
                f"Nothing is open in the next {hours} hours, and the dispatcher has been alerted. Ask for "
                "the best number to reach them, then call request_callback so the office can fit them in."
            )
        due = self._add_callback(self.callback_phone, f"No P2 window within {hours}h; dispatcher to fit in", urgent=False)
        return (
            f"Nothing is open in the next {hours} hours. The dispatcher has been alerted, and the office will "
            f"call {say_phone(self.callback_phone)} {self._say_due(due, False)} to fit them in. Tell the caller "
            "exactly that."
        )

    def book_appointment(
        self,
        option_id: str,
        first_name: str,
        last_name: str,
        phone: str,
        address: str,
        zip_code: str,
        job_type: str,
        notes: str,
        phone_read_back_confirmed: bool,
        address_read_back_confirmed: bool,
    ) -> str:
        option = self.offered.get(option_id)
        phone_e164 = normalize_phone(phone)
        zip5 = normalize_zip(zip_code)

        self._refuse_if_emergency()
        problems = []
        if self.booked:
            problems.append(
                f"this call already booked appointment #{self.booked[-1]}; use change_appointment to move it"
            )
        if option is None or self.offered_for.get(option_id) is not None:
            problems.append(
                f"'{option_id}' wasn't offered for a new visit on this call; use an option_id from "
                "find_appointment_options"
            )
        else:
            stale = self._stale_reason(option)
            if stale:
                self.offered.pop(option_id, None)
                problems.append(
                    f"the call changed since '{option_id}' was offered ({stale}); call "
                    "find_appointment_options again and offer the new times"
                )
        required = {
            "first name": first_name, "last name": last_name, "phone number": phone,
            "street address": address, "ZIP code": zip_code, "what the job is": job_type,
        }  # fmt: skip
        missing = [label for label, value in required.items() if not (value or "").strip()]
        if missing:
            problems.append("missing " + ", ".join(missing))
        if phone and not phone_e164:
            problems.append(f"'{phone}' isn't a valid 10-digit US phone number")
        if zip_code and (self.area is None or zip5 != self.area.zip):
            checked = self.area.zip if self.area else "none"
            problems.append(
                f"ZIP {zip5 or zip_code} doesn't match the ZIP checked for the service area ({checked}); "
                "confirm the address and run check_service_address again"
            )
        if not phone_read_back_confirmed or (phone_e164 and not self._read_back_phone(phone_e164)):
            problems.append("read the phone number back digit by digit and get a yes")
        if not address_read_back_confirmed or not self._read_back_address(address):
            problems.append("read the full address back and get a yes")
        if problems:
            raise ActionRefused("Not booked yet: " + "; ".join(problems) + ".")

        assert option and phone_e164 and zip5 and self.assessment
        customer_id = self._customer_for_booking(
            first_name, last_name, phone_e164, address, zip5, option.county
        )
        appointment_id = self.scheduler.book(
            option,
            customer_id=customer_id,
            call_id=self.call_id,
            job_type=job_type.strip(),
            priority=self.assessment.priority,
            service_address=f"{address.strip()}, {zip5}",
            contact_name=f"{first_name.strip()} {last_name.strip()}",
            contact_phone=phone_e164,
            notes=self._technician_notes(notes),
        )
        if appointment_id is None:
            self._slot_taken(option)

        self.booked.append(appointment_id)
        self.outcome = "booked"
        today = self.now().date()
        self.announcement = (
            f"You're booked. A technician will arrive {option.speakable(today)}, at {address.strip()}. "
            f"{self._spoken_price(job_type, option.after_hours)} Is there anything else I can help with?"
        )
        return (
            f"Booked: appointment #{appointment_id}. This confirmation is being read to the caller word "
            f'for word, so don\'t repeat it: "{self.announcement}"' + self._membership_nudge()
        )

    def _read_back_phone(self, phone_e164: str) -> bool:
        """The agent actually said these ten digits, in any spoken form ("516-555-0142",
        "five one six, five five five, oh one four two")."""
        return phone_e164.removeprefix("+1") in spoken_digits(self.agent_said)

    def _read_back_address(self, address: str) -> bool:
        """The agent said the house number and the street name."""
        words = re.findall(r"[a-z0-9]+", address.lower())
        if not words:
            return False
        said = self.agent_said.lower()
        number = words[0] if words[0][0].isdigit() else None
        street = next((w for w in words[1:] if not w.isdigit() and len(w) > 1), None) if number else words[0]
        if number and not re.search(rf"\b{number}\b", said):
            return False
        return street is None or re.search(rf"\b{re.escape(street)}", said) is not None

    def _stale_reason(self, option: Option) -> str | None:
        """Re-check an offered option against the call as it is now, not as it was when offered."""
        if self.property != "residential":
            return "the property isn't confirmed as a home"
        if self.area is None or self.area.county != option.county:
            where = area_name(self.area.county, self.cfg) if self.area and self.area.county else "no checked address"
            return f"that window is for {area_name(option.county, self.cfg)} and the address is now {where}"
        assert self.assessment
        return self.scheduler.still_fits(option, self.assessment.priority, self.is_member, self.now())

    def _customer_for_booking(
        self, first_name: str, last_name: str, phone: str, address: str, zip5: str, county: str
    ) -> int:
        if self.customer:
            return self.customer.id
        # Unverified callers on a number we know get attached to that customer, but
        # their record is left alone: we can't tell a spouse from a stranger here.
        existing = self.store.customers_by_phone(phone)
        if existing:
            return existing[0].id
        return self.store.add_customer(
            first_name.strip(), last_name.strip(), phone, address.strip(), zip5, county
        )

    def change_appointment(self, appointment_id: int, option_id: str) -> str:
        self._refuse_if_emergency()
        appointment = self._own_appointment(appointment_id)
        option = self.offered.get(option_id)
        if option is None or self.offered_for.get(option_id) != appointment_id:
            raise ActionRefused(
                f"'{option_id}' wasn't offered for appointment #{appointment_id}. Call "
                f"find_appointment_options with reschedule_appointment_id={appointment_id} first."
            )
        stale = self.scheduler.still_fits(option, appointment.priority, self.is_member, self.now())
        if stale or option.county != appointment.county:
            self.offered.pop(option_id, None)
            raise ActionRefused(
                f"'{option_id}' no longer fits appointment #{appointment_id} ({stale or 'different county'}). "
                f"Call find_appointment_options with reschedule_appointment_id={appointment_id} again."
            )
        assert self.customer
        try:
            new_id = self._move(appointment, option)
        except AppointmentChanged:
            raise ActionRefused(
                f"Appointment #{appointment_id} was changed by another call a moment ago, so nothing was "
                "moved. Tell the caller, and call lookup_customer to see their appointments as they are now."
            ) from None
        if new_id is None:
            self._slot_taken(option, reschedule_appointment_id=appointment.id)

        self.booked.append(new_id)
        self.outcome = "rescheduled"
        today = self.now().date()
        self.announcement = (
            f"Done. Your {appointment.job_type} is now {option.speakable(today)}, and the old time has "
            "been released. Is there anything else I can help with?"
        )
        return (
            f"Moved: appointment #{new_id}. This confirmation is being read to the caller word for word, "
            f'so don\'t repeat it: "{self.announcement}"'
        )

    def _move(self, appointment: Appointment, option: Option) -> int | None:
        assert self.customer
        return self.scheduler.move(
            appointment.id,
            option,
            customer_id=self.customer.id,
            call_id=self.call_id,
            job_type=appointment.job_type,
            priority=appointment.priority,
            service_address=appointment.service_address,
            contact_name=self.customer.full_name,
            contact_phone=self.customer.phone,
            notes=f"Moved from appointment #{appointment.id}.",
        )

    def _own_appointment(self, appointment_id: int) -> Appointment:
        if self.customer is None:
            raise ActionRefused(
                "Verify who they are (lookup_customer) before touching an existing appointment."
            )
        appointment = self.store.get_appointment(appointment_id)
        if (
            appointment is None
            or appointment.customer_id != self.customer.id
            or appointment.status != "booked"
        ):
            raise ActionRefused(
                f"Appointment #{appointment_id} isn't an upcoming appointment on this account."
            )
        return appointment

    def _slot_taken(self, option: Option, reschedule_appointment_id: int | None = None) -> None:
        self.offered.pop(option.option_id, None)
        try:
            alternatives = self.find_appointment_options(reschedule_appointment_id)
        except ActionRefused:
            alternatives = "Offer to look for other times."
        raise ActionRefused(
            "That window was just taken by another booking. Apologize, then offer these instead. "
            + alternatives
        )

    # Escalation

    def request_callback(self, phone: str, reason: str, urgent: bool = False, name: str | None = None) -> str:
        number = normalize_phone(phone)
        if number is None and phone and "this" in phone.lower():
            number = self.callback_phone
        if number is None:
            raise ActionRefused("Need a valid 10-digit number for the callback. Ask for it and read it back.")
        if not reason.strip():
            raise ActionRefused("Say what the callback is about (reason).")

        due = self._add_callback(number, reason.strip(), urgent=urgent, name=name)
        if urgent:
            self.notifier.alert(self.call_id, "urgent", f"Urgent callback for {say_phone(number)}: {reason}")
        if self.outcome is None:
            self.outcome = "callback"
        return (
            f"Callback set: the office will call {say_phone(number)} {self._say_due(due, urgent)}. "
            "Tell the caller exactly that."
        )

    def _add_callback(self, phone: str, reason: str, urgent: bool, name: str | None = None) -> datetime:
        now = self.now()
        if urgent:
            due = now + timedelta(minutes=self.cfg["escalation"]["urgent_callback_minutes"])
        else:
            target = now + timedelta(hours=self.cfg["escalation"]["callback_hours"])
            due = config.next_office_opening(self.cfg, target)
        callback_id = self.store.add_callback(self.call_id, phone, reason, due, urgent=urgent, name=name)
        self.callbacks.append(callback_id)
        return due

    def _say_due(self, due: datetime, urgent: bool) -> str:
        if urgent:
            return f"within {self.cfg['escalation']['urgent_callback_minutes']} minutes"
        hour = due.strftime("%I:%M %p").lstrip("0").replace(":00", "")
        return f"by {hour} {say_day(due.date(), self.now().date())}"

    def plan_transfer(self) -> tuple[str | None, str]:
        """(number to transfer to, or None) and what the model should do next."""
        number = self.cfg["escalation"]["human_transfer_number"]
        if not number:
            return None, (
                "There's no live transfer line. Tell the caller you can't put them through right now "
                "and offer a callback from the office."
            )
        if not config.office_open(self.cfg, self.now()):
            return None, (
                "The office is closed, so nobody can take a transfer right now. Offer a callback "
                "(urgent if it's an urgent problem)."
            )
        return number, "Transferring the caller to the office now."

    def transfer_failed(self) -> str:
        self.notes.append("live transfer failed")
        if not self.callback_phone:
            return "The transfer didn't go through. Apologize and ask for a number for an urgent callback."
        self._add_callback(self.callback_phone, "Asked for a person; transfer failed", urgent=True)
        self.notifier.alert(self.call_id, "urgent", f"Transfer failed for {self._who()}; callback due")
        minutes = self.cfg["escalation"]["urgent_callback_minutes"]
        return (
            f"The transfer didn't go through. An urgent callback is set for {say_phone(self.callback_phone)} "
            f"within {minutes} minutes. Apologize and tell the caller exactly that."
        )

    def get_pricing(self, item: str) -> str:
        if not any(n.startswith("asked about pricing") for n in self.notes):
            self.note(f"asked about pricing ({item.strip()[:80]})")
        text = item.lower()
        p = self.cfg["pricing"]
        after_hours = _any_word(text, _AFTER_HOURS_WORDS)
        surcharge = f" Visits outside office hours add ${p['after_hours_surcharge']}." if after_hours else ""
        system = _any_word(text, _SYSTEM_WORDS)
        visit = any(w in text for w in _VISIT_WORDS)  # stems: "diagnos" covers diagnostic
        repair = (_any_word(text, _REPAIR_COST_WORDS) and not system) or (
            _any_word(text, _COMPONENT_WORDS) and not visit
        )
        # Repairs and parts first: "a replacement capacitor" is a repair, not a free estimate.
        if repair:
            # No figure at all here: a "$129" next to "capacitor" gets relayed as the part's price.
            return (
                "Don't give a price for the repair or the part. The technician diagnoses it and quotes on "
                "site before any work starts. If they ask what the visit costs, look up the diagnostic visit."
            )
        if system:
            return "Estimates for a new or replacement system are free."
        if "tune" in text or "maintenance" in text:
            return f"A tune-up is ${p['tune_up']}. Members get two a year included." + surcharge
        if _any_word(text, ("member", "members", "membership", "club", "plan")) and not visit:
            benefits = ", ".join(self.cfg["membership"]["benefits"])
            return f"{self.cfg['membership']['name']}: {benefits}. The office can go over membership pricing."
        if after_hours or visit or _any_word(text, ("appointment", "come", "cost", "charge", "fee")):
            # Always the base and the surcharge together, never "+$99" on its own.
            return self._diagnostic_price() + surcharge
        return "Don't estimate repairs. The technician quotes on site before any work starts."

    def _diagnostic_price(self) -> str:
        p = self.cfg["pricing"]
        if self.is_member:
            return f"The diagnostic visit is free for members (${p['diagnostic']} otherwise)."
        return f"The diagnostic visit is ${p['diagnostic']}; it's free for {self.cfg['membership']['name']} members."

    def _spoken_price(self, job_type: str, after_hours: bool) -> str:
        """The price line of the spoken confirmation, from config only."""
        p = self.cfg["pricing"]
        job = job_type.lower()
        if "tune" in job or "maintenance" in job:
            price = "The tune-up is included in your membership." if self.is_member else f"The tune-up is ${p['tune_up']}."
        elif "estimate" in job or "replacement" in job:
            price = "The estimate is free."
        elif self.is_member:
            price = "As a member there's no diagnostic fee, and the technician will quote any repair before starting."
        else:
            price = (
                f"The diagnostic visit is ${p['diagnostic']}, and the technician will quote any repair "
                "before starting."
            )
        if after_hours:
            price += f" Because it's outside regular hours, there's an extra ${p['after_hours_surcharge']}."
        return price

    def take_announcement(self) -> str | None:
        """Fixed words for the next agent turn, once."""
        text, self.announcement = self.announcement, None
        return text

    def _membership_nudge(self) -> str:
        if self.is_member or (self.customer and self.customer.membership == Membership.LAPSED):
            return ""
        benefits = ", ".join(self.cfg["membership"]["benefits"])
        return (
            f" If you haven't yet, you can mention the {self.cfg['membership']['name']} once "
            f"({benefits}). Don't push it."
        )

    # Record keeping

    def log_tool(self, name: str, args: dict[str, Any], result: str, refused: bool = False) -> None:
        self.tool_log.append(
            {"tool": name, "args": args, "result": result, "refused": refused, "at": self.now().isoformat()}
        )
        self.save()

    def note(self, text: str) -> None:
        self.notes.append(text)

    def save(self, transcript: list[dict[str, Any]] | None = None, ended: bool = False) -> None:
        self.store.upsert_call(
            self.call_id,
            caller_id=self.caller_id,
            started_at=self.started_at,
            ended_at=self.now() if ended else None,
            priority=self.priority,
            outcome=self.outcome,
            summary=self.technician_summary(),
            record=self.record(),
            transcript=transcript,
        )

    def finalize(self, transcript: list[dict[str, Any]]) -> None:
        """Called at hang-up. A triaged caller we didn't book still gets a callback, whether
        or not we got as far as their address: the callback goes to a phone, not a house."""
        needs_follow_up = (
            self.outcome in (None, "callback")
            and self.priority is not None
            and self.priority != Priority.P0
            and not self.booked
            and not self.callbacks
        )
        if needs_follow_up:
            if self.callback_phone:
                self._add_callback(
                    self.callback_phone,
                    "Call ended before booking",
                    urgent=self.priority == Priority.P1,
                )
                self.outcome = "callback"
            else:
                self.outcome = "abandoned"
        self._flag_false_claims(transcript)
        if self.outcome is None:
            self.outcome = "info_only" if self.tool_log else "abandoned"
        self.save(transcript=transcript, ended=True)

    def _flag_false_claims(self, transcript: list[dict[str, Any]]) -> None:
        """The agent said it booked something, or that someone will call, and the records
        say otherwise. The caller is now expecting a technician or a call that isn't coming,
        so the office has to hear about it."""
        said = " ".join(t.get("text", "") for t in transcript if t.get("role") == "assistant")
        # A customer's existing appointment can back "you're scheduled for Thursday", but not
        # a claim that today's new problem was booked when nothing was.
        new_problem = self.priority in (Priority.P1, Priority.P2)
        has_booking = bool(self.booked) or bool(
            self.customer
            and not new_problem
            and self.store.upcoming_appointments(self.customer.id, self.now().date())
        )
        self.false_claims = false_claims(said, has_booking=has_booking, has_callback=bool(self.callbacks))
        if not self.false_claims:
            return
        self.note("REVIEW: " + "; ".join(self.false_claims))
        self.notifier.alert(
            self.call_id,
            "urgent",
            f"Agent told {self._who()} something the records don't show: {self.false_claims[0]}. Call them back.",
        )
        if self.callback_phone and not self.callbacks:
            self._add_callback(self.callback_phone, "Agent wrongly told the caller it was booked or arranged", urgent=True)

    def technician_summary(self) -> str:
        parts = []
        if self.assessment:
            parts.append(f"{self.assessment.priority.label}: {', '.join(self.assessment.reasons)}.")
        if self.facts.description:
            parts.append(f"Caller says: {self.facts.description}.")
        if self.facts.indoor_temp_f is not None:
            parts.append(f"{self.facts.indoor_temp_f}°F inside.")
        if self.facts.vulnerable_occupant:
            parts.append("Vulnerable occupant at home.")
        if self.customer:
            status = "member" if self.is_member else self.customer.membership.value
            parts.append(f"Customer: {self.customer.full_name} ({status}, verified).")
        elif self.caller_id:
            parts.append(f"Caller {say_phone(self.caller_id)} (not verified).")
        if self.notes:
            parts.append("Notes: " + "; ".join(self.notes) + ".")
        return " ".join(parts)

    def _technician_notes(self, caller_notes: str) -> str:
        summary = self.technician_summary()
        return f"{summary} {caller_notes.strip()}".strip()

    def record(self) -> dict[str, Any]:
        return {
            "caller_id": self.caller_id,
            "verified_customer_id": self.customer.id if self.customer else None,
            "facts": self.facts.known(),
            "priority": int(self.priority) if self.priority is not None else None,
            "reasons": self.assessment.reasons if self.assessment else [],
            "service_area": {"county": self.area.county, "zip": self.area.zip} if self.area else None,
            "property": self.property,
            "offered": sorted(self.offered),
            "appointments": self.booked,
            "callbacks": self.callbacks,
            "notes": self.notes,
            "false_claims": self.false_claims,
            "outcome": self.outcome,
            "tools": self.tool_log,
        }

    def _who(self) -> str:
        if self.customer:
            name = self.customer.full_name
        elif self.caller_match:
            # Caller ID isn't identity: the person on the line may be a spouse or a guest.
            name = f"unverified caller; caller ID matches {self.caller_match.full_name}"
        else:
            name = "unknown caller"
        phone = say_phone(self.callback_phone) if self.callback_phone else "no number"
        place = f", {area_name(self.area.county, self.cfg)}" if self.area and self.area.county else ""
        return f"{name} ({phone}{place})"
