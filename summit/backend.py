"""Per-call state and the rules every agent tool goes through.

The prompt asks the model to behave; this module makes sure it does. Anything
that costs money or touches safety is checked here, and a refused action raises
ActionRefused with a message telling the model exactly what to fix.
"""

import re
from collections.abc import Callable
from datetime import date, datetime, time, timedelta
from typing import Any

from summit import config, pricing
from summit.call_triage import TriageMixin, caller_turn_to_screen
from summit.identity import IdentityMixin
from summit.models import ActionRefused, Appointment, Customer, Membership, Priority
from summit.notify import Notifier
from summit.records import RecordsMixin, close_abandoned_calls
from summit.scheduling import AppointmentChanged, Option, Scheduler, say_day, say_window, window_bounds
from summit.service_area import AreaCheck, area_name, check_town, check_zip, property_kind
from summit.speech import normalize_phone, normalize_zip, say_confirmation, say_phone, spoken_digits
from summit.store import Store
from summit.triage import Assessment, Facts

_NYC_COUNTIES = {"Kings", "Queens", "Bronx", "New York", "Richmond"}

_WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


__all__ = ["ActionRefused", "CallSession", "caller_turn_to_screen", "close_abandoned_calls"]


class CallSession(IdentityMixin, TriageMixin, RecordsMixin):
    """One phone call: its state, and every tool the agent can call.

    Identity (identity.py), live triage and the P0 path (call_triage.py) and the call
    record (records.py) are mixins over this state; scheduling, addresses and escalation
    live here."""

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
        self.membership_asked = False
        self.facts = Facts()
        self.assessment: Assessment | None = None
        self.heard: set[str] = set()  # hazards found in the caller's own words
        self.hazard_place: dict[str, str] = {}  # ZIP/town said alongside the hazard, if any
        self.p0_script: str | None = None  # the script as first read, so it's read once
        self.caller_leaving = False
        self.area: AreaCheck | None = None
        self.area_from_file = False  # set from the verified account, not said on this call
        self.property = "unknown"
        # The heat or cooling comes from the building's own plant (an NYC rental with a
        # boiler in the basement): the landlord's job, not a visit we can book.
        self.building_system = False
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
        # Response times and usage, filled in at hang-up (summit/call_metrics.py).
        self.metrics: dict[str, Any] = {}

        # Booking attempts refused in a row on this request. At the limit the office is
        # asked to call back and finish it, rather than the caller being stuck in a loop.
        self.booking_failures = 0
        self.failure_callback_set = False
        self.caller_availability: str | None = None

    def now(self) -> datetime:
        return self._clock().astimezone(self.tz)

    @property
    def priority(self) -> Priority | None:
        return self.assessment.priority if self.assessment else None

    @property
    def is_member(self) -> bool:
        return self.membership == Membership.ACTIVE

    @property
    def membership(self) -> Membership | None:
        """The verified caller's membership today, or None if nobody is verified."""
        return self.customer.membership_on(self.now().date()) if self.customer else None

    @property
    def callback_phone(self) -> str | None:
        return self.customer.phone if self.customer else self.caller_id

    # Identity

    # Triage and eligibility

    def check_service_address(
        self,
        zip_code: str | None = None,
        town: str | None = None,
        property_type: str | None = None,
        heat_from_building: bool | None = None,
    ) -> str:
        before = (self.area and (self.area.county, self.area.zip), self.property, self.building_system)
        self.area_from_file = False
        if heat_from_building is not None:
            self.building_system = heat_from_building
        message = self._check_service_address(zip_code, town, property_type)
        after = (self.area and (self.area.county, self.area.zip), self.property, self.building_system)
        if after != before:
            # Times offered for the old address or property don't apply to the new one.
            message += self._void_offers()
        return message

    def _check_service_address(
        self, zip_code: str | None, town: str | None, property_type: str | None
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

        if self.building_system and (check.in_area or self.area):
            self._set_outcome_unless_decided("building_system")
            if not any(n.startswith("heat comes from the building") for n in self.notes):
                self.note("heat comes from the building: referred to landlord/super")
            nyc = self.area and self.area.county in _NYC_COUNTIES
            report = " In New York City they can also call 311 to report no heat." if nyc else ""
            return (
                "Their heat or cooling comes from the building's own system, which is the landlord's or "
                "building's responsibility, so don't book. Tell them kindly to contact their landlord or "
                f"building super.{report} If they own their unit's equipment after all, or want the office to "
                "call them, offer a callback (request_callback)."
            )

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
        if self.outcome in (None, "out_of_area", "commercial_lead", "building_system"):
            self.outcome = outcome

    # Scheduling

    def find_appointment_options(
        self,
        reschedule_appointment_id: int | None = None,
        caller_says_member: bool | None = None,
        days: list[str] | None = None,
        not_before: str | None = None,
        after_time: str | None = None,
        before_time: str | None = None,
    ) -> str:
        self._refuse_if_emergency()
        fits, wanted = self._availability_filter(days, not_before, after_time, before_time)
        if reschedule_appointment_id is not None:
            appointment = self._own_appointment(reschedule_appointment_id)
            county, priority = appointment.county, appointment.priority
        else:
            self._check_ready_to_schedule()
            self._check_membership_asked(caller_says_member)
            assert self.assessment and self.area and self.area.county
            county, priority = self.area.county, self.assessment.priority

        if wanted and wanted != self.caller_availability:
            self.caller_availability = wanted
            self.notes = [n for n in self.notes if not n.startswith("caller availability:")]
            self.note(f"caller availability: {wanted}")
        options = self.scheduler.find_options(county, priority, self.is_member, self.now(), fits=fits)
        header = ""
        if fits is not None and not options:
            # Nothing open when they said they're home: offer what is open, and say so,
            # rather than a dead end.
            options = self.scheduler.find_options(county, priority, self.is_member, self.now())
            if options:
                header = f"Nothing open fits what they said ({wanted}). Say so, and offer these nearest open windows instead."
                if priority == Priority.P1:
                    hours = self.cfg["triage"]["p1_within_hours"]
                    header += f" An urgent visit has to be within {hours} hours, so these are the options."
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
            (f"{header}\n" if header else "")
            + "Offer these arrival windows, earliest first. The technician arrives within the window.\n"
            + "\n".join(lines)
            + "\nBook with the option_id the caller picks."
            + self._tech_details_reminder()
        )

    def _availability_filter(
        self,
        days: list[str] | None,
        not_before: str | None,
        after_time: str | None,
        before_time: str | None,
    ) -> tuple[Callable[[date, str], bool] | None, str]:
        """When the caller said they can be home, as a test on (day, window), and in words for
        the ticket. A window fits only if it lies wholly inside what they said."""
        weekdays: set[int] = set()
        dates: set[date] = set()
        problems = []
        for raw in days or []:
            word = raw.strip().lower()
            if word in ("weekday", "weekdays"):
                weekdays.update(range(5))
            elif word in ("weekend", "weekends"):
                weekdays.update((5, 6))
            elif any(day.startswith(word[:3]) for day in _WEEKDAYS) and len(word) >= 3 and word.isalpha():
                weekdays.add(next(i for i, day in enumerate(_WEEKDAYS) if day.startswith(word[:3])))
            else:
                try:
                    dates.add(date.fromisoformat(word))
                except ValueError:
                    problems.append(f"days entry '{raw}' (use a weekday name, 'weekdays', or YYYY-MM-DD)")
        earliest_day = None
        if not_before:
            try:
                earliest_day = date.fromisoformat(not_before.strip())
            except ValueError:
                problems.append(f"not_before '{not_before}' (use YYYY-MM-DD)")
        after, before = _clock(after_time), _clock(before_time)
        if after_time and after is None:
            problems.append(f"after_time '{after_time}' (use 24-hour HH:MM, e.g. 15:00)")
        if before_time and before is None:
            problems.append(f"before_time '{before_time}' (use 24-hour HH:MM, e.g. 12:00)")
        if problems:
            raise ActionRefused(
                "Couldn't read the caller's availability: " + "; ".join(problems) + ". Try again."
            )
        if not (weekdays or dates or earliest_day or after or before):
            return None, ""

        def fits(day: date, window: str) -> bool:
            start, end = window_bounds(window)
            if (weekdays or dates) and day.weekday() not in weekdays and day not in dates:
                return False
            if earliest_day and day < earliest_day:
                return False
            if after and start < after:
                return False
            return not (before and end > before)

        words = []
        if weekdays or dates:
            named = [_WEEKDAYS[i].capitalize() for i in sorted(weekdays)]
            named += [f"{d:%A %B} {d.day}" for d in sorted(dates)]
            words.append(" or ".join(named))
        if earliest_day:
            words.append(f"from {earliest_day:%A %B} {earliest_day.day}")
        if after:
            words.append(f"after {_say_clock(after)}")
        if before:
            words.append(f"before {_say_clock(before)}")
        return fits, ", ".join(words)

    def _check_membership_asked(self, caller_says_member: bool | None) -> None:
        """No times exist until we know whether an unknown caller is already a member, so a
        member calling from a new number isn't charged the diagnostic fee or kept out of member
        times. A checkpoint in code: the times come back only after the answer is reported."""
        if self.customer:
            return
        if self.caller_match:
            raise ActionRefused(
                f"The greeting asked if this is {self.caller_match.first_name}. Report their answer with "
                "lookup_customer(confirmed_name=...) first."
            )
        if self.lookup_attempts:
            return  # they were looked up already; no match means a new customer
        club = self.cfg["membership"]["name"]
        if caller_says_member is None:
            self.membership_asked = True
            raise ActionRefused(
                f"Before offering times, ask once whether they're already a {club} member or have had us out "
                "before. Then call find_appointment_options again with caller_says_member set to their answer."
            )
        if caller_says_member:
            raise ActionRefused(
                "They say they're a member: verify them first (lookup_customer with the account's phone number, "
                "last name and ZIP), then call find_appointment_options again. Members get priority windows and "
                "no diagnostic fee."
            )
        self.membership_asked = True

    def _tech_details_reminder(self) -> str:
        return (
            "\nBefore booking, if they haven't said: what kind of system it is (furnace, boiler, heat pump, "
            "central AC, mini-split; gas, oil or electric), and anything the technician needs to get in "
            "(apartment number, gate or door code, pets, parking). Ask naturally, one at a time; pass them "
            "as equipment and access_notes."
        )

    def _check_ready_to_schedule(self) -> None:
        if self.assessment is None:
            raise ActionRefused("Find out what's wrong and call assess_situation before looking for times.")
        if self.property == "commercial":
            raise ActionRefused("Commercial property: no booking. Offer a callback from the office instead.")
        if self.building_system:
            raise ActionRefused(
                "The building supplies their heat or cooling: that's the landlord's to fix. No booking; "
                "suggest the landlord or super, or offer a callback."
            )
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
        due = self._add_callback(
            self.callback_phone, f"No P2 window within {hours}h; dispatcher to fit in", urgent=False
        )
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
        equipment: str | None = None,
        access_notes: str | None = None,
        name_read_back_confirmed: bool | None = None,
    ) -> str:
        try:
            result = self._book_appointment(
                option_id, first_name, last_name, phone, address, zip_code, job_type, notes,
                phone_read_back_confirmed, address_read_back_confirmed, equipment, access_notes,
                name_read_back_confirmed,
            )  # fmt: skip
        except ActionRefused as refused:
            if self.priority == Priority.P0:
                raise
            self.booking_failures += 1
            raise ActionRefused(str(refused) + self._after_failed_booking(phone)) from None
        self.booking_failures = 0
        return result

    def _after_failed_booking(self, phone: str) -> str:
        """After the limit of refused bookings in a row, the office takes over: a callback and
        an alert, once per request. The caller can still keep going if they'd rather."""
        limit = self.cfg["escalation"]["max_booking_failures"]
        if self.booking_failures < limit or self.failure_callback_set:
            return ""
        self.failure_callback_set = True
        urgent = self.priority == Priority.P1
        number = self.callback_phone or normalize_phone(phone)
        self.notifier.alert(
            self.call_id,
            "urgent" if urgent else "info",
            f"Agent couldn't complete a booking after {limit} tries for {self._who()}; office to finish it.",
        )
        self.note(f"booking failed {limit} times in a row; office to finish it")
        if not number:
            return (
                f" That's {limit} tries without a booking. Ask for the best number to reach them and set a "
                "callback (request_callback) so the office can finish it."
            )
        due = self._add_callback(
            number, f"Booking failed {limit} times on the call; finish booking", urgent=urgent
        )
        if self.outcome is None:
            self.outcome = "callback"
        return (
            f" That's {limit} tries without a booking, so a callback is now set: the office will call "
            f"{say_phone(number)} {self._say_due(due, urgent)} to finish it. Tell the caller that. If they'd "
            "rather keep going now, fix the above and try once more."
        )

    def _book_appointment(
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
        equipment: str | None,
        access_notes: str | None,
        name_read_back_confirmed: bool | None,
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
        if zip_code and self.area is not None and self.area.zip is None and zip5:
            # The address was checked by town only ("Syosset, don't know the ZIP"): the ZIP given
            # now must be one of ours, in the same county, and becomes the checked ZIP.
            by_zip = check_zip(zip5, self.cfg)
            if by_zip.in_area and by_zip.county == self.area.county:
                self.area = by_zip
        if zip_code and (self.area is None or zip5 != self.area.zip):
            checked = self.area.zip if self.area else "none"
            problems.append(
                f"ZIP {zip5 or zip_code} doesn't match the ZIP checked for the service area ({checked}); "
                "confirm the address and run check_service_address again"
            )
        if (
            self.customer is None
            and (first_name or "").strip()
            and (last_name or "").strip()
            and (name_read_back_confirmed is False or not self._read_back_name(first_name, last_name))
        ):
            # Speech-to-text mishears names without flagging it, and a wrong name ends up on the
            # ticket, on the technician's phone and on the next call's greeting.
            problems.append(
                "read their first and last name back (ask them to spell it if it's unusual or you're unsure) "
                "and get a yes"
            )
        if not phone_read_back_confirmed or (phone_e164 and not self._read_back_phone(phone_e164)):
            problems.append("read the phone number back digit by digit and get a yes")
        if address and address.strip() and not re.search(r"\d", address):
            problems.append("the street address needs a house number")
        elif not address_read_back_confirmed or not self._read_back_address(address):
            problems.append("read the full address back and get a yes")
        if problems:
            raise ActionRefused(
                "NOT BOOKED. Fix this: "
                + "; ".join(problems)
                + ". Then call book_appointment again. Nothing "
                "is booked, and you must not say it is, until book_appointment returns 'Booked'."
            )

        assert option and phone_e164 and zip5 and self.assessment
        customer_id, created = self._customer_for_booking(
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
            notes=self._technician_notes(notes, equipment=equipment, access_notes=access_notes),
        )
        if appointment_id is None:
            if created:
                self.store.delete_customer_without_history(customer_id)
            self._slot_taken(option)

        self.booked.append(appointment_id)
        self.outcome = "booked"
        today = self.now().date()
        self.announcement = (
            f"You're booked. A technician will arrive {option.speakable(today)}, at {address.strip()}. "
            f"{self._spoken_price(job_type, option.after_hours)} "
            f"Your confirmation number is {say_confirmation(appointment_id)}. Is there anything else I can help with?"
        )
        return (
            f"Booked: appointment #{appointment_id}. This confirmation is being read to the caller word "
            f'for word, so don\'t repeat it: "{self.announcement}"' + self._membership_nudge()
        )

    def _read_back_phone(self, phone_e164: str) -> bool:
        """The agent actually said these ten digits, in any spoken form ("516-555-0142",
        "five one six, five five five, oh one four two")."""
        return phone_e164.removeprefix("+1") in spoken_digits(self.agent_said)

    def _read_back_name(self, first_name: str, last_name: str) -> bool:
        """The agent said both names, whole ("Ortiz") or spelled out ("O-R-T-I-Z")."""
        said = self.agent_said.lower()
        for name in (first_name, last_name):
            letters = re.sub(r"[^a-z]", "", name.lower())
            if not letters:
                continue
            pattern = r"(?<![a-z])" + r"[\s\-.,']*".join(letters) + r"(?![a-z])"
            if not re.search(pattern, said):
                return False
        return True

    def _read_back_address(self, address: str) -> bool:
        """The agent said the house number and the street name."""
        words = re.findall(r"[a-z0-9]+", address.lower())
        if not words:
            return False
        said = self.agent_said.lower()
        number = words[0] if words[0][0].isdigit() else None
        street = next((w for w in words[1:] if not w.isdigit() and len(w) > 1), None) if number else words[0]
        if number and not re.search(rf"\b{number}\b", said) and number not in spoken_digits(said):
            return False
        return street is None or re.search(rf"\b{re.escape(street)}\b", said) is not None

    def _stale_reason(self, option: Option) -> str | None:
        """Re-check an offered option against the call as it is now, not as it was when offered."""
        if self.property != "residential":
            return "the property isn't confirmed as a home"
        if self.building_system:
            return "the building supplies their heat or cooling"
        if self.area is None or self.area.county != option.county:
            where = (
                area_name(self.area.county, self.cfg)
                if self.area and self.area.county
                else "no checked address"
            )
            return f"that window is for {area_name(option.county, self.cfg)} and the address is now {where}"
        assert self.assessment
        return self.scheduler.still_fits(option, self.assessment.priority, self.is_member, self.now())

    def _customer_for_booking(
        self, first_name: str, last_name: str, phone: str, address: str, zip5: str, county: str
    ) -> tuple[int, bool]:
        """The customer an appointment belongs to, and whether we just created them.

        An unverified caller gets their own record even on a number we know: attaching
        their visit to that account would show a stranger's booking to the account holder
        and let them move it. The office sees the possible match and merges if it's real."""
        if self.customer:
            return self.customer.id, False
        existing = self.store.customers_by_phone(phone)
        if existing:
            names = ", ".join(f"#{c.id} {c.full_name}" for c in existing)
            self.note(
                f"unverified caller; phone matches existing customer {names}: office to confirm and merge"
            )
        customer_id = self.store.add_customer(
            # A new number is simply a new customer; one that matches an account stays
            # provisional, out of caller ID and lookups, until the office confirms it.
            first_name.strip(),
            last_name.strip(),
            phone,
            address.strip(),
            zip5,
            county,
            confirmed=not existing,
        )
        return customer_id, True

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
            f"been released. Your new confirmation number is {say_confirmation(new_id)}. "
            "Is there anything else I can help with?"
        )
        return (
            f"Moved: appointment #{new_id}. This confirmation is being read to the caller word for word, "
            f'so don\'t repeat it: "{self.announcement}"'
        )

    def cancel_appointment(self, appointment_id: int) -> str:
        self._refuse_if_emergency()
        appointment = self._own_appointment(appointment_id)
        if not self.store.cancel_appointment(appointment_id):
            raise ActionRefused(
                f"Appointment #{appointment_id} was changed by another call a moment ago, so nothing was "
                "cancelled. Call lookup_customer to see their appointments as they are now."
            )
        self.note(f"cancelled appointment #{appointment_id}")
        if self.outcome in (None, "info_only"):
            self.outcome = "cancelled"
        today = self.now().date()
        self.announcement = (
            f"Done. Your {appointment.job_type} {say_day(appointment.day, today)}, {say_window(appointment.window)}, "
            "is cancelled. Is there anything else I can help with?"
        )
        return (
            f"Cancelled: appointment #{appointment_id}. This confirmation is being read to the caller word for "
            f'word, so don\'t repeat it: "{self.announcement}"'
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
            or appointment.day < self.now().date()
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

        # The call's priority decides, not the model's flag: a P1 callback is urgent even if
        # the tool call said urgent=false (an elderly caller with no heat waited until Monday).
        urgent = urgent or self.priority == Priority.P1
        due = self._add_callback(number, reason.strip(), urgent=urgent, name=name)
        self.note(f"{'urgent ' if urgent else ''}callback requested: {reason.strip()[:120]}")
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
        return pricing.answer(item, self.cfg, self.is_member)

    def _spoken_price(self, job_type: str, after_hours: bool) -> str:
        return pricing.confirmation_line(job_type, after_hours, self.cfg, self.is_member)

    def take_announcement(self) -> str | None:
        """Fixed words for the next agent turn, once."""
        text, self.announcement = self.announcement, None
        return text

    def _membership_nudge(self) -> str:
        if self.membership in (Membership.ACTIVE, Membership.LAPSED):
            return ""
        benefits = ", ".join(self.cfg["membership"]["benefits"])
        return (
            f" If you haven't yet, you can mention the {self.cfg['membership']['name']} once "
            f"({benefits}). Don't push it."
        )

    # Record keeping


def _clock(text: str | None) -> time | None:
    """'15:00', '3pm', '3:30 pm' -> a time. None if it can't be read."""
    if not text:
        return None
    match = re.fullmatch(r"\s*(\d{1,2})(?::(\d{2}))?\s*([ap])?\.?\s*m?\.?\s*", text.lower())
    if not match:
        return None
    hour, minute, half = int(match[1]), int(match[2] or 0), match[3]
    if half == "p" and hour < 12:
        hour += 12
    elif half == "a" and hour == 12:
        hour = 0
    if hour > 23 or minute > 59:
        return None
    return time(hour, minute)


def _say_clock(t: time) -> str:
    hour = t.hour % 12 or 12
    suffix = "AM" if t.hour < 12 else "PM"
    if t.hour == 12 and t.minute == 0:
        return "noon"
    return f"{hour}:{t.minute:02d} {suffix}" if t.minute else f"{hour} {suffix}"
