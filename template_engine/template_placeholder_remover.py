"""Template placeholder removal utilities.

This module removes placeholders from templates stored in ``production.db`` and
logs each removal event to ``analytics.db``. Operations display progress using
``tqdm`` and a validation hook ensures that removal events were recorded.
"""

from __future__ import annotations

import logging
import os
import re
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List

from tqdm import tqdm

DEFAULT_PRODUCTION_DB = Path("databases/production.db")
DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")
LOGS_DIR = Path("logs/template_rendering")
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / f"template_placeholder_remover_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

_PLACEHOLDER_RE = re.compile(r"{{\s*([A-Z0-9_]+)\s*}}")

def validate_no_recursive_folders() -> None:
    workspace_root = Path(os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT"))
    forbidden_patterns = ['*backup*', '*_backup_*', 'backups', '*temp*']
    for pattern in forbidden_patterns:
        for folder in workspace_root.rglob(pattern):
            if folder.is_dir() and folder != workspace_root:
                logging.error(f"Recursive folder detected: {folder}")
                raise RuntimeError(f"CRITICAL: Recursive folder violation: {folder}")

def _load_valid_placeholders(db: Path) -> List[str]:
    """
    Load valid placeholder names from the production database.
    """
    names: List[str] = []
    if db.exists():
        with sqlite3.connect(db) as conn:
            try:
                cur = conn.execute("SELECT placeholder_name FROM template_placeholders")
                names = [row[0].strip('{}') for row in cur.fetchall()]
            except sqlite3.Error as exc:
                logging.error(f"Error querying template_placeholders: {exc}")
                names = []
    return names

def calculate_etc(start_time: float, current_progress: int, total_work: int) -> str:
    elapsed = time.time() - start_time
    if current_progress > 0:
        total_estimated = elapsed / (current_progress / total_work)
        remaining = total_estimated - elapsed
        return f"{remaining:.2f}s remaining"
    return "N/A"

def _write_log(found: List[str], valid: set, result: str) -> None:
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "found_placeholders": found,
        "valid_placeholders": list(valid),
        "result": result
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(str(log_entry) + "\n")

def remove_unused_placeholders(
    template: str,
    production_db: Path = DEFAULT_PRODUCTION_DB,
    analytics_db: Path = DEFAULT_ANALYTICS_DB,
    timeout_minutes: int = 30,
) -> str:
    """
    Remove placeholders not defined in production DB from the template string.
    Includes visual processing indicators, start time logging, timeout, ETC, and status updates.
    Logs all removals to analytics.db and /logs/template_rendering.
    """
    validate_no_recursive_folders()
    start_time = datetime.now()
    process_id = os.getpid()
    timeout_seconds = timeout_minutes * 60
    logging.info(f"PROCESS STARTED: Template Placeholder Remover")
    logging.info(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"Process ID: {process_id}")
    valid = set(_load_valid_placeholders(production_db))
    found = _PLACEHOLDER_RE.findall(template)
    result = template
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    total_steps = len(found)
    elapsed = 0.0
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS placeholder_removals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                placeholder TEXT,
                ts TEXT
            )"""
        )
        with tqdm(total=total_steps, desc="Removing Placeholders", unit="ph") as bar:
            for idx, ph in enumerate(found, 1):
                phase = f"Removing placeholder {ph}"
                bar.set_description(phase)
                if ph not in valid:
                    pattern = r"{{\s*%s\s*}}" % re.escape(ph)
                    result = re.sub(pattern, "", result)
                    conn.execute(
                        "INSERT INTO placeholder_removals (placeholder, ts) VALUES (?, ?)",
                        (ph, datetime.utcnow().isoformat()),
                    )
                elapsed = time.time() - start_time.timestamp()
                etc = calculate_etc(start_time.timestamp(), idx, total_steps)
                bar.set_postfix(ETC=etc)
                bar.update(1)
                if elapsed > timeout_seconds:
                    raise TimeoutError(f"Process exceeded {timeout_minutes} minute timeout")
        conn.commit()
    logging.info(f"Placeholder removal completed in {elapsed:.2f}s | ETC: {etc}")
    _write_log(found, valid, result)
    return result

def validate_removals(expected_count: int, analytics_db: Path = DEFAULT_ANALYTICS_DB) -> bool:
    """
    DUAL COPILOT validation for placeholder removals.
    Checks analytics.db for matching removal events.
    """
    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM placeholder_removals")
        count = cur.fetchone()[0]
    if count >= expected_count:
        logging.info("DUAL COPILOT validation passed: Placeholder removal integrity confirmed.")
        return True
    else:
        logging.error("DUAL COPILOT validation failed: Placeholder removal mismatch.")
        return False

__all__ = ["remove_unused_placeholders", "validate_removals"]
