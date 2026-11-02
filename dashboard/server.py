"""Live board of calls, alerts, callbacks and bookings for the office.

    uv run python -m dashboard.server      then open http://localhost:8765

Standard library only: a small JSON API over data/summit.db and one static page.
"""

import contextlib
import json
import re
from http import HTTPStatus
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from summit.store import Store

STATIC = Path(__file__).parent / "static"
PORT = 8765

QUERIES = {
    "/api/alerts": "SELECT * FROM alerts ORDER BY acknowledged, id DESC LIMIT 100",
    "/api/callbacks": "SELECT * FROM callbacks WHERE status = 'open' ORDER BY urgent DESC, due_at",
    "/api/appointments": (
        "SELECT a.*, c.first_name || ' ' || c.last_name AS customer FROM appointments a "
        "JOIN customers c ON c.id = a.customer_id WHERE a.status IN ('booked', 'on_hold') "
        "ORDER BY a.day, a.arrival_window"
    ),
    "/api/calls": (
        "SELECT id, caller_id, started_at, ended_at, priority, outcome, summary "
        "FROM calls ORDER BY started_at DESC LIMIT 100"
    ),
}


class Handler(SimpleHTTPRequestHandler):
    store: Store

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def do_GET(self) -> None:
        if self.path in QUERIES:
            rows = self.store.conn.execute(QUERIES[self.path]).fetchall()
            return self._json([dict(r) for r in rows])
        if match := re.fullmatch(r"/api/calls/([\w-]+)", self.path):
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
    # Single-threaded on purpose: one office screen polling, one SQLite connection.
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Dashboard on http://localhost:{PORT}")
    with contextlib.suppress(KeyboardInterrupt):
        server.serve_forever()


if __name__ == "__main__":
    main()
