import io
import os
import sys

import pytest

from tools.output_pattern_chunker import OutputPatternChunker, process_shell_output


@pytest.mark.parametrize(
    "line,pattern",
    [
        ("\x1b[31m" + "a" * 40 + "\x1b[0m", "ansi"),
        ('{"k": "' + "a" * 40 + '"}', "json"),
        (",".join(str(i) for i in range(30)), "csv"),
        ("def f():" + " pass" * 20, "code"),
        ("diff --git a/b b/b" + " a" * 20, "git"),
    ],
)
def test_pattern_detection(line, pattern):
    chunker = OutputPatternChunker(max_line_length=20)
    assert chunker.detect_pattern(line) == pattern


def test_csv_chunking_preserves_fields():
    line = ",".join(str(i) for i in range(30))
    chunker = OutputPatternChunker(max_line_length=20)
    chunks = [c for c, _ in chunker.chunk_line(line)]
    assert all(len(c) <= 20 for c in chunks)
    assert ",".join(chunks) == line


def test_process_shell_output_creates_temp_file(monkeypatch):
    long_line = "a" * 100
    stdin = io.StringIO(long_line + "\n")
    stdout = io.StringIO()
    stderr = io.StringIO()

    monkeypatch.setattr(sys, "stdin", stdin)
    monkeypatch.setattr(sys, "stdout", stdout)
    monkeypatch.setattr(sys, "stderr", stderr)

    monkeypatch.setattr("tools.output_pattern_chunker.OutputPatternChunker", lambda: OutputPatternChunker(max_line_length=20))
    process_shell_output()

    output_lines = stdout.getvalue().strip().splitlines()
    assert len(output_lines) > 1
    err = stderr.getvalue().strip()
    assert "[CHUNKED]" in err
    temp_path = err.split("Full content:")[-1].strip()
    with open(temp_path, "r") as fh:
        assert fh.read().strip() == long_line
    os.remove(temp_path)
