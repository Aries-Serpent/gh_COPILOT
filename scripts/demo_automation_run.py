#!/usr/bin/env python
from __future__ import annotations

import json
import os
from datetime import datetime

from gh_copilot.automation.core import StepCtx, run_phases
from gh_copilot.automation.logging import append_ndjson


def main() -> int:
    dry_run = os.environ.get("DRY_RUN", "1") != "0"

    def prepare(dry_run: bool = True) -> None:
        _ = dry_run
        return None

    def analyze(dry_run: bool = True) -> None:
        root = os.path.join(os.getcwd(), "gh_copilot")
        names = []
        if os.path.isdir(root):
            for n in os.listdir(root)[:20]:
                names.append(n)
        print("Analyze summary:", json.dumps({"count": len(names), "sample": names[:5]}))

    def finalize(dry_run: bool = True) -> None:
        log_path = os.path.join(os.getcwd(), ".codex", "action_log.ndjson")
        append_ndjson(
            log_path,
            {
                "ts": datetime.utcnow().isoformat() + "Z",
                "event": "demo_finalize",
                "dry_run": dry_run,
            },
        )

    phases = [
        StepCtx(name="Prepare", desc="Initialize", fn=prepare),
        StepCtx(name="Analyze", desc="Summarize gh_copilot/", fn=analyze),
        StepCtx(name="Finalize", desc="Log one entry", fn=finalize),
    ]

    result = run_phases(phases, dry_run=dry_run)
    print(
        "Run result:",
        json.dumps({"phases_completed": result.phases_completed, "ok": result.ok}),
    )
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

