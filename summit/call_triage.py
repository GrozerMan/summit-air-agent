"""Triage on the live call: the hazard screen on the caller's words, the P0 safety
path, and priority changes as facts come in.

A mixin for CallSession; see summit/triage.py for the rules themselves.
"""

import re
from collections.abc import Iterable

from summit import config
from summit.hazard_words import cannot_leave, hazard_in, leaving
from summit.models import ActionRefused, Priority
from summit.service_area import area_name, check_zip, place_in, property_kind
from summit.triage import EMERGENCY, Assessment, Facts, assess, cannot_leave_script, safety_script

# A P0 that only the word list raised can be a false alarm ("I asked if it smells like
# gas and she said no"). It stays P0: undoing an emergency is the riskier mistake. The
# caller who wanted a visit gets a person to arrange it instead of a dead end.
_WORDS_ONLY_CALLBACK = (
    "If the caller says there's no hazard at all and they still want a visit, don't argue and don't "
    "book: offer a callback from the office to arrange it (request_callback)."
)


def _squash(text: str) -> str:
    return " ".join("".join(ch for ch in text.lower() if ch.isalnum() or ch.isspace()).split())


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


class TriageMixin:
    def assess_situation(self, facts: Facts) -> str:
        if self.area_from_file and facts.description and property_kind(facts.description) == "commercial":
            # "The AC at my restaurant": not the home on the account, so check the address again.
            self.area, self.property, self.area_from_file = None, "unknown", False
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
                a.id
                for a in self.store.upcoming_appointments(self.customer.id, self.now().date())
                if a.id not in held
            ]
            if others:
                alert += f". Customer also has upcoming appointment {', '.join(f'#{a}' for a in others)}"
        self.notifier.alert(self.call_id, "critical", alert)
        self.outcome = "safety_emergency"
        # Times offered before the hazard came up are void.
        self._void_offers()
        return (
            f"SAFETY EMERGENCY ({what}). The dispatcher has been alerted. The safety script is being read to "
            f'the caller word for word right now, so don\'t repeat it: "{script}" '
            "Then stop. Don't collect booking details, and if they want to hang up and leave, let them."
        )

    def safety_script(self) -> str:
        """The script for this P0 call, fixed the first time it's worked out, so a county
        learned later doesn't make it count as "not read yet" and get read twice."""
        assert self.assessment and self.assessment.priority == Priority.P0
        if self.p0_script is None:
            # Where they say they are beats where caller ID says they live: the call may be
            # from a rental, a parent's house or a cell phone.
            checked = self.area.county if self.area and not self.area_from_file else None
            county = (
                checked
                or self.hazard_place.get("county")
                or (self.area and self.area.county)
                or (self.caller_match and self.caller_match.county)
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
        """Where the caller is, from the turn that reported the hazard: a ZIP or one of
        our places, from the hazard's own sentence if it has one, else the rest of the turn."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        # The hazard's sentence takes any place; another sentence only one the caller is at
        # ("I smell gas. I'm in Yonkers." but not "My sister lives in Yonkers. I smell gas.").
        ordered = [(s, False) for s in sentences if hazard_in(s)] + [
            (s, True) for s in sentences if not hazard_in(s)
        ]
        for sentence, only_mine in ordered:
            place: dict[str, str] = {}
            named = place_in(sentence, self.cfg, only_mine=only_mine)
            if named:
                place["town"] = named[0]
                if named[1]:
                    place["county"] = named[1]
            # "10701" or "1 0 7 0 1"
            zip_match = re.search(r"(?<!\d)\d(?:[\s-]?\d){4}(?![\s-]?\d)", sentence)
            if zip_match and (not only_mine or named):
                zip_code = re.sub(r"\D", "", zip_match[0])
                place["zip"] = zip_code
                check = check_zip(zip_code, self.cfg)
                if check.in_area and check.county:
                    # A ZIP is more precise than a town name.
                    place["county"] = check.county
            if place:
                return place
        return {}

    # The caller's own words

    def unsaid_safety_script(self, said_so_far: str) -> str | None:
        """The safety script, if the call is P0 and it hasn't been spoken yet. Checked before every
        reply: after a caller's turn (the word screen) and after a tool call (a hazard only the
        model reported), so the script is always fixed text, never the model's rewording."""
        if self.priority != Priority.P0:
            return None
        script = self.safety_script()
        return None if _squash(script) in _squash(said_so_far) else script

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

        script = self.unsaid_safety_script(said_so_far)
        if script:
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

    def _refuse_if_emergency(self) -> None:
        if self.priority == Priority.P0:
            message = (
                "This is a safety emergency. Don't book or move anything on this call; the caller "
                "should be leaving the house."
            )
            if self.hazard_from_words_only:
                message += " " + _WORDS_ONLY_CALLBACK
            raise ActionRefused(message)
