from src.monitoring.anomaly import StatisticalAnomalyDetector


def test_detects_synthetic_anomaly():
    model = StatisticalAnomalyDetector(threshold=2.0)
    model.train()
    results = model.detect([10, 12, 30])
    assert results == [False, False, True]
