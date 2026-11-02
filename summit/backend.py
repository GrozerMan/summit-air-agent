"""Per-call state and the rules every agent tool goes through.

The prompt asks the model to behave; this module makes sure it does. Anything
that costs money or touches safety is checked here, and a refused action raises
ActionRefused with a message telling the model exactly what to fix.
"""

from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from summit import config
from summit.models import Appointment, Customer, Membership, Priority
from summit.notify import Notifier
from summit.scheduling import Option, Scheduler, say_day, say_window
from summit.service_area import AreaCheck, check_town, check_zip, property_kind
from summit.speech import normalize_phone, normalize_zip, say_phone
from summit.store import Store
from summit.triage import Assessment, Facts, assess, safety_script


class ActionRefused(Exception):
    """The backend won't do what the model asked. The message says what's missing."""


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
        self.facts = Facts()
        self.assessment: Assessment | None = None
        self.area: AreaCheck | None = None
        self.property = "unknown"
        self.offered: dict[str, Option] = {}
        self.booked: list[int] = []
        self.callbacks: list[int] = []
        self.notes: list[str] = []
        self.outcome: str | None = None
        self.tool_log: list[dict[str, Any]] = []

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
            self.caller_match = None

        number = normalize_phone(phone) or self.caller_id
        if not number or not (last_name or zip_code):
            raise ActionRefused(
                "To look up an account, ask for the phone number on the account plus their "
                "last name or ZIP code."
            )

        candidates = self.store.customers_by_phone(number)
        if last_name:
            candidates = [c for c in candidates if c.last_name.lower() == last_name.strip().lower()]
        if zip_code:
            candidates = [c for c in candidates if c.zip == normalize_zip(zip_code)]
        if first_name and len(candidates) > 1:
            wanted = first_name.strip().lower()
            candidates = [c for c in candidates if c.first_name.lower() == wanted]

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
        lines = [f"{c.full_name}, {c.address}, ZIP {c.zip} ({c.county} County)."]
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
        fresh = assess(self.facts, self.cfg)
        previous = self.assessment

        if previous and previous.priority <= fresh.priority:
            # Never lower priority mid-call. Keep asking the follow-ups, though.
            previous.ask_next = fresh.ask_next if fresh.priority == previous.priority else []
            return self._describe(previous, changed=False)

        self.assessment = fresh
        if fresh.priority == Priority.P0:
            return self._safety_emergency(fresh)
        if fresh.priority == Priority.P1:
            return self._urgent(fresh)
        return self._describe(fresh, changed=previous is not None)

    def _safety_emergency(self, assessment: Assessment) -> str:
        county = (self.area and self.area.county) or (self.caller_match and self.caller_match.county)
        script = safety_script(assessment.hazard or "", county or None, self.cfg)
        who = self._who()
        self.notifier.alert(self.call_id, "critical", f"P0 {', '.join(assessment.reasons)}: {who}")
        self.outcome = "safety_emergency"
        return (
            f"SAFETY EMERGENCY ({', '.join(assessment.reasons)}). The dispatcher has been alerted. "
            f'Read this to the caller word for word: "{script}" '
            "Then stop. Don't collect booking details, and if they want to hang up and leave, let them."
        )

    def _urgent(self, assessment: Assessment) -> str:
        now = self.now()
        after_hours = not config.office_open(self.cfg, now)
        note = " After hours: page on-call." if after_hours else ""
        self.notifier.alert(
            self.call_id, "urgent", f"P1 {', '.join(assessment.reasons)}: {self._who()}.{note}"
        )
        text = self._describe(assessment, changed=True)
        if after_hours:
            text += " The office is closed, so the on-call technician has been alerted too."
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
            if check.ask_town and town:
                check = check_town(town, self.cfg, zip_code=check.zip)
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

    def _set_outcome_unless_decided(self, outcome: str) -> None:
        # A booking or a safety emergency outranks "turned away"; the latest turn-away wins otherwise.
        if self.outcome in (None, "out_of_area", "commercial_lead"):
            self.outcome = outcome

    # Scheduling

    def find_appointment_options(self, reschedule_appointment_id: int | None = None) -> str:
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
            return (
                f"No openings in the next {self.cfg['scheduling']['horizon_days']} days. "
                "Apologize and offer a callback from the office."
            )

        self.offered.update({o.option_id: o for o in options})
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
        if self.assessment.priority == Priority.P0:
            raise ActionRefused("This is a safety emergency. Don't book anything on this call.")
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

        problems = []
        if self.priority == Priority.P0:
            raise ActionRefused("This is a safety emergency. Don't book anything on this call.")
        if self.booked:
            problems.append(
                f"this call already booked appointment #{self.booked[-1]}; use change_appointment to move it"
            )
        if option is None:
            problems.append(
                f"'{option_id}' wasn't offered on this call; use an option_id from find_appointment_options"
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
        if not phone_read_back_confirmed:
            problems.append("read the phone number back digit by digit and get a yes")
        if not address_read_back_confirmed:
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
        return (
            f"Booked: appointment #{appointment_id}, {option.speakable(today)}, at {address.strip()}. "
            f"{self._visit_price(job_type, option.after_hours)} "
            "Confirm the day, the window and the address back to the caller." + self._membership_nudge()
        )

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
        appointment = self._own_appointment(appointment_id)
        option = self.offered.get(option_id)
        if option is None:
            raise ActionRefused(
                f"'{option_id}' wasn't offered. Call find_appointment_options with "
                f"reschedule_appointment_id={appointment_id} first."
            )
        assert self.customer
        new_id = self.scheduler.move(
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
        if new_id is None:
            self._slot_taken(option)

        self.booked.append(new_id)
        self.outcome = "rescheduled"
        today = self.now().date()
        return (
            f"Moved: the {appointment.job_type} is now {option.speakable(today)} "
            f"(appointment #{new_id}), and the old time has been released. "
            "Confirm the new time with the caller."
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

    def _slot_taken(self, option: Option) -> None:
        self.offered.pop(option.option_id, None)
        try:
            alternatives = self.find_appointment_options()
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
        text = item.lower()
        p = self.cfg["pricing"]
        if any(w in text for w in ("estimate", "replacement", "new system", "new unit", "install")):
            return "Replacement estimates are free."
        if any(w in text for w in ("repair", "fix", "part", "compressor", "motor", "how much will", "total")):
            return "Don't estimate repairs. The technician quotes on site before any work starts."
        if "tune" in text or "maintenance" in text:
            return f"A tune-up is ${p['tune_up']}. Members get two a year included."
        if any(w in text for w in ("after", "weekend", "night", "evening", "sunday", "holiday")):
            return f"After-hours visits add ${p['after_hours_surcharge']}."
        if any(w in text for w in ("member", "club", "plan")):
            benefits = ", ".join(self.cfg["membership"]["benefits"])
            return f"{self.cfg['membership']['name']}: {benefits}. The office can go over membership pricing."
        if any(w in text for w in ("diagnos", "service call", "visit", "come out", "trip", "look at")):
            if self.is_member:
                return f"The diagnostic visit is free for members (${p['diagnostic']} otherwise)."
            club = self.cfg["membership"]["name"]
            return f"The diagnostic visit is ${p['diagnostic']}; it's free for {club} members."
        return "Don't estimate repairs. The technician quotes on site before any work starts."

    def _visit_price(self, job_type: str, after_hours: bool) -> str:
        p = self.cfg["pricing"]
        job = job_type.lower()
        if "tune" in job or "maintenance" in job:
            price = "Tune-up: included in membership." if self.is_member else f"Tune-up: ${p['tune_up']}."
        elif "estimate" in job or "replacement" in job:
            price = "The estimate is free."
        elif self.is_member:
            price = "No diagnostic fee as a member; any repair is quoted on site."
        else:
            price = f"Diagnostic fee ${p['diagnostic']}; any repair is quoted on site."
        if after_hours:
            price += f" After-hours visit: +${p['after_hours_surcharge']}."
        return price

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
        """Called at hang-up. A triaged caller we didn't book still gets a callback."""
        needs_follow_up = (
            self.outcome in (None, "callback")
            and self.priority is not None
            and self.priority != Priority.P0
            and self.area is not None
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
        if self.outcome is None:
            self.outcome = "info_only" if self.tool_log else "abandoned"
        self.save(transcript=transcript, ended=True)

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
            "outcome": self.outcome,
            "tools": self.tool_log,
        }

    def _who(self) -> str:
        person = self.customer or self.caller_match
        name = person.full_name if person else "unknown caller"
        phone = say_phone(self.callback_phone) if self.callback_phone else "no number"
        place = f", {self.area.county} County" if self.area and self.area.county else ""
        return f"{name} ({phone}{place})"
