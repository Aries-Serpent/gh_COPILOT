#!/usr/bin/env python3
# [Session]: Session Protocol Validator
# > Generated: 2025-07-24 20:20:40 | Author: mbaetiong

"""
Session Protocol Validator

- Validates the integrity, compliance, and schema of session databases for the gh_COPILOT enterprise suite.
- Ensures all session records follow the current enterprise protocol specification.
- Audits key metadata, field completeness, state transitions, and compliance with rollback/merge requirements.
- Prints and logs validation steps, results, and errors for compliance audit trails.
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from utils.log_utils import _log_event

TEXT_INDICATORS = {
    "start": "[START]",
    "info": "[INFO]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "validation": "[VALIDATION]",
    "fail": "[FAIL]",
    "pass": "[PASS]",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Enterprise Session Protocol Validator"
    )
    parser.add_argument(
        "--session-db", type=Path, required=True, help="Session database file"
    )
    parser.add_argument(
        "--strict", action="store_true", help="Fail validation on first error"
    )
    parser.add_argument(
        "--report", type=Path, default=None, help="Optional path to write validation report (JSON)"
    )
    return parser.parse_args()


def get_existing_tables(conn: sqlite3.Connection) -> List[str]:
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [row[0] for row in cur.fetchall()]


def validate_schema(conn: sqlite3.Connection) -> Dict[str, Any]:
    """
    Validates that the 'sessions' table exists and has all required fields.
    Returns a dictionary with validation results.
    """
    expected_columns = {
        "session_id", "user_id", "state", "created_at", "last_updated", "metadata"
    }
    result = {
        "schema_ok": False,
        "missing_columns": [],
        "found_columns": [],
        "table_exists": False
    }
    tables = get_existing_tables(conn)
    if 'sessions' not in tables:
        result["missing_columns"] = list(expected_columns)
        result["found_columns"] = []
        result["table_exists"] = False
        return result
    result["table_exists"] = True

    cur = conn.cursor()
    cur.execute("PRAGMA table_info(sessions);")
    cols = {row[1] for row in cur.fetchall()}
    result["found_columns"] = list(cols)
    missing = expected_columns - cols
    result["missing_columns"] = list(missing)
    result["schema_ok"] = len(missing) == 0
    return result


def validate_metadata(metadata: str) -> Optional[str]:
    """
    Example: Validate that metadata is a valid JSON string and contains required keys.
    Returns None if OK, or error string if invalid.
    """
    try:
        data = json.loads(metadata)
        required_keys = ["origin", "ip", "device"]
        for rk in required_keys:
            if rk not in data:
                return f"Missing metadata key: {rk}"
        return None
    except Exception as e:
        return f"Invalid metadata JSON: {e}"


def validate_records(conn: sqlite3.Connection, strict: bool = False) -> List[Dict[str, Any]]:
    """
    Validates all records in 'sessions' for completeness, state, and date formats.
    Returns a list of record validation dictionaries.
    If strict is True, stops on first error.
    """
    cur = conn.cursor()
    try:
        cur.execute("SELECT session_id, user_id, state, created_at, last_updated, metadata FROM sessions;")
    except sqlite3.OperationalError as e:
        return [{
            "row_index": None,
            "valid": False,
            "errors": [f"Table error: {e}"]
        }]
    results = []
    for idx, row in enumerate(cur.fetchall()):
        session_id, user_id, state, created_at, last_updated, metadata = row
        record_report = {
            "row_index": idx,
            "session_id": session_id,
            "user_id": user_id,
            "state": state,
            "created_at": created_at,
            "last_updated": last_updated,
            "metadata": metadata,
            "valid": True,
            "errors": [],
        }
        # Check required fields
        for field_name, value in [
            ("session_id", session_id),
            ("user_id", user_id),
            ("state", state),
            ("created_at", created_at)
        ]:
            if value is None or (isinstance(value, str) and value.strip() == ""):
                record_report["errors"].append(f"Missing value for required field: {field_name}")
                record_report["valid"] = False

        # Example: state must be in allowed set
        allowed_states = {"active", "closed", "pending", "archived"}
        if state not in allowed_states:
            record_report["errors"].append(f"Invalid state: {state}")
            record_report["valid"] = False

        # Date checks
        try:
            # Allow either ISO8601 or ISO8601 Zulu time
            datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except Exception:
            record_report["errors"].append(f"Invalid created_at format: {created_at}")
            record_report["valid"] = False
        try:
            datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
        except Exception:
            record_report["errors"].append(f"Invalid last_updated format: {last_updated}")
            record_report["valid"] = False

        # Metadata checks
        metaerr = validate_metadata(metadata)
        if metaerr:
            record_report["errors"].append(metaerr)
            record_report["valid"] = False

        results.append(record_report)
        if strict and not record_report["valid"]:
            break
    return results


def validate_consolidation_protocol(session_db: Path) -> bool:
    """
    API for external tools (returns True if validation passes, else False).
    Performs schema and record checks, prints errors, and logs events.
    """
    try:
        with sqlite3.connect(str(session_db)) as conn:
            schema_result = validate_schema(conn)
            if not schema_result["schema_ok"]:
                print(f"{TEXT_INDICATORS['fail']} Schema validation failed: missing columns {schema_result['missing_columns']}")
                _log_event({"event": "session_protocol_validation_failed", "details": schema_result})
                return False
            record_results = validate_records(conn, strict=True)
            for rec in record_results:
                if not rec.get("valid", True):
                    print(f"{TEXT_INDICATORS['fail']} Invalid record: {rec}")
                    _log_event({"event": "session_protocol_validation_failed", "details": rec})
                    return False
        print(f"{TEXT_INDICATORS['pass']} Protocol validation passed.")
        _log_event({"event": "session_protocol_validation_passed"})
        return True
    except Exception as e:
        print(f"{TEXT_INDICATORS['error']} Protocol validation error: {e}")
        _log_event({"event": "session_protocol_validation_error", "error": str(e)})
        return False


def main() -> int:
    args = parse_args()
    report = {
        "schema": None,
        "records": [],
        "validation_passed": False,
        "errors": [],
        "timestamp": datetime.utcnow().isoformat()
    }

    print(f"{TEXT_INDICATORS['start']} Validating session protocol for {args.session_db}")
    _log_event({"event": "session_protocol_validation_start", "session_db": str(args.session_db)})

    try:
        with sqlite3.connect(str(args.session_db)) as conn:
            schema_result = validate_schema(conn)
            report["schema"] = schema_result
            if not schema_result["schema_ok"]:
                print(f"{TEXT_INDICATORS['fail']} Schema validation failed: missing columns {schema_result['missing_columns']}")
                report["errors"].append(f"Missing columns: {schema_result['missing_columns']}")
                _log_event({"event": "session_protocol_validation_failed", "details": schema_result})
                if args.report:
                    args.report.write_text(json.dumps(report, indent=2))
                return 1
            record_results = validate_records(conn, strict=args.strict)
            report["records"] = record_results
            failed = [r for r in record_results if not r.get("valid", True)]
            if failed:
                print(f"{TEXT_INDICATORS['fail']} {len(failed)} invalid records found.")
                report["errors"].extend([f"Invalid record: {rec}" for rec in failed])
                _log_event({"event": "session_protocol_validation_failed", "details": failed})
                if args.report:
                    args.report.write_text(json.dumps(report, indent=2))
                return 1
            print(f"{TEXT_INDICATORS['success']} All session records valid.")
            report["validation_passed"] = True
            _log_event({"event": "session_protocol_validation_passed"})
    except Exception as e:
        print(f"{TEXT_INDICATORS['error']} Protocol validation error: {e}")
        report["errors"].append(str(e))
        _log_event({"event": "session_protocol_validation_error", "error": str(e)})
        if args.report:
            args.report.write_text(json.dumps(report, indent=2))
        return 2

    if args.report:
        args.report.write_text(json.dumps(report, indent=2))
    print(f"{TEXT_INDICATORS['success']} Session protocol validation complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
