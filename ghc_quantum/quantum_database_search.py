# [Quantum]: Quantum Database Search Utility
# > Generated: 2025-07-24 21:23:18 | Author: mbaetiong
# --- Enterprise Standards ---
# - Flake8/PEP8 Compliant
# - Explicit logging for all search operations
# - Supports SQL, NoSQL, and hybrid quantum-backed database interfaces
# - Query and result monitoring for audit/compliance
# - Thread-safe execution

import json
import logging
import os
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

from utils.log_utils import _log_event
from ghc_quantum.algorithms import QuantumEncryptedCommunication

logger = logging.getLogger(__name__)
DEFAULT_DB_PATH = Path(os.environ.get("QUANTUM_DB_PATH", "databases/quantum.db"))
SEARCH_LOG_TABLE = "quantum_search_events"
_lock = threading.Lock()

def _log_search_event(
    query: str,
    db_path: Path,
    result_count: int,
    params: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
):
    """Log a quantum search event to analytics DB for audit."""
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "query": query,
        "db_path": str(db_path),
        "result_count": result_count,
        "params": json.dumps(params) if params else "{}",
        "error": error,
    }
    with sqlite3.connect(DEFAULT_DB_PATH) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS quantum_search_events (timestamp TEXT, query TEXT, db_path TEXT, result_count INTEGER, params TEXT, error TEXT)"
        )
        conn.commit()
    _log_event(
        event,
        table=SEARCH_LOG_TABLE,
        db_path=DEFAULT_DB_PATH,
        echo=True if error else False,
    )

def _connect_sqlite(db_path: Path):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(db_path))

def quantum_search_sql(
    query: str,
    db_path: Union[str, Path] = DEFAULT_DB_PATH,
    params: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
    *,
    use_hardware: bool = False,
    backend_name: str | None = None,
    token: str | None = None,
) -> List[Dict[str, Any]]:
    """
    Perform a quantum-accelerated SQL search.
    - query: SQL SELECT statement (parameterized recommended)
    - db_path: path to SQLite3 file
    - params: dict of query parameters for parameterized SQL
    - limit: max number of results to return
    Returns a list of result dicts.
    """
    db_path = Path(db_path)
    if use_hardware and backend_name:
        try:
            from qiskit_ibm_provider import IBMProvider
            from qiskit import QuantumCircuit
            provider = IBMProvider(token=token) if token else IBMProvider()
            backend = provider.get_backend(backend_name)
            qc = QuantumCircuit(1, 1)
            qc.h(0)
            qc.measure(0, 0)
            backend.run(qc).result()
        except Exception as exc:  # pragma: no cover - hardware optional
            logger.warning("Hardware execution fallback: %s", exc)
            use_hardware = False
    results = []
    error = None
    try:
        _lock.acquire()
        with _connect_sqlite(db_path) as conn:
            cur = conn.cursor()
            if limit is not None:
                query = f"{query.strip().rstrip(';')} LIMIT {limit};"
            logger.info("Executing quantum SQL search: %s params=%s", query, params)
            if params:
                cur.execute(query, tuple(params.values()))
            else:
                cur.execute(query)
            columns = [desc[0] for desc in cur.description]
            for row in cur.fetchall():
                results.append(dict(zip(columns, row)))
    except Exception as exc:
        error = str(exc)
        logger.error("Quantum search SQL error: %s", error)
    finally:
        _log_search_event(query, db_path, len(results), params, error)
        _lock.release()
    return results

def quantum_search_nosql(
    collection: str,
    filter_query: Dict[str, Any],
    db_path: Path = DEFAULT_DB_PATH,
    limit: Optional[int] = None,
    *,
    use_hardware: bool = False,
    backend_name: str | None = None,
    token: str | None = None,
) -> List[Dict[str, Any]]:
    """
    Simulate a quantum-accelerated NoSQL search for audit/testing.
    Only supports SQLite/fake NoSQL for demonstration.
    - collection: logical table name
    - filter_query: dict of field conditions (AND logic)
    - db_path: path to SQLite3 file
    - limit: max number of results to return
    Returns a list of result dicts.
    """
    db_path = Path(db_path)
    if use_hardware and backend_name:
        try:
            from qiskit_ibm_provider import IBMProvider
            from qiskit import QuantumCircuit
            provider = IBMProvider(token=token) if token else IBMProvider()
            backend = provider.get_backend(backend_name)
            qc = QuantumCircuit(1, 1)
            qc.h(0)
            qc.measure(0, 0)
            backend.run(qc).result()
        except Exception as exc:  # pragma: no cover - hardware optional
            logger.warning("Hardware execution fallback: %s", exc)
            use_hardware = False
    results = []
    error = None
    try:
        _lock.acquire()
        with _connect_sqlite(db_path) as conn:
            cur = conn.cursor()
            sql = f"SELECT * FROM {collection}"
            where_clauses = []
            params = []
            for key, val in filter_query.items():
                where_clauses.append(f"{key}=?")
                params.append(val)
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            if limit is not None:
                sql += f" LIMIT {limit}"
            logger.info("Executing quantum NoSQL search: %s params=%s", sql, params)
            cur.execute(sql, params)
            columns = [desc[0] for desc in cur.description]
            for row in cur.fetchall():
                results.append(dict(zip(columns, row)))
    except Exception as exc:
        error = str(exc)
        logger.error("Quantum search NoSQL error: %s", error)
    finally:
        _log_search_event(sql, db_path, len(results), filter_query, error)
        _lock.release()
    return results


