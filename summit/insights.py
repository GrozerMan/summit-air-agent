"""What the agent did for the business, in the owner's terms.

Three views over the calls the agent has already recorded, for the dashboard and the
morning brief:

- results():       calls answered (and how many the office would have missed), jobs booked,
                   estimated revenue, emergencies handled, speed, cost per call.
- opportunities(): sales follow-ups the calls surfaced: old systems worth a replacement
                   estimate, lapsed members, commercial leads, callers who didn't book.
- brief():         a one-page morning report: since the office closed, today's jobs, what
                   to call back.

Read-only over the store, plain functions, no model involved. Money figures are
estimates from `[insights]` in config/business.toml and are always labelled that way.
"""

import re
from datetime import date, datetime, time, timedelta
from statistics import median
from typing import Any

from summit import config
from summit.models import Membership
from summit.store import Store

SAMPLE_PREFIX = "sample-"

# What counts as a job's kind, from the job_type the agent booked it as.
_TUNE_UP = re.compile(r"tune|maintenance|check[- ]?up|inspection|cleaning", re.I)
_ESTIMATE = re.compile(r"estimate|replace|quote|new system|install", re.I)

# "20 years old", "20-year-old", "about 20 yrs old"
_AGE = re.compile(r"\b(\d{1,2})[\s-]*(?:years?|yrs?)[\s-]*old\b", re.I)
# "from 2004", "installed in 2004", "put in in 2004", "since 2004", "a 2004 Carrier"
_YEAR = re.compile(r"\b(?:from|installed(?: in)?|put in(?: in)?|since|a|an)\s+(19[5-9]\d|20[0-4]\d)\b", re.I)
_REPLACEMENT_ASK = re.compile(r"\breplac|\bnew (?:system|unit|furnace|boiler|ac\b)|\bestimate", re.I)

_OUTCOME_LABELS = {
    "booked": "Booked",
    "rescheduled": "Moved",
    "cancelled": "Cancelled",
    "callback": "Callback set",
    "safety_emergency": "Safety emergency",
    "out_of_area": "Outside our area",
    "commercial_lead": "Commercial lead",
    "building_system": "Building's heat (landlord)",
    "info_only": "Question answered",
    "abandoned": "Hung up",
    None: "In progress",
}


def outcome_label(outcome: str | None) -> str:
    if outcome in _OUTCOME_LABELS:
        return _OUTCOME_LABELS[outcome]
    return str(outcome).replace("_", " ").capitalize()


def job_kind(job_type: str | None) -> str:
    text = job_type or ""
    if _TUNE_UP.search(text):
        return "tune_up"
    if _ESTIMATE.search(text):
        return "estimate"
    return "repair"


def job_value(job_type: str | None, cfg: dict[str, Any]) -> int:
    """Estimated revenue of a booked visit. An estimate visit earns nothing itself."""
    values = cfg["insights"]
    return {"repair": values["repair_visit_value"], "tune_up": values["tune_up_value"]}.get(
        job_kind(job_type), 0
    )


def equipment_age(text: str, this_year: int) -> int | None:
    """How old the caller said their system is, if they did."""
    if match := _AGE.search(text):
        return int(match[1])
    if match := _YEAR.search(text):
        year = int(match[1])
        if year <= this_year:
            return this_year - year
    return None


def is_sample(call_id: str | None) -> bool:
    return bool(call_id and call_id.startswith(SAMPLE_PREFIX))


def _local(iso: str, cfg: dict[str, Any]) -> datetime:
    return datetime.fromisoformat(iso).astimezone(config.timezone(cfg))


def after_hours(started_at: str, cfg: dict[str, Any]) -> bool:
    """Started while the office was closed: evenings, Sundays, holidays."""
    return not config.office_open(cfg, _local(started_at, cfg))


def period_start(now: datetime, days: int) -> datetime | None:
    """1: since midnight today. N: the last N days. 0: everything."""
    if days <= 0:
        return None
    if days == 1:
        return datetime.combine(now.date(), time(0), tzinfo=now.tzinfo)
    return now - timedelta(days=days)


