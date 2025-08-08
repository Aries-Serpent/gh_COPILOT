from tools.output_pattern_chunker import IntelligentOutputChunker
import pytest


def test_truncates_long_lines():
    chunker = IntelligentOutputChunker(max_line_length=10)
    line = "x" * 25
    chunks = list(chunker.chunk_line(line))
    assert len(chunks) == 3
    assert all(len(c[0]) <= 10 for c in chunks)
    assert all(c[1] for c in chunks)


def test_preserves_ansi_sequences():
    chunker = IntelligentOutputChunker(max_line_length=10)
    red = "\x1b[31m" + ("x" * 20) + "\x1b[0m"
    chunks = list(chunker.chunk_line(red))
    assert all(c[0].startswith("\x1b[31m") for c in chunks)
    assert all(c[0].endswith("\x1b[0m") for c in chunks)


@pytest.mark.parametrize(
    "line,expected",
    [
        ("\x1b[31mred\x1b[0m", "ansi"),
        ("{\"a\":1}", "json"),
        ("2023-01-01 00:00:00 INFO msg", "log"),
        ("a,b,c", "csv"),
        ("```python", "code"),
        ("diff --git a/file b/file", "git"),
        ("plain text", "generic"),
    ],
)
def test_classify_patterns(line, expected):
    chunker = IntelligentOutputChunker()
    assert chunker.classify(line) == expected


@pytest.mark.parametrize(
    "line",
    [
        "{\"a\":1,\"b\":2,\"c\":3,\"d\":4}",
        "2023-01-01 00:00:00 INFO part1 part2 part3",
        "alpha,beta,gamma,delta,epsilon",
        "def f(a, b, c, d, e): pass",
        "diff --git a/file b/file with more details",
    ],
)
def test_specialized_chunk_counts(line):
    chunker = IntelligentOutputChunker(max_line_length=20)
    chunks = list(chunker.chunk_line(line))
    assert len(chunks) > 1

