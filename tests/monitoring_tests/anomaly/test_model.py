import sys
from pathlib import Path

# Ensure repository root is on the import path to avoid conflicts with external
# packages named `ghc_monitoring`.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from ghc_monitoring.anomaly import StatisticalAnomalyDetector


def test_detects_synthetic_anomaly():
    model = StatisticalAnomalyDetector(threshold=2.0)
    model.train()
    results = model.detect([10, 12, 30])
    assert results == [False, False, True]
