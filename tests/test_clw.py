#!/usr/bin/env python3
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "clw"


def run_clw(input_bytes: bytes, max_len: int = None) -> bytes:
    env = {} if max_len is None else {"CLW_MAX_LINE_LENGTH": str(max_len)}
    proc = subprocess.run(
        ["python3", str(SCRIPT)],
        input=input_bytes,
        capture_output=True,
        env=env,
    )
    return proc.stdout


def test_no_wrap() -> None:
    line = b"hello world\n"
    out = run_clw(line)
    assert out == line


def test_wrap() -> None:
    long_line = b"a" * 1600 + b"\n"
    out = run_clw(long_line, 1550)
    assert b"\xe2\x8f\x8e\n" in out  # wrap marker
    assert out.endswith(b"\n")
