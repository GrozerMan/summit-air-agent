import json
import threading
import urllib.request
from http.server import HTTPServer

import pytest

from dashboard.server import Handler
from summit.triage import Facts


@pytest.fixture
def dashboard(make_call, seeded):
    call = make_call("+16315550177")
    call.assess_situation(Facts(gas_smell=True))
    call.finalize([{"role": "user", "text": "I smell gas"}])

    Handler.store = seeded
    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


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
