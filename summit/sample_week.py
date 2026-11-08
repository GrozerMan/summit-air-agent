"""A plausible past week of calls, for showing the owner's views on a fresh database.

    uv run python -m summit.seed --reset --sample-week

Every row it writes is marked: call ids start with "sample-" and records carry
"sample": true, so the dashboard and the brief say "includes sample data". Real calls
land alongside. Its future jobs use the regular pool only, so they can't take the
emergency reserve a live demo call might need.
"""

from datetime import datetime, time, timedelta
from typing import Any

from summit.insights import SAMPLE_PREFIX, outcome_label
from summit.models import Pool, Priority
from summit.store import Store

# (days ago, "HH:MM", minutes long, priority, outcome, who, what they said, extra)
_CALLS: list[dict[str, Any]] = [
    dict(ago=2, at="21:40", mins=4.1, p=1, outcome="booked", caller="+17185550134",
         new=("Maria", "Lopez", "71-14 Austin Street, Forest Hills", "11375", "Queens"),
         said="no heat since this afternoon, it's 54 in the house",
         reasons=["no heat during heating season"], temp=54,
         job=dict(type="no heat", in_days=1, window="08:00-10:00", pool=Pool.REGULAR,
                  equipment="gas furnace, about 22 years old", access="side door, dog in the yard")),
    dict(ago=1, at="21:30", mins=3.6, p=1, outcome="booked", existing="+19145550188",
         said="the boiler stopped, my mother is 84 and she's freezing",
         reasons=["no heat during heating season", "vulnerable occupant"], vulnerable=True,
         job=dict(type="no heat", in_days=1, window="08:00-10:00", pool=Pool.REGULAR,
                  equipment="oil boiler, installed in 2009", access="ring twice, mother hard of hearing")),
    dict(ago=0, at="05:50", mins=3.2, p=2, outcome="booked", existing="+16315550177",
         said="the furnace is making a loud banging noise when it starts",
         reasons=["equipment working but noisy"],
         job=dict(type="furnace noise", in_days=0, window="12:00-14:00", pool=Pool.REGULAR,
                  equipment="gas furnace, 8 years old", access="park in the driveway")),
    dict(ago=3, at="10:20", mins=2.4, p=3, outcome="booked", existing="member",
         said="I'd like my fall tune-up", reasons=["tune-up"], request="tune-up",
         job=dict(type="tune-up", in_days=-1, window="10:00-12:00", pool=Pool.MEMBER,
                  equipment="central AC and gas furnace")),
    dict(ago=5, at="08:15", mins=3.0, p=2, outcome="booked", caller="+19145550166",
         new=("James", "Carter", "22 Birch Road, Scarsdale", "10583", "Westchester"),
         said="the thermostat is blank and the heat won't come on", reasons=["no heat, house still warm"],
         job=dict(type="no heat", in_days=-4, window="10:00-12:00", pool=Pool.REGULAR,
                  equipment="Carrier heat pump, 6 years old")),
    dict(ago=6, at="20:05", mins=2.8, p=3, outcome="booked", caller="+15165550121",
         new=("Linda", "Park", "9 Shore Drive, Great Neck", "11021", "Nassau"),
         said="we're thinking about replacing our old AC", reasons=["replacement estimate"],
         request="replacement estimate",
         job=dict(type="replacement estimate", in_days=-4, window="14:00-16:00", pool=Pool.REGULAR)),
    dict(ago=4, at="23:05", mins=1.6, p=0, outcome="safety_emergency", caller="+17185550190",
         said="I smell gas in the basement near the furnace", reasons=["gas smell"],
         alert=("critical", "SAFETY: gas smell reported in Brooklyn. Caller told to leave and call 911 "
                "and National Grid. Their words: \"I smell gas in the basement near the furnace\"")),
    dict(ago=1, at="19:45", mins=1.9, p=None, outcome="info_only", caller="+17185550123",
         said="how much is a tune-up", request="tune-up"),
    dict(ago=3, at="18:50", mins=2.2, p=2, outcome="callback", caller="+19175550111",
         said="the heat pump is running but not keeping up", reasons=["heating weak"],
         callback=("Call ended before booking", False)),
    dict(ago=5, at="13:00", mins=2.0, p=None, outcome="commercial_lead", caller="+17185550177",
         said="I run a restaurant on Steinway Street, the rooftop unit is down",
         callback=("commercial lead: restaurant rooftop unit, Astoria", False)),
    dict(ago=1, at="22:15", mins=1.8, p=None, outcome="building_system", caller="+17185550145",
         said="no heat in my apartment, the building has a boiler"),
    dict(ago=2, at="20:30", mins=1.1, p=None, outcome="out_of_area", caller="+12015550110",
         said="AC repair", town="Jersey City"),
    dict(ago=6, at="11:00", mins=1.0, p=None, outcome="out_of_area", caller="+12015550188",
         said="heat not working", zip="07030"),
    dict(ago=3, at="15:00", mins=1.2, p=None, outcome="out_of_area", caller="+12035550141",
         said="furnace tune-up", town="Stamford"),
]  # fmt: skip