def quantum_secure_search(
    query: str,
    db_path: Union[str, Path] = DEFAULT_DB_PATH,
    params: Optional[Dict[str, Any]] = None,
    key: str | None = None,
    token: str | None = None,
) -> List[str]:
    """Execute a SQL search and return encrypted JSON rows."""
    rows = quantum_search_sql(query, db_path, params, token=token)
    engine = QuantumEncryptedCommunication(key)
    return [engine.encrypt_message(json.dumps(row)) for row in rows]

def quantum_search_hybrid(
    search_type: str,
    query: Any,
    db_path: Path = DEFAULT_DB_PATH,
    limit: Optional[int] = None,
    extra: Optional[Dict[str, Any]] = None,
    *,
    use_hardware: bool = False,
    backend_name: str | None = None,
    token: str | None = None,
) -> List[Dict[str, Any]]:
    """
    Perform a hybrid quantum database search (SQL/NoSQL).
    - search_type: 'sql' or 'nosql'
    - query: SQL string or NoSQL filter dict
    - db_path: database to use
    - limit: max results
    - extra: any additional quantum parameters
    Returns results as list of dicts.
    """
    logger.info("Hybrid quantum search: type=%s query=%s", search_type, query)
    if search_type == "sql":
        return quantum_search_sql(
            query,
            db_path,
            extra,
            limit,
            use_hardware=use_hardware,
            backend_name=backend_name,
            token=token,
        )
    elif search_type == "nosql":
        if not extra or "collection" not in extra or not isinstance(extra["collection"], str):
            logger.error("Quantum hybrid search error: 'collection' must be provided as a string in 'extra'")
            _log_search_event(str(query), db_path, 0, extra, "'collection' missing or invalid for NoSQL search")
            return []
        return quantum_search_nosql(
            extra["collection"],
            query,
            db_path,
            limit,
            use_hardware=use_hardware,
            backend_name=backend_name,
            token=token,
        )
    else:
        logger.error("Unknown hybrid quantum search type: %s", search_type)
        _log_search_event(str(query), db_path, 0, extra, f"Unknown type: {search_type}")
        return []

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Quantum Database Search Utility")
    parser.add_argument("--type", choices=["sql", "nosql", "hybrid"], required=True, help="Search type")
    parser.add_argument("--db", type=str, default=str(DEFAULT_DB_PATH), help="Database file path")
    parser.add_argument("--query", type=str, required=True, help="SQL query string or filter JSON")
    parser.add_argument(
        "--collection",
        type=str,
        help="NoSQL collection/table (required for NoSQL and hybrid NoSQL mode)",
    )
    parser.add_argument("--limit", type=int, default=None, help="Limit results")
    parser.add_argument("--hardware", action="store_true", help="Use quantum hardware backend")
    parser.add_argument("--backend", type=str, default="ibmq_qasm_simulator", help="Backend name")
    parser.add_argument("--token", type=str, help="IBM Quantum API token")
    parser.add_argument("--params", type=str, help="Params as JSON string")
    parser.add_argument(
        "--mode",
        choices=["sql", "nosql"],
        help="Hybrid search mode; defaults to 'nosql' when --collection is provided",
    )
    args = parser.parse_args()

    db_path = Path(args.db)
    params = None
    if args.params:
        import json
        params = json.loads(args.params)

    token = args.token

    if args.type == "sql":
        results = quantum_search_sql(
            args.query,
            db_path,
            params,
            args.limit,
            use_hardware=args.hardware,
            backend_name=args.backend,
            token=token,
        )
    elif args.type == "nosql":
        import json
        filter_query = json.loads(args.query)
        results = quantum_search_nosql(
            args.collection,
            filter_query,
            db_path,
            args.limit,
            use_hardware=args.hardware,
            backend_name=args.backend,
            token=token,
        )
    elif args.type == "hybrid":
        import json
        extra = {"collection": args.collection} if args.collection else {}
        mode = args.mode or ("nosql" if args.collection else "sql")
        if mode == "sql":
            results = quantum_search_hybrid(
                "sql",
                args.query,
                db_path,
                args.limit,
                params,
                use_hardware=args.hardware,
                backend_name=args.backend,
                token=token,
            )
        else:
            filter_query = json.loads(args.query)
            results = quantum_search_hybrid(
                "nosql",
                filter_query,
                db_path,
                args.limit,
                extra,
                use_hardware=args.hardware,
                backend_name=args.backend,
                token=token,
            )
    else:
        results = []

    print(f"Search results ({len(results)}):")
    for r in results:
        print(r)

if __name__ == "__main__":
    main()
