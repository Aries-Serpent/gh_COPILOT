from tools.output_chunker import OutputChunker


def test_chunker_handles_short_line():
    chunker = OutputChunker(max_line_length=10)
    chunks = list(chunker.chunk_line("short"))
    assert chunks == [("short", False)]


def test_chunker_splits_long_line():
    chunker = OutputChunker(max_line_length=10)
    long_line = "x" * 25
    chunks = list(chunker.chunk_line(long_line))
    assert len(chunks) == 3
    assert all(len(c[0]) <= 10 for c in chunks)
    assert all(c[1] for c in chunks)
