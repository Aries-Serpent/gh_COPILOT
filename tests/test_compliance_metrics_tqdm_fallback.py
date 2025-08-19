import builtins
import importlib
import sys
import types


def test_tqdm_fallback(monkeypatch, tmp_path):
    # Simulate tqdm not being installed
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "tqdm":
            raise ImportError("tqdm missing")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    sys.modules.pop("tqdm", None)

    # Stub heavy orchestrator dependency to avoid optional extras
    stub_dual = types.SimpleNamespace(
        DualCopilotOrchestrator=type("Dummy", (), {"__init__": lambda self, *a, **k: None})
    )
    sys.modules["scripts.validation.dual_copilot_orchestrator"] = stub_dual

    cmu = importlib.reload(importlib.import_module("dashboard.compliance_metrics_updater"))

    # Patch dependencies to keep the update lightweight
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setattr(cmu, "ANALYTICS_DB", tmp_path / "analytics.db")
    monkeypatch.setattr(cmu, "ensure_tables", lambda *a, **k: None)
    monkeypatch.setattr(cmu, "insert_event", lambda *a, **k: None)
    monkeypatch.setattr(cmu, "validate_enterprise_operation", lambda *a, **k: None)
    monkeypatch.setattr(cmu, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(cmu, "validate_environment_root", lambda: None)
    monkeypatch.setattr(cmu, "CorrectionLoggerRollback", lambda *a, **k: types.SimpleNamespace())
    monkeypatch.setattr(
        cmu.ComplianceMetricsUpdater,
        "_fetch_compliance_metrics",
        lambda self, test_mode=False: {},
    )
    monkeypatch.setattr(
        cmu.ComplianceMetricsUpdater,
        "_cognitive_compliance_suggestion",
        lambda self, metrics: "ok",
    )

    updater = cmu.ComplianceMetricsUpdater(tmp_path / "dashboard", test_mode=True)

    # Ensure no-op tqdm behaves as context manager
    with cmu.tqdm(total=1) as pbar:
        pbar.set_description("noop")
        pbar.update(1)

    updater.update(simulate=True)
    assert updater.status == "COMPLETED"
