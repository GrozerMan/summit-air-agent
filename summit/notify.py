import json
import logging
import os
import threading
import urllib.request

from summit.store import Store

logger = logging.getLogger("summit.notify")

_SLACK_ICONS = {"critical": ":rotating_light:", "urgent": ":warning:", "info": ":information_source:"}


class Notifier:
    """Dispatcher alerts. The alerts table is the source of truth; Slack is a courtesy copy."""

    def __init__(self, store: Store, slack_webhook_url: str | None = None) -> None:
        self.store = store
        self.slack_webhook_url = slack_webhook_url or os.getenv("SLACK_WEBHOOK_URL") or None

    def alert(self, call_id: str | None, severity: str, summary: str) -> int:
        alert_id = self.store.add_alert(call_id, severity, summary)
        if self.slack_webhook_url:
            # Off the event loop: a slow or dead Slack must never stall a live call.
            text = f"{_SLACK_ICONS.get(severity, '')} *{severity.upper()}* {summary}"
            threading.Thread(target=_post_slack, args=(self.slack_webhook_url, text), daemon=True).start()
        return alert_id

    def send(self, text: str) -> bool:
        """Post a message (the morning brief) to Slack, waiting for it. False if no webhook
        is set or the post failed."""
        return bool(self.slack_webhook_url) and _post_slack(self.slack_webhook_url, text)


def _post_slack(url: str, text: str) -> bool:
    request = urllib.request.Request(
        url,
        data=json.dumps({"text": text}).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(request, timeout=3).close()
        return True
    except Exception:
        logger.warning("couldn't post to Slack", exc_info=True)
        return False
