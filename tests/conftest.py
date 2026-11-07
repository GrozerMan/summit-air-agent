import os
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


# SUMMIT_TEST_POSTGRES=1 runs every test against a throwaway Postgres (pgserver, a dev
# dependency) instead of in-memory SQLite: the deployed agent's database.
ON_POSTGRES = os.getenv("SUMMIT_TEST_POSTGRES") == "1"


@pytest.fixture(scope="session")
def pg_uri(tmp_path_factory):
    """A throwaway Postgres server for the session."""
    pgserver = pytest.importorskip("pgserver")
    server = pgserver.get_server(tmp_path_factory.mktemp("pg"), cleanup_mode="stop")
    yield server.get_uri()
    server.cleanup()


def fresh_postgres(uri: str) -> str:
    import psycopg

    with psycopg.connect(uri, autocommit=True) as conn:
        conn.execute("DROP SCHEMA public CASCADE")
        conn.execute("CREATE SCHEMA public")
    return uri


@pytest.fixture
def store(request):
    s = Store(fresh_postgres(request.getfixturevalue("pg_uri"))) if ON_POSTGRES else Store(":memory:")
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
