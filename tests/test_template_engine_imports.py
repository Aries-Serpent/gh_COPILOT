from pathlib import Path

import pytest

MODULES = [
    "template_engine",
    "template_engine.auto_generator",
    "template_engine.db_first_code_generator",
    "template_engine.log_utils",
    "template_engine.objective_similarity_scorer",
    "template_engine.pattern_clustering_sync",
    "template_engine.pattern_mining_engine",
    "template_engine.placeholder_utils",
    "template_engine.template_placeholder_remover",
    "template_engine.template_synchronizer",
    "template_engine.workflow_enhancer",
]


@pytest.mark.parametrize("module", MODULES)
def test_import(module):
    """Ensure module path exists."""
    parts = module.split(".")
    if len(parts) == 1:
        path = Path(parts[0])
    else:
        path = Path(parts[0]) / f"{parts[1]}.py"
    assert path.exists()
