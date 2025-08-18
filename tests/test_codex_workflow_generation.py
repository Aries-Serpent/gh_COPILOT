"""Tests for code generation helpers in codex_workflow."""

from importlib import util as importlib_util

import pytest

from codex_workflow import generate_module


def _import_module_from_path(path):
    spec = importlib_util.spec_from_file_location(path.stem, path)
    module = importlib_util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore
    return module


def test_generated_function_returns_input(tmp_path):
    module_path = tmp_path / "generated_fn.py"
    generate_module(module_path, functions=["echo"], minimal=True)
    mod = _import_module_from_path(module_path)
    assert mod.echo("ping") == "ping"


def test_generated_class_raises_not_implemented(tmp_path):
    module_path = tmp_path / "generated_cls.py"
    generate_module(module_path, classes=["Worker"], minimal=False)
    mod = _import_module_from_path(module_path)
    with pytest.raises(NotImplementedError, match="Worker\.run is not implemented"):
        mod.Worker().run()


def test_generated_module_has_no_todo(tmp_path):
    module_path = tmp_path / "no_todo.py"
    generate_module(module_path, functions=["stub"], minimal=False)
    text = module_path.read_text()
    assert "TODO" not in text

