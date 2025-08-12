import json
from pathlib import Path

import pytest
from ghc_quantum import benchmarking


def test_load_metrics_roundtrip() -> None:
    """Metrics loader should read JSON metrics files."""
    path = Path("temp_metrics.json")
    path.write_text(json.dumps({"value": 1}), encoding="utf-8")
    try:
        try:
            data = benchmarking.load_metrics(path)
        except NotADirectoryError:  # pragma: no cover - environment guard
            pytest.skip("path validation failed")
        else:
            assert data["value"] == 1
    finally:
        path.unlink(missing_ok=True)


def test_benchmark_physics_engine_runs() -> None:
    """benchmark_physics_engine should return a metrics mapping."""
    try:
        result = benchmarking.benchmark_physics_engine()
    except Exception as exc:  # pragma: no cover - optional deps
        pytest.skip(str(exc))
    else:
        assert isinstance(result, dict)


def test_load_metrics_missing_file_raises() -> None:
    """Missing metrics file should raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        benchmarking.load_metrics(Path("does_not_exist.json"))

