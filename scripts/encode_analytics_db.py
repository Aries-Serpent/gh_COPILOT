"""Utility to encode the analytics database as Base64.

This script zips ``databases/analytics.db`` and converts the zip
archive to a Base64 string using :class:`EncodeWorker` from
``misc/legacy/Base64ImageTransformer.py``. The resulting text is written
to ``databases/analytics_db_zip.b64``.
"""

from __future__ import annotations

from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from misc.legacy.Base64ImageTransformer import EncodeWorker


def encode_database() -> None:
    """Zip and encode the analytics database."""

    db_path = Path("databases/analytics.db")
    zip_path = Path("databases/analytics_db.zip")
    b64_path = Path("databases/analytics_db_zip.b64")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(db_path, arcname=db_path.name)

    result: dict[str, str] = {}
    worker = EncodeWorker(str(zip_path))
    worker.encoding_successful.connect(lambda s: result.setdefault("data", s))
    worker.encoding_failed.connect(lambda e: (_ for _ in ()).throw(RuntimeError(e)))
    worker.run_encode()

    b64_path.write_text(result["data"])


if __name__ == "__main__":
    encode_database()

