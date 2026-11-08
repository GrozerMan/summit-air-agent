"""Live board of calls, alerts, callbacks and bookings for the office.

    uv run python -m dashboard.server      then open http://localhost:8765

Standard library only: a small JSON API over data/summit.db and one static page.
"""

import contextlib
import json
import re
from datetime import datetime
from http import HTTPStatus
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

from summit import config, insights
from summit.store import Store

STATIC = Path(__file__).parent / "static"
PORT = 8765

QUERIES = {
    "/api/alerts": "SELECT * FROM alerts ORDER BY acknowledged, id DESC LIMIT 100",
    "/api/callbacks": "SELECT * FROM callbacks WHERE status = 'open' ORDER BY urgent DESC, due_at",
    "/api/calls": (
        "SELECT id, caller_id, started_at, ended_at, priority, outcome, summary "
        "FROM calls ORDER BY started_at DESC LIMIT 100"
    ),
}


# Upcoming only: past visits from earlier in the week aren't the dispatcher's concern.
APPOINTMENTS = (
    "SELECT a.*, c.first_name || ' ' || c.last_name AS customer FROM appointments a "
    "JOIN customers c ON c.id = a.customer_id WHERE a.status IN ('booked', 'on_hold') AND a.day >= ? "
    "ORDER BY a.day, a.arrival_window"
)


class Handler(SimpleHTTPRequestHandler):
    store: Store
    cfg: dict
    clock = None  # tests pin the time; None means now

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def now(self) -> datetime:
        clock = type(self).clock  # looked up on the class, so a plain function stays unbound
        return clock() if clock else datetime.now(config.timezone(self.cfg))

    def do_GET(self) -> None:
        url = urlsplit(self.path)
        path, query = url.path, parse_qs(url.query)
        if path in QUERIES:
            rows = self.store.conn.execute(QUERIES[path]).fetchall()
            return self._json([dict(r) for r in rows])
        if path == "/api/appointments":
            rows = self.store.conn.execute(APPOINTMENTS, (self.now().date().isoformat(),)).fetchall()
            return self._json([dict(r) for r in rows])
        if path == "/api/results":
            days = int((query.get("days") or ["7"])[0])
            return self._json(insights.results(self.store, self.cfg, self.now(), days))
        if path == "/api/followups":
            now = self.now()
            return self._json(
                {
                    "items": insights.opportunities(self.store, self.cfg, now),
                    "outside": insights.outside_demand(self.store, self.cfg, now),
                }
            )
        if path == "/api/brief":
            report = insights.brief(self.store, self.cfg, self.now())
            return self._json({**report, "text": insights.brief_text(report, self.cfg)})
        if match := re.fullmatch(r"/api/calls/([\w-]+)", path):
            call = self.store.get_call(match[1])
            return self._json(call) if call else self.send_error(HTTPStatus.NOT_FOUND)
        return super().do_GET()

    def do_POST(self) -> None:
        if match := re.fullmatch(r"/api/alerts/(\d+)/ack", self.path):
            self.store.acknowledge_alert(int(match[1]))
            return self._json({"ok": True})
        if match := re.fullmatch(r"/api/callbacks/(\d+)/done", self.path):
            self.store.conn.execute("UPDATE callbacks SET status = 'done' WHERE id = ?", (int(match[1]),))
            return self._json({"ok": True})
        if match := re.fullmatch(r"/api/followups/([^/]+)/done", self.path):
            self.store.mark_followup_done(unquote(match[1]))
            return self._json({"ok": True})
        self.send_error(HTTPStatus.NOT_FOUND)

    def _json(self, payload) -> None:
        body = json.dumps(payload, default=str).encode()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args) -> None:
        pass  # the page polls every couple of seconds; don't flood the terminal


def main() -> None:
    Handler.store = Store()
    Handler.cfg = config.load()
    # Single-threaded on purpose: one office screen polling, one SQLite connection.
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Dashboard on http://localhost:{PORT}")
    with contextlib.suppress(KeyboardInterrupt):
        server.serve_forever()


if __name__ == "__main__":
    main()
