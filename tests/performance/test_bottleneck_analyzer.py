from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_analyzer() -> object:
    path = Path("scripts/performance/bottleneck_analyzer.py")
    spec = importlib.util.spec_from_file_location("bottleneck_analyzer", path)
    module = importlib.util.module_from_spec(spec)
    argv_backup = sys.argv.copy()
    sys.argv = [str(path)]
    try:
        spec.loader.exec_module(module)  # type: ignore[attr-defined]
    finally:
        sys.argv = argv_backup
    return module


def test_discover_targets(tmp_path):
    (tmp_path / "alpha.py").write_text("def foo():\n    return 'foo'\n")
    (tmp_path / "beta.py").write_text(
        "def bar():\n    return 'bar'\n\n" "def baz(x):\n    return x\n"
    )
    analyzer = load_analyzer()
    targets = analyzer.discover_targets(tmp_path)
    names = {name for name, _ in targets}
    assert "alpha:foo" in names
    assert "beta:bar" in names
    assert "beta:baz" not in names

