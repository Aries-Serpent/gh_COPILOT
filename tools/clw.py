#!/usr/bin/env python3
"""Command-line wrapper to prevent overly long output lines.

Lines longer than 1550 bytes are hard-wrapped with a visible marker.
Configuration can be controlled with ``CLW_MAX_LINE_LENGTH`` and ``CLW_WRAP_MARK``.
"""

import binascii
import os
import re
import sys

DEFAULT_MAX_LINE_LENGTH = 1550
DEFAULT_WRAP_MARK = "⏎"


def split_into_chunks(data: bytes, chunk_size: int):
    word_wrap = re.compile(rb"^.*(\b).+", re.DOTALL)
    start = 0
    while True:
        end = start + chunk_size
        chunk = data[start:end]
        if len(chunk) < chunk_size:
            yield False, chunk
            return
        match = word_wrap.match(chunk)
        if match and match.start(1):
            chunk = chunk[: match.start(1)]
        yield True, chunk
        start += len(chunk)


USAGE = """Usage: clw [--help]\n\nPipe output through this wrapper to avoid long lines."""


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] in {"-h", "--help"}:
        print(USAGE)
        return

    max_len = int(os.environ.get("CLW_MAX_LINE_LENGTH", DEFAULT_MAX_LINE_LENGTH))
    wrap_mark = os.environ.get("CLW_WRAP_MARK")
    if wrap_mark:
        mark = binascii.unhexlify(wrap_mark)
    else:
        mark = DEFAULT_WRAP_MARK.encode("utf-8")
    mark += b"\n"

    chunk_size = max_len - len(mark)
    if chunk_size <= 0:
        raise ValueError("CLW_MAX_LINE_LENGTH too small")

    for line in sys.stdin.buffer:
        for wrapped, chunk in split_into_chunks(line, chunk_size):
            try:
                sys.stdout.buffer.write(chunk)
                if wrapped:
                    sys.stdout.buffer.write(mark)
                sys.stdout.buffer.flush()
            except BrokenPipeError:
                return


if __name__ == "__main__":
    main()
