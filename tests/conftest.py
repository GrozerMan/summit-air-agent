from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from summit import config
from summit.backend import CallSession
from summit.seed import DEMO_MEMBER_PHONE, seed
from summit.store import Store

TZ = ZoneInfo("America/New_York")

# A Tuesday, mid-morning, office open. Every test runs against this clock.
TUESDAY_10AM = datetime(2026, 11, 3, 10, 0, tzinfo=TZ)


@pytest.fixture
def cfg():
    return config.load()


@pytest.fixture
def store():
    s = Store(":memory:")
    yield s
    s.close()


@pytest.fixture
def seeded(store):
    seed(store, today=TUESDAY_10AM.date())
    return store


@pytest.fixture
def make_call(seeded, cfg):
    def make(caller_id: str | None = None, now: datetime = TUESDAY_10AM, call_id: str = "call-1"):
        call = CallSession(call_id, caller_id, seeded, cfg, clock=lambda: now)
        call.prefetch_caller()
        return call

    return make


@pytest.fixture
def member_call(make_call):
    return make_call(DEMO_MEMBER_PHONE)
