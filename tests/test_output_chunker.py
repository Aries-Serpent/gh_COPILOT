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


def test_chunker_splits_log_line_at_fields():
    chunker = OutputChunker(max_line_length=30)
    line = "2023-10-05 12:34:56 INFO message part1 part2"
    chunks = [c[0] for c in chunker.chunk_line(line)]
    assert chunks == ["2023-10-05 12:34:56 INFO", "message part1 part2"]


def test_chunker_splits_csv_at_commas():
    chunker = OutputChunker(max_line_length=7)
    line = "a,b,c,d,e,f"
    chunks = [c[0] for c in chunker.chunk_line(line)]
    assert chunks == ["a,b,c,d", "e,f"]
