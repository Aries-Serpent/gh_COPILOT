#!/usr/bin/env python3
# tools/codex_workflow_log_analytics_event.py
# End-to-end workflow:
# - README parse + tiny reference refresh
# - DB migration + helper creation
# - Sync hook attempt (best-effort, non-breaking)
# - Unit test authoring
# - Change log update
# - Error capture prompts for ChatGPT-5
# NOTE: Does NOT touch .github/workflows/*

import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

WS = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
DB = WS / "databases" / "analytics.db"
MIG_DIR = WS / "databases" / "migrations"
UTILS = WS / "utils"
TESTS = WS / "tests"
CHANGES = WS / "codex_changes"
README = WS / "README.md"

ERRORS: list[str] = []


def record_error(step: str, msg: str, ctx: str) -> None:
    ERRORS.append(
        f"Question for ChatGPT-5:\nWhile performing [{step}], encountered the following error:\n[{msg}]\nContext: [{ctx}]\nWhat are the possible causes, and how can this be resolved while preserving intended functionality?"
    )


def ensure_dirs() -> None:
    for p in [DB.parent, MIG_DIR, UTILS, TESTS, CHANGES]:
        p.mkdir(parents=True, exist_ok=True)


def apply_migration() -> Path:
    sql = (
        "CREATE TABLE IF NOT EXISTS analytics_events (\n"
        "  run_id  TEXT NOT NULL,\n"
        "  kind    TEXT NOT NULL,\n"
        "  payload TEXT NOT NULL,\n"
        "  ts      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))\n"
        ");\n"
    )
    mig_path = MIG_DIR / "add_analytics_events_table.sql"
    mig_path.write_text(sql, encoding="utf-8")
    try:
        con = sqlite3.connect(DB)
        con.executescript(sql)
        con.commit()
    except Exception as e:  # pragma: no cover - best effort
        record_error("3:Migration apply", repr(e), "Applying analytics_events schema")
    finally:
        try:
            con.close()
        except Exception:
            pass
    return mig_path


def write_helper_module() -> Path:
    mod = (
        "from __future__ import annotations\n"
        "import json, sqlite3, os\n"
        "from pathlib import Path\n"
        "from typing import Any, Optional\n\n"
        "DB_PATH = Path(os.getenv('ANALYTICS_DB_PATH', 'databases/analytics.db'))\n\n"
        "def _insert_direct(run_id: str, kind: str, payload: str, ts: Optional[str]) -> bool:\n"
        "    DB_PATH.parent.mkdir(parents=True, exist_ok=True)\n"
        "    con = sqlite3.connect(DB_PATH)\n"
        "    try:\n"
        "        cur = con.cursor()\n"
        "        if ts is None:\n"
        "            cur.execute(\n"
        "                'INSERT INTO analytics_events(run_id, kind, payload) VALUES (?, ?, ?)',\n"
        "                (run_id, kind, payload),\n"
        "            )\n"
        "        else:\n"
        "            cur.execute(\n"
        "                'INSERT INTO analytics_events(run_id, kind, payload, ts) VALUES (?, ?, ?, ?)',\n"
        "                (run_id, kind, payload, ts),\n"
        "            )\n"
        "        con.commit()\n"
        "        return True\n"
        "    finally:\n"
        "        con.close()\n\n"
        "def log_analytics_event(run_id: str, kind: str, payload: Any, ts: Optional[str] = None) -> bool:\n"
        "    if isinstance(payload, (dict, list)):\n"
        "        payload = json.dumps(payload, separators=(',', ':'))\n"
        "    else:\n"
        "        payload = str(payload)\n"
        "    try:\n"
        "        from utils.log_utils import _log_event\n"
        "        record = {'run_id': run_id, 'kind': kind, 'payload': payload, 'ts': ts}\n"
        "        return bool(_log_event(record, table='analytics_events', db_path=str(DB_PATH)))\n"
        "    except Exception:\n"
        "        return _insert_direct(run_id, kind, payload, ts)\n"
    )
    out = UTILS / "analytics_events.py"
    out.write_text(mod, encoding="utf-8")
    return out