# Results


def results(store: Store, cfg: dict[str, Any], now: datetime, days: int = 7) -> dict[str, Any]:
    start = period_start(now, days)
    calls = store.calls_since(start)
    by_call = _jobs_by_call(store)
    values = cfg["insights"]

    outcomes: dict[str, int] = {}
    jobs: list[dict[str, Any]] = []
    after_hours_calls = after_hours_jobs = 0
    minutes: list[float] = []
    latencies: list[float] = []
    members = emergencies = urgent = false_claims = 0
    revenue = revenue_after_hours = 0

    for call in calls:
        label = outcome_label(call["outcome"])
        outcomes[label] = outcomes.get(label, 0) + 1
        late = after_hours(call["started_at"], cfg)
        after_hours_calls += late
        record = call["record"]
        if call["priority"] == 0:
            emergencies += 1
        elif call["priority"] == 1:
            urgent += 1
        false_claims += bool(record.get("false_claims"))
        if call["ended_at"]:
            length = datetime.fromisoformat(call["ended_at"]) - datetime.fromisoformat(call["started_at"])
            minutes.append(max(length.total_seconds(), 0) / 60)
        if (p50 := (record.get("metrics") or {}).get("latency_p50_s")) is not None:
            latencies.append(p50)
        if _active_member(store, record, _local(call["started_at"], cfg).date()):
            members += 1
        if call["outcome"] != "booked":
            continue  # a moved visit isn't new work
        for job in by_call.get(call["id"], []):
            value = job_value(job["job_type"], cfg)
            jobs.append({**job, "value": value, "after_hours": late})
            revenue += value
            if late:
                after_hours_jobs += 1
                revenue_after_hours += value

    kinds = {"repair": 0, "tune_up": 0, "estimate": 0}
    for job in jobs:
        kinds[job_kind(job["job_type"])] += 1
    replacement = [o for o in opportunities(store, cfg, now, include_done=True, calls=calls)
                   if o["kind"] == "replacement"]  # fmt: skip
    avg_minutes = sum(minutes) / len(minutes) if minutes else None
    return {
        "days": days,
        "calls": len(calls),
        "after_hours_calls": after_hours_calls,
        "outcomes": dict(sorted(outcomes.items(), key=lambda kv: -kv[1])),
        "jobs_booked": len(jobs),
        "jobs_after_hours": after_hours_jobs,
        "jobs_by_kind": kinds,
        "revenue_estimate": revenue,
        "revenue_after_hours": revenue_after_hours,
        "replacement_leads": len(replacement),
        "pipeline_estimate": len(replacement) * values["replacement_value"],
        "emergencies": emergencies,
        "urgent": urgent,
        "members_recognized": members,
        "false_claims": false_claims,
        "booking_rate": round(len(jobs) / len(calls), 2) if calls else None,
        "latency_p50_s": round(median(latencies), 2) if latencies else None,
        "avg_minutes": round(avg_minutes, 1) if avg_minutes is not None else None,
        "agent_cost_per_call": round(avg_minutes * values["agent_cost_per_minute"], 2)
        if avg_minutes is not None
        else None,
        "answering_service_per_call": round(avg_minutes * values["answering_service_per_minute"], 2)
        if avg_minutes is not None
        else None,
        "sample": any(is_sample(c["id"]) for c in calls),
        "assumptions": {
            "repair_visit_value": values["repair_visit_value"],
            "tune_up_value": values["tune_up_value"],
            "replacement_value": values["replacement_value"],
            "agent_cost_per_minute": values["agent_cost_per_minute"],
            "answering_service_per_minute": values["answering_service_per_minute"],
        },
    }


def _jobs_by_call(store: Store) -> dict[str, list[dict[str, Any]]]:
    jobs: dict[str, list[dict[str, Any]]] = {}
    for appt in store.appointments_from_calls():
        if appt["status"] != "cancelled":
            jobs.setdefault(appt["call_id"], []).append(appt)
    return jobs


