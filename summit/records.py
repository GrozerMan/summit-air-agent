"""The call record: what the office sees on the dashboard and the technician gets
on the ticket, what happens at hang-up, and recovery when hang-up never came.

A mixin for CallSession.
"""

from datetime import datetime, timedelta
from typing import Any

from summit import config
from summit.claims import false_claims
from summit.models import Membership, Priority
from summit.notify import Notifier
from summit.service_area import area_name
from summit.speech import say_phone
from summit.store import Store

# Which outcome a call with several requests shows, most telling first.
_OUTCOME_RANK = [
    "safety_emergency", "booked", "rescheduled", "cancelled", "callback", "transferred",
    "commercial_lead", "building_system", "out_of_area", "info_only", "abandoned",
]  # fmt: skip


class RecordsMixin:
    @property
    def call_priority(self) -> Priority | None:
        """The most serious priority of any request on the call."""
        found = [Priority(r["priority"]) for r in self.earlier_requests if r["priority"] is not None]
        if self.priority is not None:
            found.append(self.priority)
        return min(found) if found else None

    @property
    def call_outcome(self) -> str | None:
        found = [r["outcome"] for r in self.earlier_requests if r["outcome"]]
        if self.outcome:
            found.append(self.outcome)
        if not found:
            return None
        return min(found, key=lambda o: _OUTCOME_RANK.index(o) if o in _OUTCOME_RANK else len(_OUTCOME_RANK))

    def call_summary(self) -> str:
        """The dashboard's summary: earlier requests on the call, then the current one."""
        earlier = [
            f"Request {n}: P{r['priority']} {', '.join(r['reasons'])}, "
            + (
                f"appointment {', '.join(f'#{a}' for a in r['appointments'])}"
                if r["appointments"]
                else (r["outcome"] or "").replace("_", " ")
            )
            + "."
            for n, r in enumerate(self.earlier_requests, start=1)
            if r["priority"] is not None
        ]
        now = self.technician_summary()
        if earlier:
            now = f"Request {len(self.earlier_requests) + 1}: {now}"
        return " ".join([*earlier, now]).strip()

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
            last_seen=self.now(),
            priority=self.call_priority,
            outcome=self.call_outcome,
            summary=self.call_summary(),
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
            # Nothing booked or called back for this request (a call can carry several).
            and len(self.booked) == self._request_booked_from
            and len(self.callbacks) == self._request_callbacks_from
            # A callback already made for this call (by the dropped-call recovery) is enough.
            and len(self.store.callbacks_for_call(self.call_id)) <= len(self.callbacks)
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

    def has_booking(self) -> bool:
        """Something the agent may truthfully call booked: a visit booked or moved on this call,
        or (unless today's call is about a new problem) the customer's existing appointment,
        which backs "you're scheduled for Thursday"."""
        new_problem = self.priority in (Priority.P1, Priority.P2)
        return bool(self.booked) or bool(
            self.customer
            and not new_problem
            and self.store.upcoming_appointments(self.customer.id, self.now().date())
        )

    def _flag_false_claims(self, transcript: list[dict[str, Any]]) -> None:
        """The agent said it booked something, or that someone will call, and the records
        say otherwise. The caller is now expecting a technician or a call that isn't coming,
        so the office has to hear about it."""
        said = " ".join(t.get("text", "") for t in transcript if t.get("role") == "assistant")
        self.false_claims = false_claims(
            said, has_booking=self.has_booking(), has_callback=bool(self.callbacks)
        )
        if not self.false_claims:
            return
        self.note("REVIEW: " + "; ".join(self.false_claims))
        self.notifier.alert(
            self.call_id,
            "urgent",
            f"Agent told {self._who()} something the records don't show: {self.false_claims[0]}. Call them back.",
        )
        if self.callback_phone and not self.callbacks:
            self._add_callback(
                self.callback_phone, "Agent wrongly told the caller it was booked or arranged", urgent=True
            )

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
            status = "member" if self.is_member else (self.membership or Membership.NONE).value
            parts.append(f"Customer: {self.customer.full_name} ({status}, verified).")
        elif self.caller_id:
            parts.append(f"Caller {say_phone(self.caller_id)} (not verified).")
        if self.notes:
            parts.append("Notes: " + "; ".join(self.notes) + ".")
        if not parts and self.outcome:
            parts.append(f"Outcome: {self.outcome.replace('_', ' ')}.")
        return " ".join(parts)

    def _technician_notes(
        self, caller_notes: str, equipment: str | None = None, access_notes: str | None = None
    ) -> str:
        parts = [self.technician_summary()]
        if equipment and equipment.strip():
            parts.append(f"Equipment: {equipment.strip()}.")
        if access_notes and access_notes.strip():
            parts.append(f"Access: {access_notes.strip()}.")
        parts.append(caller_notes.strip())
        return " ".join(p for p in parts if p)

    def record(self) -> dict[str, Any]:
        return {
            "caller_id": self.caller_id,
            "verified_customer_id": self.customer.id if self.customer else None,
            "facts": self.facts.known(),
            "priority": int(self.call_priority) if self.call_priority is not None else None,
            "reasons": self.assessment.reasons if self.assessment else [],
            "service_area": {"county": self.area.county, "zip": self.area.zip} if self.area else None,
            "property": self.property,
            "offered": sorted(self.offered),
            "appointments": self.booked,
            "callbacks": self.callbacks,
            "notes": self.notes,
            "false_claims": self.false_claims,
            "outcome": self.call_outcome,
            "requests": self.earlier_requests,
            "caller_availability": self.caller_availability,
            "metrics": self.metrics,
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


def close_abandoned_calls(store: Store, cfg: dict[str, Any], now: datetime, silent_minutes: int = 10) -> int:
    """Close calls whose worker died before hang-up (a crash, a deploy, a killed process).

    Their hang-up handler never ran, so nothing followed them up: a triaged caller who
    wasn't booked gets the callback finalize() would have made. Runs as each new call starts.
    """
    closed = 0
    notifier = Notifier(store)
    for row in store.open_calls_silent_since(now - timedelta(minutes=silent_minutes)):
        record = row["record"]
        priority = record.get("priority")
        outcome = record.get("outcome") or row.get("outcome")
        phone = row.get("caller_id")
        triaged_unbooked = (
            priority in (1, 2) and not record.get("appointments") and not record.get("callbacks")
        )
        if triaged_unbooked and phone:
            urgent = priority == 1
            due = (
                now + timedelta(minutes=cfg["escalation"]["urgent_callback_minutes"])
                if urgent
                else config.next_office_opening(
                    cfg, now + timedelta(hours=cfg["escalation"]["callback_hours"])
                )
            )
            store.add_callback(
                row["id"], phone, "Call dropped before booking (agent restarted)", due, urgent=urgent
            )
            notifier.alert(
                row["id"],
                "urgent",
                f"Call from {say_phone(phone)} dropped mid-call at P{priority}; callback set",
            )
            outcome = "callback"
        store.close_call(row["id"], outcome or "abandoned", now)
        closed += 1
    return closed