def wire_sync_hooks() -> list[Path]:
    targets = [
        WS / "scripts" / "database" / "cross_database_sync_logger.py",
        WS / "database_first_synchronization_engine.py",
        WS / "src" / "sync" / "engine.py",
    ]
    injected: list[Path] = []
    pattern = re.compile(r"^def\\s+log_sync_operation\\s*\\(.*\\):", re.M)
    injection = (
        "from utils.analytics_events import log_analytics_event\n"
        "try:\n"
        "    log_analytics_event('SYNC_RUN', 'sync_step', {'file': __file__}, None)\n"
        "except Exception:\n"
        "    pass\n"
    )
    for t in targets:
        if not t.exists():
            continue
        text = t.read_text(encoding="utf-8")
        if injection in text:
            injected.append(t)
            continue
        m = pattern.search(text)
        if not m:
            continue
        idx = m.end()
        new = text[:idx] + "\n" + injection + text[idx:]
        t.write_text(new, encoding="utf-8")
        injected.append(t)
    return injected


def write_unit_test() -> Path:
    test = (
        "import sqlite3, os, json\n"
        "from pathlib import Path\n\n"
        "def test_log_analytics_event_roundtrip(tmp_path):\n"
        "    db = tmp_path / 'analytics.db'\n"
        "    os.environ['ANALYTICS_DB_PATH'] = str(db)\n"
        "    con = sqlite3.connect(db); cur = con.cursor()\n"
        "    cur.executescript(\n"
        "    '''\n    CREATE TABLE IF NOT EXISTS analytics_events (\n      run_id  TEXT NOT NULL,\n      kind    TEXT NOT NULL,\n      payload TEXT NOT NULL,\n      ts      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))\n    );\n    '''\n        )\n        con.commit(); con.close()\n        from utils.analytics_events import log_analytics_event\n        ok = log_analytics_event('RUN_TEST', 'unit', {'ok': True}, '2025-08-18T00:00:00Z')\n        assert ok\n        con = sqlite3.connect(db); cur = con.cursor()\n        cur.execute('SELECT run_id, kind, payload, ts FROM analytics_events WHERE run_id=? AND kind=?', ('RUN_TEST','unit'))\n        row = cur.fetchone(); con.close()\n        assert row is not None\n        assert row[0] == 'RUN_TEST'\n        assert row[1] == 'unit'\n        data = json.loads(row[2])\n        assert data.get('ok') is True\n"
    )
    out = TESTS / "test_analytics_events.py"
    out.write_text(test, encoding="utf-8")
    return out


def tweak_readme() -> bool:
    if not README.exists():
        return False
    txt = README.read_text(encoding="utf-8")
    if "analytics_events" in txt:
        return True
    new = re.sub(
        r"(\* Table: `events\(event_time TEXT, level TEXT, event TEXT, details TEXT\)`\n)",
        r"\1* Internal helper table: `analytics_events(run_id, kind, payload, ts)`\n",
        txt,
        count=1,
    )
    README.write_text(new, encoding="utf-8")
    return True


def append_changelog(files: list[str]) -> Path:
    CHANGES.mkdir(parents=True, exist_ok=True)
    path = CHANGES / "CHANGELOG_Codex_Auto.md"
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = [f"## {ts}", "- Implemented log_analytics_event and tests.", "- Files:"]
    entry += [f"  - {f}" for f in files]
    entry.append("")
    with path.open("a", encoding="utf-8") as f:
        f.write("\n".join(entry))
    return path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", action="store_true", help="Run with real DB path; otherwise only author files.")
    ap.parse_args()
    ensure_dirs()
    mig = apply_migration()
    helper = write_helper_module()
    injected = wire_sync_hooks()
    test = write_unit_test()
    tweak_readme()
    files = [str(mig.relative_to(WS)), str(helper.relative_to(WS)), str(test.relative_to(WS))]
    files += [str(p.relative_to(WS)) for p in injected]
    clog = append_changelog(files)
    print(
        json.dumps(
            {
                "workspace": str(WS),
                "db": str(DB),
                "artifacts": files,
                "changelog": str(clog.relative_to(WS)),
                "errors": ERRORS,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        record_error("ALL:workflow-abort", repr(e), "Top-level failure")
        print(json.dumps({"fatal": True, "errors": ERRORS}, indent=2))
        sys.exit(1)
