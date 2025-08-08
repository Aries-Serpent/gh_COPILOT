import pytest

import src.schema as schema
from src.schema.schema_mapper import SchemaMapper


def test_merge_records_decision(caplog):
    base = {"a": {"x": 1}}
    mapper = SchemaMapper(base)
    updates = {"a": {"x": 2, "y": 3}}
    with caplog.at_level("INFO"):
        result = mapper.apply(updates, strategy="merge")
    assert result == {"a": {"x": 1, "y": 3}}
    assert ("a.x", "merge") in mapper.decisions
    assert "Merge skipped for 'a.x'; keeping original" in caplog.text


def test_overwrite_records_decision(caplog):
    base = {"a": {"x": 1}}
    mapper = SchemaMapper(base)
    updates = {"a": {"x": 2}}
    with caplog.at_level("INFO"):
        result = mapper.apply(updates, strategy="overwrite")
    assert result == {"a": {"x": 2}}
    assert ("a.x", "overwrite") in mapper.decisions
    assert "Overwrote 'a.x'" in caplog.text


def test_manual_triggers_rollback(monkeypatch, caplog):
    base = {"a": {"x": 1}}
    mapper = SchemaMapper(base)
    updates = {"a": {"x": 2}}
    called = {}

    def fake_rollback():
        called["done"] = True
        return base

    monkeypatch.setattr(schema, "rollback", fake_rollback)
    with caplog.at_level("INFO"), pytest.raises(ValueError):
        mapper.apply(updates, strategy="manual")
    assert mapper.schema == {"a": {"x": 1}}
    assert ("a.x", "manual") in mapper.decisions
    assert called.get("done")
    assert "Manual resolution required for 'a.x'" in caplog.text
