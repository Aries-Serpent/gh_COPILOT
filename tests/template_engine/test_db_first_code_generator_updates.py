"""Tests for updated DB-first code generator features."""

import os
import sqlite3
from pathlib import Path

import pytest
import sys
import types

os.environ.setdefault("GH_COPILOT_DISABLE_VALIDATION", "1")

# Stub out heavy quantum dependency
qiskit_mod = types.ModuleType("qiskit")
circuit_mod = types.ModuleType("circuit")
library_mod = types.ModuleType("library")
library_mod.QFT = object
circuit_mod.library = library_mod
qi_mod = types.ModuleType("quantum_info")
qi_mod.Statevector = object
qiskit_mod.QuantumCircuit = object
qiskit_mod.circuit = circuit_mod
qiskit_mod.quantum_info = qi_mod
sys.modules["qiskit"] = qiskit_mod
sys.modules["qiskit.circuit"] = circuit_mod
sys.modules["qiskit.circuit.library"] = library_mod
sys.modules["qiskit.quantum_info"] = qi_mod
sys.modules["qiskit_aer"] = types.ModuleType("qiskit_aer")
sys.modules["qiskit_aer"].AerSimulator = object

dashboard_mod = types.ModuleType("dashboard")
cmu_mod = types.ModuleType("compliance_metrics_updater")
class ComplianceMetricsUpdater: ...
cmu_mod.ComplianceMetricsUpdater = ComplianceMetricsUpdater
dashboard_mod.compliance_metrics_updater = cmu_mod
sys.modules["dashboard"] = dashboard_mod
sys.modules["dashboard.compliance_metrics_updater"] = cmu_mod

tpl_remover_mod = types.ModuleType("template_placeholder_remover")
def remove_unused_placeholders(text, **_):
    return text
tpl_remover_mod.remove_unused_placeholders = remove_unused_placeholders
sys.modules["template_engine.template_placeholder_remover"] = tpl_remover_mod

tqdm_mod = types.ModuleType("tqdm")
class _TqdmStub:
    def __init__(self, iterable=None, **_kw):
        self.iterable = iterable or []

    def __iter__(self):
        return iter(self.iterable)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def update(self, *_a, **_k):
        return None

    def set_description(self, *_a, **_k):
        return None

    @staticmethod
    def write(*_a, **_k):
        return None

tqdm_mod.tqdm = _TqdmStub
sys.modules["tqdm"] = tqdm_mod
import utils.progress as _progress
_progress.tqdm = _TqdmStub
import utils.log_utils as _log_utils
_log_utils.tqdm = _TqdmStub

from template_engine.db_first_code_generator import TemplateAutoGenerator
from template_engine import db_first_code_generator
db_first_code_generator._log_event = lambda *a, **k: None


def test_load_templates_prefers_database(tmp_path: Path) -> None:
    completion_db = tmp_path / "templates.db"
    production_db = tmp_path / "production.db"
    analytics_db = tmp_path / "analytics.db"

    with sqlite3.connect(completion_db) as conn:
        conn.execute("CREATE TABLE templates (template_content TEXT)")
        conn.execute("INSERT INTO templates (template_content) VALUES ('db_template')")

    with sqlite3.connect(production_db) as conn:
        conn.execute("CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)")
        conn.execute("INSERT INTO code_templates (template_code) VALUES ('prod_template')")

    gen = TemplateAutoGenerator(
        analytics_db=analytics_db,
        completion_db=completion_db,
        production_db=production_db,
    )
    assert gen.templates == ["db_template"]


def test_cluster_patterns_logs_quantum_score(tmp_path: Path, monkeypatch) -> None:
    analytics_db = tmp_path / "analytics.db"
    gen = TemplateAutoGenerator(
        analytics_db=analytics_db,
        completion_db=tmp_path / "templates.db",
        production_db=tmp_path / "production.db",
    )
    gen.templates = ["alpha", "beta"]
    calls = []
    monkeypatch.setattr(
        db_first_code_generator,
        "quantum_cluster_score",
        lambda m: calls.append(m) or 0.5,
    )
    events: list[dict] = []
    monkeypatch.setattr(db_first_code_generator, "_log_event", lambda data, **_: events.append(data))
    gen._cluster_patterns()
    assert calls
    assert any(e.get("event") == "quantum_cluster_score" for e in events)


def test_rank_templates_logs_duration(tmp_path: Path, monkeypatch) -> None:
    prod_db = tmp_path / "production.db"
    with sqlite3.connect(prod_db) as conn:
        conn.execute("CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)")
        conn.execute("INSERT INTO code_templates (template_code) VALUES ('foo')")
        conn.execute("INSERT INTO code_templates (template_code) VALUES ('bar')")

    gen = TemplateAutoGenerator(
        analytics_db=tmp_path / "analytics.db",
        completion_db=tmp_path / "templates.db",
        production_db=prod_db,
    )

    monkeypatch.setattr(
        db_first_code_generator,
        "compute_similarity_scores",
        lambda *_, **__: [(1, 0.1), (2, 0.2)],
    )
    events: list[dict] = []
    monkeypatch.setattr(db_first_code_generator, "_log_event", lambda data, **_: events.append(data))
    gen.rank_templates("foo")
    assert any(e.get("event") == "rank_duration" for e in events)


def test_pre_query_similarity_called(tmp_path: Path, monkeypatch) -> None:
    prod_db = tmp_path / "production.db"
    with sqlite3.connect(prod_db) as conn:
        conn.execute("CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)")
        conn.execute("INSERT INTO code_templates (template_code) VALUES ('tmpl')")
    gen = TemplateAutoGenerator(
        analytics_db=tmp_path / "analytics.db",
        completion_db=tmp_path / "templates.db",
        production_db=prod_db,
    )
    called: dict[str, bool] = {}

    def fake_scores(*_, **__):
        called["hit"] = True
        return [(1, 0.5)]

    monkeypatch.setattr(db_first_code_generator, "compute_similarity_scores", fake_scores)
    gen._pre_query_checks("goal")
    assert called.get("hit")



