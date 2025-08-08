from tools.output_pattern_chunker import IntelligentOutputChunker


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

