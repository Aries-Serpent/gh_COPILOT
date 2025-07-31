import logging
from scripts import DATABASE_REDUNDANCY_ANALYZER as dra
from scripts import FINAL_PRODUCTION_COMPLETER as fpc


def test_database_redundancy_validation(monkeypatch, tmp_path):
    called = {"validate": False}

    class DummyValidator:
        def __init__(self, logger=None):
            pass

        def validate_corrections(self, files):
            called["validate"] = True
            return True

    def dummy_init(self, database_path="production.db"):
        self.database_path = tmp_path / "db.db"
        self.logger = logging.getLogger(__name__)

    monkeypatch.setattr(dra, "SecondaryCopilotValidator", DummyValidator)
    monkeypatch.setattr(dra.EnterpriseDatabaseProcessor, "__init__", dummy_init)

    assert dra.main() is True
    assert called["validate"]


def test_final_production_validation(monkeypatch):
    called = {"validate": False}

    class DummyValidator:
        def __init__(self, logger=None):
            pass

        def validate_corrections(self, files):
            called["validate"] = True
            return True

    class DummyUtility:
        def __init__(self, workspace_path="e:/gh_COPILOT"):
            pass

        def execute_utility(self) -> bool:
            return True

    monkeypatch.setattr(fpc, "SecondaryCopilotValidator", DummyValidator)
    monkeypatch.setattr(fpc, "EnterpriseUtility", DummyUtility)

    assert fpc.main() is True
    assert called["validate"]
