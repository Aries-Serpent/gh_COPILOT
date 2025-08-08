#!/usr/bin/env python3
"""CLI for logging Codex actions to the session log database."""

from __future__ import annotations

import argparse

from utils.codex_log_database import log_codex_event


def main() -> None:
    parser = argparse.ArgumentParser(description="Log a Codex action")
    parser.add_argument("action", help="Action performed")
    parser.add_argument("statement", help="Associated statement")
    parser.add_argument(
        "--session-id", default="default", help="Identifier for the session"
    )
    args = parser.parse_args()
    log_codex_event(args.action, args.statement, session_id=args.session_id)


if __name__ == "__main__":
    main()

