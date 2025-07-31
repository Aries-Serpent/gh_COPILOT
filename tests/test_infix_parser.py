import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest


def build_module() -> Path:
    project_dir = Path(__file__).resolve().parents[1] / "enterprise_modules" / "rust_extensions" / "infix_parser"
    env = os.environ.copy()
    env["PYO3_PYTHON"] = sys.executable
    subprocess.run(
        ["cargo", "build", "--manifest-path", str(project_dir / "Cargo.toml")],
        cwd=project_dir,
        env=env,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if sys.platform.startswith("linux"):
        lib_name = "libinfix_parser.so"
    elif sys.platform == "darwin":
        lib_name = "libinfix_parser.dylib"
    else:
        lib_name = "infix_parser.pyd"
    return project_dir / "target" / "debug" / lib_name


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("infix_parser", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def infix_parser_module():
    path = build_module()
    return load_module(path)


def test_simple_expression(infix_parser_module):
    res = infix_parser_module.parse_infix("1 + 2 * 3")
    assert res == {"type": "Number", "value": 7.0}


def test_parentheses(infix_parser_module):
    res = infix_parser_module.parse_infix("(2 + 3) * 4")
    assert res == {"type": "Number", "value": 20.0}
