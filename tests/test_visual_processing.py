import ast
from pathlib import Path

import pytest

HELPERS = {"start_indicator", "progress_bar", "end_indicator"}


@pytest.mark.parametrize("script", [Path("scripts/utilities/unified_script_generation_system.py")])
def test_visual_helpers_present(script: Path) -> None:
    tree = ast.parse(script.read_text())
    calls = {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    missing = HELPERS - calls
    assert not missing, f"Missing visual helper calls: {missing}"
