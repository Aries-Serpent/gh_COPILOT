from pathlib import Path

from scripts.monitoring import performance_analyzer as pa


def test_analyze_trend() -> None:
    assert pa.analyze_trend([1.0, 3.0]) == 2.0


def test_threshold_breach_exit(tmp_path: Path) -> None:
    metrics = tmp_path / "metrics.txt"
    metrics.write_text("10\n90\n")
    code = pa.main(["--metric-file", str(metrics), "--threshold", "80"])
    assert code == 1

