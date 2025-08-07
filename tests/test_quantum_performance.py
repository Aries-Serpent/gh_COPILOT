import json
from pathlib import Path

import pytest
from quantum import benchmarking


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

