import os
import tomllib
from datetime import date, datetime, time, timedelta
from functools import cache
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "business.toml"

WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


@cache
def load(path: Path = CONFIG_PATH) -> dict[str, Any]:
    with open(path, "rb") as f:
        cfg = tomllib.load(f)

    transfer = os.getenv("HUMAN_TRANSFER_NUMBER")
    if transfer:
        cfg["escalation"]["human_transfer_number"] = transfer
    return cfg


def db_path() -> Path:
    return ROOT / os.getenv("SUMMIT_DB_PATH", "data/summit.db")


def timezone(cfg: dict[str, Any]) -> ZoneInfo:
    return ZoneInfo(cfg["company"]["timezone"])


def office_hours(cfg: dict[str, Any], day: date) -> tuple[time, time] | None:
    hours = cfg["hours"][WEEKDAYS[day.weekday()]]
    if not hours:
        return None
    opens, closes = hours
    return time.fromisoformat(opens), time.fromisoformat(closes)


def office_open(cfg: dict[str, Any], now: datetime) -> bool:
    hours = office_hours(cfg, now)
    if hours is None:
        return False
    opens, closes = hours
    return opens <= now.time() < closes


def next_office_opening(cfg: dict[str, Any], now: datetime) -> datetime:
    """The next time the office opens, or `now` if it's open already."""
    if office_open(cfg, now):
        return now
    for offset in range(8):
        day = now + timedelta(days=offset)
        hours = office_hours(cfg, day)
        if hours is None:
            continue
        opening = datetime.combine(day.date(), hours[0], tzinfo=now.tzinfo)
        if opening > now:
            return opening
    raise ValueError("office hours are empty for every day of the week")