def _active_member(store: Store, record: dict[str, Any], day: date) -> bool:
    customer = _customer(store, record)
    return bool(customer and customer.membership_on(day) == Membership.ACTIVE)


def _customer(store: Store, record: dict[str, Any]):
    customer_id = record.get("verified_customer_id")
    return store.get_customer(customer_id) if customer_id else None


# Follow-ups


def opportunities(
    store: Store,
    cfg: dict[str, Any],
    now: datetime,
    include_done: bool = False,
    calls: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Sales follow-ups from finished calls, most valuable first."""
    calls = store.calls_since(None) if calls is None else calls
    by_call: dict[str, list[dict[str, Any]]] = {}
    for appt in store.appointments_from_calls():
        by_call.setdefault(appt["call_id"], []).append(appt)
    done = store.followups_done()
    values = cfg["insights"]
    diagnostic = cfg["pricing"]["diagnostic"]

    found: list[dict[str, Any]] = []
    for call in calls:
        if not call["ended_at"] or call["priority"] == 0:
            continue  # still talking, or a safety call: not a sales conversation
        record = call["record"]
        day = _local(call["started_at"], cfg).date()
        customer = _customer(store, record)
        appts = [a for a in by_call.get(call["id"], []) if a["status"] != "cancelled"]
        booked = bool(appts) and call["outcome"] in ("booked", "rescheduled")
        phone = (customer.phone if customer else None) or _callback_phone(store, call) or call["caller_id"]
        who = (
            customer.full_name
            if customer
            else (appts[0]["contact_name"] if appts else _callback_name(store, call)) or "New caller"
        )

        def add(kind: str, label: str, why: str, action: str, value: int | None) -> None:
            key = f"{call['id']}:{kind}"
            found.append({
                "key": key, "kind": kind, "label": label, "who": who, "phone": phone,
                "why": why, "action": action, "value": value, "call_id": call["id"],
                "at": call["started_at"], "done": key in done,
            })  # fmt: skip

        # An old system, or a caller asking about replacing it.
        text = " ".join(_call_texts(record, appts))
        age = equipment_age(text, day.year)
        if age is not None and age >= values["replacement_age_years"]:
            what = _equipment(record, appts) or "System"
            add(
                "replacement",
                "Replacement estimate",
                f"{what}." if _AGE.search(what) else f"{what} (about {age} years old).",
                "Have the tech offer a free replacement estimate on the visit."
                if booked
                else "Call to offer a free replacement estimate.",
                values["replacement_value"],
            )
        elif _REPLACEMENT_ASK.search(" ".join([record.get("facts", {}).get("request_type") or "",
                                               *(a["job_type"] for a in appts)])):  # fmt: skip
            add(
                "replacement",
                "Replacement estimate",
                "Asked about replacing their system.",
                "Make sure the estimate visit happens; follow up within a day of it.",
                values["replacement_value"],
            )

        if customer and customer.membership_on(day) == Membership.LAPSED:
            add(
                "renewal",
                "Membership renewal",
                "Lapsed Comfort Club member called"
                + (f" (lapsed {customer.membership_expires:%b %Y})." if customer.membership_expires else "."),
                "Offer to renew: no diagnostic fee, two tune-ups a year, priority scheduling.",
                None,
            )
        elif (
            booked
            and call["outcome"] == "booked"
            and not (customer and customer.membership_on(day) == Membership.ACTIVE)
        ):
            repairs = [a for a in appts if job_kind(a["job_type"]) == "repair"]
            if repairs:
                add(
                    "membership",
                    "Membership pitch",
                    f"Paying the ${diagnostic} diagnostic fee; a Comfort Club member pays $0.",
                    "Offer the Comfort Club after the visit.",
                    None,
                )

        if call["outcome"] == "commercial_lead":
            add(
                "commercial",
                "Commercial lead",
                _what_they_said(record) or "A business or building owner called.",
                "Call back: refer it on or quote it if you take commercial work.",
                None,
            )
        elif not booked and call["outcome"] in ("callback", "abandoned", "info_only") and phone:
            if call["priority"] is not None or record.get("facts", {}).get("request_type"):
                add(
                    "unbooked",
                    "Didn't book",
                    _what_they_said(record) or "Called but didn't book.",
                    "Call back and offer the next opening.",
                    job_value(record.get("facts", {}).get("request_type") or "repair", cfg),
                )

    if not include_done:
        found = [o for o in found if not o["done"]]
    found.sort(key=lambda o: (o["done"], -(o["value"] or 0), _neg_time(o["at"])))
    return found


def outside_demand(store: Store, cfg: dict[str, Any], now: datetime, days: int = 30) -> list[dict[str, Any]]:
    """Where out-of-area callers were: a signal for where to grow, not a call list."""
    counts: dict[str, int] = {}
    for call in store.calls_since(period_start(now, days)):
        if call["outcome"] != "out_of_area":
            continue
        place = _asked_place(call["record"])
        counts[place] = counts.get(place, 0) + 1
    return [{"place": p, "calls": n} for p, n in sorted(counts.items(), key=lambda kv: -kv[1])]


def _neg_time(iso: str) -> float:
    return -datetime.fromisoformat(iso).timestamp()


def _tool_args(record: dict[str, Any], tool: str) -> list[dict[str, Any]]:
    return [t.get("args") or {} for t in record.get("tools", []) if t.get("tool") == tool]


def _equipment(record: dict[str, Any], appts: list[dict[str, Any]]) -> str | None:
    for args in reversed(_tool_args(record, "book_appointment")):
        if (args.get("equipment") or "").strip():
            return args["equipment"].strip().rstrip(".").capitalize()
    for appt in appts:
        if found := parse_notes(appt["notes"]).get("equipment"):
            return found.capitalize()
    return None


def _call_texts(record: dict[str, Any], appts: list[dict[str, Any]]) -> list[str]:
    texts = [record.get("facts", {}).get("description") or "", *record.get("notes", [])]
    texts += [args.get("equipment") or "" for args in _tool_args(record, "book_appointment")]
    texts += [a["notes"] for a in appts]
    return texts


def _what_they_said(record: dict[str, Any]) -> str:
    description = (record.get("facts", {}).get("description") or "").strip()
    if description:
        return f'"{description[:140]}"'
    reasons = record.get("reasons") or []
    return (", ".join(reasons).capitalize() + ".") if reasons else ""


def _asked_place(record: dict[str, Any]) -> str:
    for args in reversed(_tool_args(record, "check_service_address")):
        if args.get("town"):
            return str(args["town"]).strip().title()
        if args.get("zip_code"):
            return f"ZIP {args['zip_code']}"
    return "Unknown"


def _callback_phone(store: Store, call: dict[str, Any]) -> str | None:
    callbacks = store.callbacks_for_call(call["id"])
    return callbacks[0]["phone"] if callbacks else None


def _callback_name(store: Store, call: dict[str, Any]) -> str | None:
    callbacks = store.callbacks_for_call(call["id"])
    return callbacks[0]["name"] if callbacks else None


_NOTE_FIELDS = re.compile(r"\b(Equipment|Access): (.+?)\.(?=\s+[A-Z]|\s*$)")


def parse_notes(notes: str) -> dict[str, str]:
    """Pull 'Equipment: ...' and 'Access: ...' out of an appointment's technician notes."""
    return {m[1].lower(): m[2].strip() for m in _NOTE_FIELDS.finditer(notes or "")}


# Morning brief


def last_close(cfg: dict[str, Any], now: datetime) -> datetime:
    """When the office last closed before `now`."""
    for offset in range(8):
        day = (now - timedelta(days=offset)).date()
        hours = config.office_hours(cfg, day)
        if hours is None:
            continue
        closed = datetime.combine(day, hours[1], tzinfo=now.tzinfo)
        if closed <= now:
            return closed
    return now - timedelta(days=1)


def brief(store: Store, cfg: dict[str, Any], now: datetime) -> dict[str, Any]:
    since = last_close(cfg, now)
    calls = store.calls_since(since)
    end_of_day = datetime.combine(now.date(), time(23, 59), tzinfo=now.tzinfo)
    jobs = []
    for appt in store.appointments_on(now.date()):
        jobs.append({**appt, **parse_notes(appt["notes"]), "area": _area(appt["county"], cfg)})
    callbacks = [c for c in store.open_callbacks() if datetime.fromisoformat(c["due_at"]) <= end_of_day]
    return {
        "date": now.date().isoformat(),
        "since": since.isoformat(),
        "overnight": {
            "calls": len(calls),
            "booked": sum(c["outcome"] == "booked" for c in calls),
            "emergencies": sum(c["priority"] == 0 for c in calls),
            "callbacks": sum(c["outcome"] == "callback" for c in calls),
            "list": [
                {
                    "id": c["id"],
                    "at": c["started_at"],
                    "priority": c["priority"],
                    "outcome": outcome_label(c["outcome"]),
                    "caller": c["caller_id"],
                    "summary": c["summary"] or "",
                }
                for c in reversed(calls)
            ],
        },
        "alerts": store.unacknowledged_alerts(),
        "jobs": jobs,
        "callbacks": callbacks,
        "followups": opportunities(store, cfg, now)[:5],
        "sample": any(is_sample(c["id"]) for c in calls),
    }


def display_phone(number: str | None) -> str:
    if number and (m := re.fullmatch(r"\+1(\d{3})(\d{3})(\d{4})", number)):
        return f"({m[1]}) {m[2]}-{m[3]}"
    return number or "no number"


def _area(county: str, cfg: dict[str, Any]) -> str:
    return cfg["service_area"].get("names", {}).get(county, county)


def brief_text(b: dict[str, Any], cfg: dict[str, Any]) -> str:
    """The brief as plain text, for the terminal or a Slack message."""
    tz = config.timezone(cfg)
    since = datetime.fromisoformat(b["since"]).astimezone(tz)
    o = b["overnight"]
    lines = [
        f"Summit Air morning brief, {date.fromisoformat(b['date']):%A %b %-d}",
        "",
        f"Since the office closed ({since:%a %-I:%M %p}): {o['calls']} calls, {o['booked']} booked, "
        f"{o['emergencies']} safety emergencies, {o['callbacks']} callbacks set.",
    ]
    for c in o["list"]:
        at = datetime.fromisoformat(c["at"]).astimezone(tz)
        p = f"P{c['priority']} " if c["priority"] is not None else ""
        lines.append(f"  {at:%-I:%M %p}  {p}{c['outcome']}: {c['summary'][:110]}")
    if b["alerts"]:
        lines += ["", f"Alerts not yet acknowledged: {len(b['alerts'])}"]
        lines += [f"  [{a['severity']}] {a['summary'][:120]}" for a in b["alerts"][:5]]
    lines += ["", f"Today's jobs: {len(b['jobs'])}"]
    for j in b["jobs"]:
        extra = "; ".join(x for x in (j.get("equipment"), j.get("access")) if x)
        lines.append(
            f"  {j['arrival_window']}  {j['area']}  P{j['priority']} {j['job_type']}, {j['contact_name']}, "
            f"{j['service_address']}" + (f"  ({extra})" if extra else "")
        )
    lines += ["", f"Callbacks due today: {len(b['callbacks'])}"]
    lines += [
        f"  {'URGENT ' if c['urgent'] else ''}{display_phone(c['phone'])}: {c['reason'][:100]}"
        for c in b["callbacks"]
    ]
    if b["followups"]:
        lines += ["", "Top follow-ups:"]
        lines += [f"  {f['label']}: {f['who']}, {f['why']}" for f in b["followups"]]
    if b["sample"]:
        lines += ["", "(Includes sample data.)"]
    return "\n".join(lines)
