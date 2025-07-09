"""Verify all .db files in databases/ have expected new tables and indexes."""

import sqlite3
from datetime import datetime
from pathlib import Path
from tqdm import tqdm


def validate_db(path: Path, expected: set) -> dict:
    """Return missing tables or indexes in this DB."""
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    query = "SELECT name FROM sqlite_master " "WHERE type IN ('table','index')"
    cur.execute(query)
    existing = {r[0] for r in cur.fetchall()}
    conn.close()
    return {"missing": expected - existing, "extra": existing - expected}


def main():
    start = datetime.now()
    # Use path relative to repo root
    db_dir = Path(__file__).resolve().parents[1] / "databases"
    # expected new objects per recent updates
    expectations = {
       },
            "enhanced_script_tracking.db": {},
            "consolidation_tracking.db": {},
            "optimization_metrics.db": {"optimization_metrics"},
            "cleanup_actions.db": {"cleanup_actions"},
            # add other DB: expected_tables...
            }
            results = {}
            for db in tqdm(list(db_dir.glob("*.db")), desc="Checking DBs"):
        exp = expectations.get(db.name, set())
        if exp:
            results[db.name] = validate_db(db, exp)
            duration = (datetime.now() - start).total_seconds()
            print(f"\n\u2705 Verification completed in {duration:.2f}s")
            for db, res in results.items():
        print(f"{db}: missing={res['missing']} extra={res['extra']}")


            if __name__ == "__main__":
    main()