def add_sample_week(store: Store, cfg: dict[str, Any], now: datetime) -> int:
    tz = now.tzinfo
    member = store.customers_by_phone(_member_phone(store))[0]
    for n, spec in enumerate(_CALLS, start=1):
        started = datetime.combine(
            now.date() - timedelta(days=spec["ago"]), time.fromisoformat(spec["at"]), tz
        )
        if started > now - timedelta(minutes=15):
            started -= timedelta(days=1)
        ended = started + timedelta(minutes=spec["mins"])
        call_id = f"{SAMPLE_PREFIX}{n:02d}"

        customer = None
        if spec.get("existing") == "member":
            customer = member
        elif spec.get("existing"):
            customer = store.customers_by_phone(spec["existing"])[0]
        elif spec.get("new"):
            first, last, address, zip_code, county = spec["new"]
            cid = store.add_customer(first, last, spec["caller"], address, zip_code, county)
            customer = store.get_customer(cid)
        phone = customer.phone if customer else spec["caller"]

        tools: list[dict[str, Any]] = []
        if spec.get("town") or spec.get("zip"):
            tools.append({"tool": "check_service_address", "refused": False, "at": started.isoformat(),
                          "args": {"town": spec.get("town"), "zip_code": spec.get("zip")},
                          "result": "Outside our service area."})  # fmt: skip
        appointments = []
        if job := spec.get("job"):
            # Positive: days after the call. Zero or negative: relative to today.
            base = started.date() if job["in_days"] > 0 else now.date()
            day = base + timedelta(days=job["in_days"])
            notes = " ".join(
                x
                for x in (
                    f"Caller says: {spec['said']}.",
                    f"Equipment: {job['equipment']}." if job.get("equipment") else "",
                    f"Access: {job['access']}." if job.get("access") else "",
                )
                if x
            )
            tools.append({"tool": "book_appointment", "refused": False, "at": ended.isoformat(),
                          "args": {"job_type": job["type"], "equipment": job.get("equipment")},
                          "result": "Booked"})  # fmt: skip
            appointments.append(
                store.insert_appointment(
                    customer_id=customer.id,
                    call_id=call_id,
                    county=customer.county,
                    day=day,
                    window=job["window"],
                    pool=job["pool"],
                    job_type=job["type"],
                    priority=Priority(spec["p"]),
                    service_address=f"{customer.address}, {customer.zip}",
                    contact_name=customer.full_name,
                    contact_phone=customer.phone,
                    notes=notes,
                )
            )

        callbacks = []
        if cb := spec.get("callback"):
            reason, urgent = cb
            store.add_callback(call_id, phone, reason, ended + timedelta(hours=2), urgent=urgent)
            callbacks.append(reason)
        if alert := spec.get("alert"):
            store.acknowledge_alert(store.add_alert(call_id, *alert))
        elif spec["p"] == 1:
            store.acknowledge_alert(
                store.add_alert(call_id, "urgent", f"URGENT booking after hours: {spec['said']}")
            )

        facts: dict[str, Any] = {"description": spec["said"]}
        for key, field in (("temp", "indoor_temp_f"), ("request", "request_type")):
            if key in spec:
                facts[field] = spec[key]
        if spec.get("vulnerable"):
            facts["vulnerable_occupant"] = True
        record = {
            "sample": True,
            "caller_id": phone,
            "verified_customer_id": customer.id if customer and spec.get("existing") else None,
            "facts": facts,
            "priority": spec["p"],
            "reasons": spec.get("reasons", []),
            "appointments": appointments,
            "callbacks": callbacks,
            "notes": [],
            "false_claims": [],
            "outcome": spec["outcome"],
            "metrics": {
                "turns_measured": 9,
                "latency_p50_s": round(1.05 + 0.04 * (n % 6), 2),
                "latency_p95_s": round(1.6 + 0.05 * (n % 5), 2),
            },  # fmt: skip
            "tools": tools,
        }
        reasons = ", ".join(spec.get("reasons", [])) or outcome_label(spec["outcome"])
        label = f"P{spec['p']} " if spec["p"] is not None else ""
        store.upsert_call(
            call_id,
            caller_id=phone,
            started_at=started,
            ended_at=ended,
            record=record,
            transcript=[
                {"role": "assistant", "text": "Thanks for calling Summit Air. How can I help?"},
                {"role": "user", "text": spec["said"].capitalize() + "."},
                {"role": "assistant", "text": "(Sample call: full transcript not included.)"},
            ],
            priority=Priority(spec["p"]) if spec["p"] is not None else None,
            outcome=spec["outcome"],
            summary=f"{label}{reasons}. Caller says: {spec['said']}.",
        )
    return len(_CALLS)


def _member_phone(store: Store) -> str:
    row = store.conn.execute(
        "SELECT c.phone FROM customers c JOIN memberships m ON m.customer_id = c.id "
        "WHERE m.status = 'active' ORDER BY c.id LIMIT 1"
    ).fetchone()
    return row[0]
