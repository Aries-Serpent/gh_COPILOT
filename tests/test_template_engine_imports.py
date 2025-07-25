import os
from pathlib import Path

import pytest

import template_engine


def test_lazy_imports():
    os.environ["GH_COPILOT_WORKSPACE"] = str(Path.cwd())
    assert hasattr(template_engine, "auto_generator")
    assert hasattr(template_engine, "template_synchronizer")
    assert hasattr(template_engine, "_log_event")


def test_invalid_attribute():
    with pytest.raises(AttributeError):
        getattr(template_engine, "missing_attr")
