"""Arrival windows and capacity.

Each county has three kinds of capacity:

    regular    N jobs per arrival window
    emergency  a few jobs per day held back for P1 calls, so urgent callers
               aren't told "next Thursday" because routine work filled the week
    member     a few jobs per day only active members can take

Routine (P3) work never takes same-day capacity. The calendar starts with a
fake, deterministic load so the demo has realistic gaps in it.
"""

import hashlib
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Any

from summit import config
from summit.models import Pool, Priority
from summit.store import Store


class AppointmentChanged(Exception):
    """The appointment being moved isn't booked any more (moved or cancelled meanwhile)."""


def window_bounds(window: str) -> tuple[time, time]:
    start, end = window.split("-")
    return time.fromisoformat(start), time.fromisoformat(end)


def _hour(t: time) -> str:
    if t.hour == 12:
        return "noon"
    hour = t.hour % 12 or 12
    return f"{hour}:{t.minute:02d}" if t.minute else str(hour)


def say_window(window: str) -> str:
    """Turn 08:00-10:00 into "between 8 and 10 AM", 10:00-12:00 into "between 10 AM and noon"."""
    start, end = window_bounds(window)
    start_half = "AM" if start.hour < 12 else "PM"
    end_half = "AM" if end.hour < 12 else "PM"
    if _hour(start) == "noon":
        return f"between noon and {_hour(end)} {end_half}"
    if _hour(end) == "noon":
        return f"between {_hour(start)} AM and noon"
    if start_half == end_half:
        return f"between {_hour(start)} and {_hour(end)} {end_half}"
    return f"between {_hour(start)} {start_half} and {_hour(end)} {end_half}"


def say_day(day: date, today: date) -> str:
    if day == today:
        return f"today, {day:%A}"
    if day == today + timedelta(days=1):
        return f"tomorrow, {day:%A}"
    return f"{day:%A}, {day:%B} {day.day}"


@dataclass(frozen=True)
class Option:
    option_id: str
    county: str
    day: date
    window: str
    pool: Pool
    after_hours: bool

    def speakable(self, today: date) -> str:
        return f"{say_day(self.day, today)}, {say_window(self.window)}"


class Scheduler:
    def __init__(self, store: Store, cfg: dict[str, Any]) -> None:
        self.store = store
        self.cfg = cfg
        self.rules = cfg["scheduling"]
        self.tz = config.timezone(cfg)

    def find_options(
        self,
        county: str,
        priority: Priority,
        is_member: bool,
        now: datetime,
        limit: int | None = None,
    ) -> list[Option]:
        """Earliest windows first, one option per window, saving reserve capacity
        for when regular capacity has run out."""
        limit = limit or self.rules["options_to_offer"]
        now = now.astimezone(self.tz)
        pools = self._pools(priority, is_member)

        options: list[Option] = []
        for offset in range(self.rules["horizon_days"] + 1):
            day = now.date() + timedelta(days=offset)
            for window in self.rules["windows"]:
                if not self._window_fits(day, window, priority, now):
                    continue
                pool = next((p for p in pools if self.seats_left(county, day, window, p) > 0), None)
                if pool is None:
                    continue
                options.append(self._option(county, day, window, pool))
                if len(options) == limit:
                    return options
        return options

    def still_fits(self, option: Option, priority: Priority, is_member: bool, now: datetime) -> str | None:
        """Why an option offered earlier on the call no longer fits the call as it is now,
        or None if it still does. Seats are re-checked separately, under the write lock."""
        if option.pool not in self._pools(priority, is_member):
            return f"it came from {option.pool.value} capacity, which a {priority.label} call can't use"
        if not self._window_fits(option.day, option.window, priority, now.astimezone(self.tz)):
            limit = self.latest_start(priority, now) - now
            hours = int(limit.total_seconds() // 3600)
            return f"a {priority.label} call has to start within {hours} hours, on a day this kind of work goes out"
        return None

    def latest_start(self, priority: Priority, now: datetime) -> datetime:
        if priority == Priority.P1:
            return now + timedelta(hours=self.cfg["triage"]["p1_within_hours"])
        if priority == Priority.P2:
            return now + timedelta(hours=self.cfg["triage"]["p2_within_hours"])
        return now + timedelta(days=self.rules["horizon_days"])

    def _pools(self, priority: Priority, is_member: bool) -> list[Pool]:
        pools = [Pool.REGULAR]
        if is_member:
            pools.append(Pool.MEMBER)
        if priority == Priority.P1:
            pools.append(Pool.EMERGENCY)
        return pools

    def _window_fits(self, day: date, window: str, priority: Priority, now: datetime) -> bool:
        if priority == Priority.P3 and day == now.date():
            return False
        # Only urgent work goes out on days the office is closed.
        if priority != Priority.P1 and config.office_hours(self.cfg, day) is None:
            return False
        start = datetime.combine(day, window_bounds(window)[0], tzinfo=self.tz)
        earliest = now + timedelta(minutes=self.rules["lead_minutes"])
        return earliest <= start < self.latest_start(priority, now)

    def seats_left(self, county: str, day: date, window: str, pool: Pool) -> int:
        if pool == Pool.REGULAR:
            capacity = self.rules["jobs_per_window_per_county"] - self.simulated_load(county, day, window)
            return capacity - self.store.count_booked(county, day, pool, window)
        if pool == Pool.EMERGENCY:
            capacity = self.rules["emergency_reserve_per_day_per_county"]
        else:
            capacity = self.rules["member_priority_per_day_per_county"]
        return capacity - self.store.count_booked(county, day, pool)

    def simulated_load(self, county: str, day: date, window: str) -> int:
        """Jobs already on the books before the demo started. Deterministic per slot."""
        key = f"{self.rules['simulated_load_seed']}:{county}:{day.isoformat()}:{window}"
        roll = int(hashlib.sha256(key.encode()).hexdigest(), 16) % 100
        capacity = self.rules["jobs_per_window_per_county"]
        if roll < 55:
            return capacity
        if roll < 80:
            return capacity - 1
        return 0

    def book(self, option: Option, **appointment: Any) -> int | None:
        """Book the option, re-checking the seat under the write lock. None if it's gone."""
        with self.store.write_lock():
            if self.seats_left(option.county, option.day, option.window, option.pool) <= 0:
                return None
            return self.store.insert_appointment(
                county=option.county,
                day=option.day,
                window=option.window,
                pool=option.pool,
                **appointment,
            )

    def move(self, appointment_id: int, option: Option, **appointment: Any) -> int | None:
        """Book the new window and release the old one in the same transaction.

        The old appointment's status is checked under the lock too: two calls moving the
        same appointment at once used to both pass the check outside it and both insert.
        """
        with self.store.write_lock():
            if self.seats_left(option.county, option.day, option.window, option.pool) <= 0:
                return None
            if not self.store.mark_moved(appointment_id):
                raise AppointmentChanged(appointment_id)
            return self.store.insert_appointment(
                county=option.county,
                day=option.day,
                window=option.window,
                pool=option.pool,
                **appointment,
            )

    def _option(self, county: str, day: date, window: str, pool: Pool) -> Option:
        start, end = window_bounds(window)
        hours = config.office_hours(self.cfg, day)
        after_hours = hours is None or start < hours[0] or end > hours[1]
        option_id = f"{county[:3].upper()}-{day:%m%d}-{start:%H%M}-{pool.value[0].upper()}"
        return Option(option_id, county, day, window, pool, after_hours)
