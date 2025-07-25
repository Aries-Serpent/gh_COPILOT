import importlib
import os
import sys
from pathlib import Path

os.environ.setdefault("GH_COPILOT_DISABLE_VALIDATION", "1")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

MODULES = [
    "auto_generator",
    "db_first_code_generator",
    "log_utils",
    "objective_similarity_scorer",
    "pattern_clustering_sync",
    "pattern_mining_engine",
    "placeholder_utils",
    "template_placeholder_remover",
    "template_synchronizer",
    "workflow_enhancer",
]

@pytest.mark.parametrize("mod", MODULES)
def test_submodule_import(mod):
    module = importlib.import_module(f"template_engine.{mod}")
    assert module is not None

