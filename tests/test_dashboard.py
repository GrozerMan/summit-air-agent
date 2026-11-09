import json
import threading
import urllib.request
from http.server import HTTPServer

import pytest

from dashboard.server import Handler
from summit.sample_week import add_sample_week
from summit.triage import Facts
from tests.conftest import TUESDAY_10AM


@pytest.fixture
def dashboard(make_call, seeded, cfg):
    call = make_call("+16315550177")
    call.assess_situation(Facts(gas_smell=True))
    call.finalize([{"role": "user", "text": "I smell gas"}])

    Handler.store = seeded
    Handler.cfg = cfg
    Handler.clock = lambda: TUESDAY_10AM
    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    Handler.clock = None


def fetch(url, method="GET"):
    with urllib.request.urlopen(urllib.request.Request(url, method=method)) as response:
        return json.loads(response.read())


def test_api_lists_calls_and_alerts(dashboard):
    assert fetch(f"{dashboard}/api/calls")[0]["outcome"] == "safety_emergency"
    assert fetch(f"{dashboard}/api/alerts")[0]["severity"] == "critical"
    assert fetch(f"{dashboard}/api/appointments")[0]["job_type"] == "tune-up"


def test_call_detail_includes_transcript(dashboard):
    call = fetch(f"{dashboard}/api/calls/call-1")
    assert call["transcript"][0]["text"] == "I smell gas"
    assert call["record"]["priority"] == 0


def test_alerts_can_be_acknowledged(dashboard):
    alert_id = fetch(f"{dashboard}/api/alerts")[0]["id"]
    fetch(f"{dashboard}/api/alerts/{alert_id}/ack", method="POST")
    assert fetch(f"{dashboard}/api/alerts")[0]["acknowledged"] == 1


def test_appointments_lists_upcoming_only(dashboard, seeded, cfg):
    add_sample_week(seeded, cfg, TUESDAY_10AM)
    days = [a["day"] for a in fetch(f"{dashboard}/api/appointments")]
    assert days and min(days) >= TUESDAY_10AM.date().isoformat()


def test_owner_views(dashboard, seeded, cfg):
    add_sample_week(seeded, cfg, TUESDAY_10AM)
    results = fetch(f"{dashboard}/api/results?days=7")
    assert results["calls"] == 15 and results["sample"] is True
    assert fetch(f"{dashboard}/api/results?days=1")["calls"] == 2

    followups = fetch(f"{dashboard}/api/followups")
    keys = [o["key"] for o in followups["items"]]
    assert "sample-02:renewal" in keys and followups["outside"]
    fetch(f"{dashboard}/api/followups/sample-02%3Arenewal/done", method="POST")
    assert "sample-02:renewal" not in [o["key"] for o in fetch(f"{dashboard}/api/followups")["items"]]

    brief = fetch(f"{dashboard}/api/brief")
    assert brief["overnight"]["calls"] == 5  # the sample overnight, plus the fixture's gas call this morning
    assert brief["text"].startswith("Summit Air morning brief")
