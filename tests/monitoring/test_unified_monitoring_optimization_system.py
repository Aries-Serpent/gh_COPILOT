import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "monitoring.unified_monitoring_optimization_system",
    Path(__file__).resolve().parents[2]
    / "src/monitoring/unified_monitoring_optimization_system.py",
)
umos = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(umos)  # type: ignore[arg-type]


def test_anomaly_detection_triggers_auto_heal(monkeypatch, tmp_path) -> None:
    def fake_collect(**_):
        return {"x": 1.0}

    def fake_detect(history, **_):
        assert history
        return [{"anomaly_score": 0.9}]

    called = {}

    def fake_auto_heal_session(anomalies, **kwargs):  # type: ignore[override]
        called["anomalies"] = anomalies
        called["kwargs"] = kwargs

    monkeypatch.setattr(umos, "collect_metrics", fake_collect)
    monkeypatch.setattr(umos, "detect_anomalies", fake_detect)
    monkeypatch.setattr(umos, "auto_heal_session", fake_auto_heal_session)

    db = tmp_path / "db.sqlite"
    umos.anomaly_detection_loop(interval=0, iterations=2, threshold=0.5, db_path=db)

    assert called["anomalies"][0]["anomaly_score"] > 0.5


def test_anomaly_detection_no_alert(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(umos, "collect_metrics", lambda **_: {"x": 1.0})
    monkeypatch.setattr(umos, "detect_anomalies", lambda *a, **k: [{"anomaly_score": 0.1}])
    called = False

    def fake_auto_heal_session(*_, **__):
        nonlocal called
        called = True

    monkeypatch.setattr(umos, "auto_heal_session", fake_auto_heal_session)
    db = tmp_path / "db.sqlite"
    umos.anomaly_detection_loop(interval=0, iterations=1, threshold=0.5, db_path=db)
    assert called is False


def test_detect_anomalies_failure(monkeypatch) -> None:
    def boom(*_, **__):
        raise RuntimeError("fail")

    monkeypatch.setattr(umos, "_detect_impl", boom)
    with pytest.raises(RuntimeError):
        umos.detect_anomalies([], contamination=0.2)

