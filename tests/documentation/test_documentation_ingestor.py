import sqlite3
import sys
import types
from pathlib import Path


class _Tqdm:
    def __init__(self, *args, **kwargs) -> None:  # pragma: no cover - simple stub
        pass

    def __enter__(self):  # pragma: no cover - simple stub
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - simple stub
        return None

    def update(self, n: int) -> None:  # pragma: no cover - simple stub
        return None

    def set_description(self, *_args, **_kwargs) -> None:  # pragma: no cover - simple stub
        return None


sys.modules.setdefault("tqdm", types.SimpleNamespace(tqdm=_Tqdm))

from scripts.database import documentation_ingestor as ingestor_module
from scripts.database.documentation_ingestor import ingest_documentation


def _get_records(db_path: Path, doc_path: str):
    with sqlite3.connect(db_path) as conn:
        return list(
            conn.execute(
                "SELECT version, content_hash FROM documentation_assets WHERE doc_path=? ORDER BY version",
                (doc_path,),
            )
        )


def test_ingest_creates_new_version_for_updated_content(tmp_path, monkeypatch):
    docs_dir = tmp_path / "documentation"
    docs_dir.mkdir()
    (tmp_path / "databases").mkdir()

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setattr(ingestor_module, "enforce_anti_recursion", lambda ctx: None)
    monkeypatch.setattr(ingestor_module, "validate_enterprise_operation", lambda: True)
    monkeypatch.setattr(
        ingestor_module.SecondaryCopilotValidator,
        "validate_corrections",
        lambda self, paths: None,
    )

    doc = docs_dir / "example.md"
    doc.write_text("first", encoding="utf-8")
    ingest_documentation(tmp_path)

    doc.write_text("second", encoding="utf-8")
    ingest_documentation(tmp_path)

    db_path = tmp_path / "databases" / "enterprise_assets.db"
    records = _get_records(db_path, str(doc.relative_to(tmp_path)))
    assert len(records) == 2
    assert records[0][0] == 1
    assert records[1][0] == 2
    assert records[0][1] != records[1][1]


def test_ingest_does_not_duplicate_when_unchanged(tmp_path, monkeypatch):
    docs_dir = tmp_path / "documentation"
    docs_dir.mkdir()
    (tmp_path / "databases").mkdir()

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setattr(ingestor_module, "enforce_anti_recursion", lambda ctx: None)
    monkeypatch.setattr(ingestor_module, "validate_enterprise_operation", lambda: True)
    monkeypatch.setattr(
        ingestor_module.SecondaryCopilotValidator,
        "validate_corrections",
        lambda self, paths: None,
    )

    doc = docs_dir / "example.md"
    doc.write_text("same", encoding="utf-8")
    ingest_documentation(tmp_path)
    ingest_documentation(tmp_path)

    db_path = tmp_path / "databases" / "enterprise_assets.db"
    records = _get_records(db_path, str(doc.relative_to(tmp_path)))
    assert len(records) == 1
    assert records[0][0] == 1
