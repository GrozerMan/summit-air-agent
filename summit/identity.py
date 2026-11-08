"""Who's calling: caller ID as a hint, never as proof.

A mixin for CallSession: it reads and writes the call's state (customer, caller_match,
denied, lookup_attempts, area). Split out of backend.py to keep each rule set readable.
"""

from summit.models import ActionRefused, Customer, Membership
from summit.scheduling import say_day, say_window
from summit.service_area import area_name, check_zip
from summit.speech import normalize_phone, normalize_zip


class IdentityMixin:
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
        if confirmed_name is None and self.caller_match:
            # The greeting asked "Am I speaking with Dana?". Without the answer, the son who
            # never says "no" would verify as his mother from her own phone with her ZIP.
            raise ActionRefused(
                f"The greeting asked if this is {self.caller_match.first_name}. Call lookup_customer with "
                "confirmed_name set to their answer (true or false) first."
            )
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
            if not number:
                raise ActionRefused(
                    "To look up an account, ask for the phone number on the account, their last name "
                    "and their ZIP code."
                )
            if number != self.caller_id and not (last_name and zip_code):
                # Calling from a different number: knowing a phone number and a surname is
                # easy for a stranger, so all three.
                raise ActionRefused(
                    "They're calling from a different number than the one on the account, so ask for "
                    "their last name and ZIP code as well as the account's phone number."
                )
            if not (last_name or zip_code):
                raise ActionRefused("Ask for their last name or ZIP code to confirm the account.")

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
            # An assumption from the account, not something said on this call: a place the
            # caller names (a gas smell at their rental, the AC at their restaurant) overrides it.
            self.area_from_file = True
        return "Verified. " + self._account_summary()

    def _account_summary(self) -> str:
        c = self.customer
        assert c is not None
        lines = [f"{c.full_name}, {c.address}, ZIP {c.zip} ({area_name(c.county, self.cfg)})."]
        if self.membership == Membership.ACTIVE:
            lines.append(f"Active {self.cfg['membership']['name']} member: thank them for being a member.")
        elif self.membership == Membership.LAPSED:
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
