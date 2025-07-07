"""\U0001f50d Verify all .db files in databases/ have expected new tables/indexes."""
import sqlite3
from pathlib import Path
from tqdm import tqdm
from datetime import datetime

def validate_db(path: Path, expected: set) -> dict:
    """Return missing tables/indexes in this DB."""
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type IN ('table','index')")
    existing = {r[0] for r in cur.fetchall()}
    conn.close()
    return {"missing": expected - existing, "extra": existing - expected}

def main():
    start = datetime.now()
    # Use path relative to repo root
    db_dir = Path(__file__).resolve().parents[1] / "databases"
    # expected new objects per recent updates
    expectations = {
        "production.db": {"quantum_processing_results", "optimization_metrics"},
        "enhanced_script_tracking.db": {"enhanced_script_tracking", "script_templates"},
        "consolidation_tracking.db": {"script_generation_consolidation", "consolidation_manifest"},
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
