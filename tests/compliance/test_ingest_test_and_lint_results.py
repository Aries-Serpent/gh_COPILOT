import json
import os
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch
import sys
import types

# Provide minimal stubs for heavy optional dependencies before importing target module
sys.modules.setdefault("sklearn", types.ModuleType("sklearn"))
sys.modules.setdefault("sklearn.ensemble", types.ModuleType("sklearn.ensemble"))
setattr(sys.modules["sklearn.ensemble"], "IsolationForest", object)
sys.modules.setdefault("sklearn.cluster", types.ModuleType("sklearn.cluster"))
setattr(sys.modules["sklearn.cluster"], "KMeans", object)
sys.modules.setdefault("sklearn.datasets", types.ModuleType("sklearn.datasets"))
setattr(sys.modules["sklearn.datasets"], "make_classification", object)
setattr(sys.modules["sklearn.datasets"], "make_blobs", object)
sys.modules.setdefault("sklearn.model_selection", types.ModuleType("sklearn.model_selection"))
setattr(sys.modules["sklearn.model_selection"], "train_test_split", object)
sys.modules.setdefault("sklearn.preprocessing", types.ModuleType("sklearn.preprocessing"))
setattr(sys.modules["sklearn.preprocessing"], "StandardScaler", object)
setattr(sys.modules["sklearn.preprocessing"], "LabelEncoder", object)
sys.modules.setdefault("sklearn.metrics", types.ModuleType("sklearn.metrics"))
setattr(sys.modules["sklearn.metrics"], "accuracy_score", object)
setattr(sys.modules["sklearn.metrics"], "silhouette_score", object)
sys.modules.setdefault("sklearn.metrics.pairwise", types.ModuleType("sklearn.metrics.pairwise"))
setattr(sys.modules["sklearn.metrics.pairwise"], "cosine_similarity", object)
setattr(sys.modules["sklearn.metrics.pairwise"], "pairwise_distances", object)
sys.modules.setdefault("sklearn.neural_network", types.ModuleType("sklearn.neural_network"))
setattr(sys.modules["sklearn.neural_network"], "MLPClassifier", object)
sys.modules.setdefault("sklearn.linear_model", types.ModuleType("sklearn.linear_model"))
setattr(sys.modules["sklearn.linear_model"], "LogisticRegression", object)
sys.modules.setdefault("sklearn.feature_extraction", types.ModuleType("sklearn.feature_extraction"))
sys.modules.setdefault(
    "sklearn.feature_extraction.text", types.ModuleType("sklearn.feature_extraction.text")
)
setattr(
    sys.modules["sklearn.feature_extraction.text"], "TfidfVectorizer", object
)

import pytest

from scripts.ingest_test_and_lint_results import _db, _ensure_db_path, ingest


@pytest.fixture
def temp_workspace():
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def sample_ruff_data():
    return [{"code": "F401"}, {"code": "E302"}]


@pytest.fixture
def sample_pytest_data():
    return {"summary": {"total": 25, "passed": 20, "failed": 3}}


class TestDatabaseFunction:
    def test_db_default_workspace(self):
        with patch.dict(os.environ, {"GH_COPILOT_WORKSPACE": "/test/workspace"}):
            assert str(_db()) == "/test/workspace/databases/analytics.db"

    def test_db_explicit_workspace(self):
        assert str(_db("/custom/workspace")) == "/custom/workspace/databases/analytics.db"

    def test_db_fallback_cwd(self, monkeypatch):
        monkeypatch.delenv("GH_COPILOT_WORKSPACE", raising=False)
        monkeypatch.setattr(Path, "cwd", lambda: Path("/current/dir"))
        assert str(_db()) == "/current/dir/databases/analytics.db"

    def test_ensure_db_path_creates_file(self, temp_workspace):
        db_path = _db(str(temp_workspace))
        assert not db_path.exists()
        _ensure_db_path(db_path)
        assert db_path.exists()


class TestIngest:
    def test_ingest_creates_db_and_inserts_metrics(
        self, temp_workspace, sample_ruff_data, sample_pytest_data
    ):
        ruff_json = temp_workspace / "ruff_report.json"
        ruff_json.write_text(json.dumps(sample_ruff_data), encoding="utf-8")
        pytest_json = temp_workspace / ".report.json"
        pytest_json.write_text(json.dumps(sample_pytest_data), encoding="utf-8")

        row_id = ingest(str(temp_workspace))
        assert row_id > 0

        analytics_db = temp_workspace / "databases" / "analytics.db"
        with sqlite3.connect(analytics_db) as conn:
            row = conn.execute(
                "SELECT ruff_issues, tests_passed, tests_total, placeholders_open, placeholders_resolved "
                "FROM compliance_metrics_history WHERE id=?",
                (row_id,),
            ).fetchone()
        assert row == (2, 20, 25, 0, 0)

    def test_ingest_handles_missing_files(self, temp_workspace):
        row_id = ingest(str(temp_workspace))
        assert row_id > 0
        analytics_db = temp_workspace / "databases" / "analytics.db"
        with sqlite3.connect(analytics_db) as conn:
            row = conn.execute(
                "SELECT ruff_issues, tests_passed, tests_total FROM compliance_metrics_history WHERE id=?",
                (row_id,),
            ).fetchone()
        assert row == (0, 0, 0)

    def test_ingest_malformed_json(self, temp_workspace):
        (temp_workspace / "ruff_report.json").write_text("{bad json", encoding="utf-8")
        (temp_workspace / ".report.json").write_text("{bad json", encoding="utf-8")
        row_id = ingest(str(temp_workspace))
        assert row_id > 0
        analytics_db = temp_workspace / "databases" / "analytics.db"
        with sqlite3.connect(analytics_db) as conn:
            row = conn.execute(
                "SELECT ruff_issues, tests_passed, tests_total FROM compliance_metrics_history WHERE id=?",
                (row_id,),
            ).fetchone()
        assert row == (0, 0, 0)

    def test_ingest_custom_paths(
        self, temp_workspace, sample_ruff_data, sample_pytest_data
    ):
        custom_ruff = temp_workspace / "custom_ruff.json"
        custom_pytest = temp_workspace / "custom_pytest.json"
        custom_ruff.write_text(json.dumps(sample_ruff_data), encoding="utf-8")
        custom_pytest.write_text(json.dumps(sample_pytest_data), encoding="utf-8")
        row_id = ingest(
            str(temp_workspace), ruff_json=custom_ruff, pytest_json=custom_pytest
        )
        assert row_id > 0
        analytics_db = temp_workspace / "databases" / "analytics.db"
        with sqlite3.connect(analytics_db) as conn:
            row = conn.execute(
                "SELECT ruff_issues, tests_passed, tests_total FROM compliance_metrics_history WHERE id=?",
                (row_id,),
            ).fetchone()
        assert row == (2, 20, 25)

