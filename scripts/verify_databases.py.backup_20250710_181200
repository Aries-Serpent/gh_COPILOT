"""Verify all .db files in databases/ have expected new tables and indexe"s""."""

import sqlite3
from datetime import datetime
from pathlib import Path
from tqdm import tqdm


def validate_db(path: Path, expected: set) -> dict:
  " "" """Return missing tables or indexes in this D"B""."""
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    query "="" "SELECT name FROM sqlite_maste"r"" """ "WHERE type IN" ""('tab'l''e''','ind'e''x''')"
    cur.execute(query)
    existing = {r[0] for r in cur.fetchall()}
    conn.close()
    return" ""{"missi"n""g": expected - existing","" "ext"r""a": existing - expected}


def main():
    start = datetime.now()
    # Use path relative to repo root
    db_dir = Path(__file__).resolve().parents[1] "/"" "databas"e""s"
    # expected new objects per recent updates
    expectations = {
       },
          " "" "enhanced_script_tracking."d""b": {},
          " "" "consolidation_tracking."d""b": {},
          " "" "optimization_metrics."d""b":" ""{"optimization_metri"c""s"},
          " "" "cleanup_actions."d""b":" ""{"cleanup_actio"n""s"},
            # add other DB: expected_tables...
            }
            results = {}
            for db in tqdm(list(db_dir.glo"b""("*."d""b")), des"c""="Checking D"B""s"):
        exp = expectations.get(db.name, set())
        if exp:
            results[db.name] = validate_db(db, exp)
            duration = (datetime.now() - start).total_seconds()
            print"(""f"\n\u2705 Verification completed in {duration:.2f"}""s")
            for db, res in results.items():
        print"(""f"{db}: missing={re"s""['missi'n''g']} extra={re's''['ext'r''a'']''}")


            if __name__ ="="" "__main"_""_":
    main()"
""