"""Per-call state and the rules every agent tool goes through.

The prompt asks the model to behave; this module makes sure it does. Anything
that costs money or touches safety is checked here, and a refused action raises
ActionRefused with a message telling the model exactly what to fix.
"""

import re
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from summit import config, pricing
from summit.call_triage import TriageMixin, caller_turn_to_screen
from summit.identity import IdentityMixin
from summit.models import ActionRefused, Appointment, Customer, Membership, Priority
from summit.notify import Notifier
from summit.records import RecordsMixin, close_abandoned_calls
from summit.scheduling import AppointmentChanged, Option, Scheduler, say_day, say_window
from summit.service_area import AreaCheck, area_name, check_town, check_zip, property_kind
from summit.speech import normalize_phone, normalize_zip, say_phone, spoken_digits
from summit.store import Store
from summit.triage import Assessment, Facts

_NYC_COUNTIES = {"Kings", "Queens", "Bronx", "New York", "Richmond"}


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
        lines = [self._before_offering()] if reschedule_appointment_id is None else []
        lines = [line for line in lines if line]
        for option in options:
            surcharge = (
                f" (after-hours visit, +${self.cfg['pricing']['after_hours_surcharge']})"
                if option.after_hours
                else ""
            )
            lines.append(f"- {option.option_id}: {option.speakable(today)}{surcharge}")
        notes = [line for line in lines if not line.startswith("- ")]
        windows = [line for line in lines if line.startswith("- ")]
        return (
            "".join(f"{n}\n" for n in notes)
            + "Offer these arrival windows, earliest first. The technician arrives within the window.\n"
            + "\n".join(windows)
            + "\nBook with the option_id the caller picks."
            + self._tech_details_reminder()
        )

    def _before_offering(self) -> str:
        """Once per call: find out whether an unknown caller is already a member, so a member
        calling from a new number isn't charged the diagnostic fee or kept out of member times."""
        if self.customer or self.membership_asked:
            return ""
        self.membership_asked = True
        if self.caller_match:
            return (
                f"FIRST: the greeting asked if this is {self.caller_match.first_name}. Report their answer with "
                "lookup_customer(confirmed_name=...) before offering times."
            )
        if self.lookup_attempts:
            return ""
        club = self.cfg["membership"]["name"]
        return (
            f"FIRST, before offering times: ask once whether they're already a {club} member or have had "
            "us out before. If yes, verify them (lookup_customer) and call find_appointment_options again: "
            "members get priority windows and no diagnostic fee. If not, offer these."
        )

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
        if address and address.strip() and not re.search(r"\d", address):
            problems.append("the street address needs a house number")
        elif not address_read_back_confirmed or not self._read_back_address(address):
            problems.append("read the full address back and get a yes")
        if problems:
            raise ActionRefused("Not booked yet: " + "; ".join(problems) + ".")

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
            "been released. Is there anything else I can help with?"
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
