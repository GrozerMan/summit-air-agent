"""The owner's morning brief: what happened since the office closed, today's jobs, and
who to call back.

    uv run python -m summit.brief            print it
    uv run python -m summit.brief --slack    also post it to SLACK_WEBHOOK_URL

Run it from cron (or launchd) at 7am and it lands on the owner's phone.
"""

import argparse
from datetime import datetime

from dotenv import load_dotenv

from summit import config
from summit.insights import brief, brief_text
from summit.notify import Notifier
from summit.store import Store


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the morning brief")
    parser.add_argument("--slack", action="store_true", help="also post it to SLACK_WEBHOOK_URL")
    args = parser.parse_args()

    load_dotenv(config.ROOT / ".env.local")  # SLACK_WEBHOOK_URL, DATABASE_URL
    cfg = config.load()
    store = Store()
    text = brief_text(brief(store, cfg, datetime.now(config.timezone(cfg))), cfg)
    print(text)
    if args.slack:
        sent = Notifier(store).send(text)
        print("\nPosted to Slack." if sent else "\nNot posted: set SLACK_WEBHOOK_URL in .env.local.")


if __name__ == "__main__":
    main()
