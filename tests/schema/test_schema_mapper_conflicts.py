import pytest

import src.schema as schema
from src.schema.schema_mapper import SchemaMapper


def test_merge_resolution(caplog):
    base = {"a": {"x": 1}, "b": 2}
    mapper = SchemaMapper(base)
    updates = {"a": {"y": 2}, "b": 3}
    with caplog.at_level("INFO"):
        result = mapper.apply(updates, strategy="merge")
    assert result == {"a": {"x": 1, "y": 2}, "b": 2}
    assert "Merged 'a'" in caplog.text
    assert "Merge skipped for 'b'" in caplog.text


def test_overwrite_resolution(caplog):
    base = {"a": {"x": 1}, "b": 2}
    mapper = SchemaMapper(base)
    updates = {"a": {"y": 2}, "b": 3}
    with caplog.at_level("INFO"):
        result = mapper.apply(updates, strategy="overwrite")
    assert result == {"a": {"y": 2}, "b": 3}
    assert "Overwrote 'a'" in caplog.text
    assert "Overwrote 'b'" in caplog.text


def test_manual_resolution_triggers_rollback(monkeypatch, caplog):
    base = {"a": 1}
    mapper = SchemaMapper(base)
    updates = {"a": 2}
    called = {}

    def fake_rollback():
        called["done"] = True

    monkeypatch.setattr(schema, "rollback", fake_rollback)
    with caplog.at_level("INFO"), pytest.raises(ValueError):
        mapper.apply(updates, strategy="manual")
    assert mapper.schema == {"a": 1}
    assert called.get("done")
    assert "Manual resolution required" in caplog.text


def test_mismatch_detection(caplog):
    base = {"a": 1}
    mapper = SchemaMapper(base)
    updates = {"a": {"x": 1}}
    with caplog.at_level("INFO"):
        result = mapper.apply(updates, strategy="merge")
    assert result == {"a": 1}
    assert "Schema mismatch for 'a'" in caplog.text
    assert "Merge skipped for 'a'" in caplog.text
