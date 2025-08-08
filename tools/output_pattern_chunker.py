"""Pattern aware output chunker.

This module provides ``IntelligentOutputChunker`` which splits lines while
respecting ANSI escape sequences and configurable boundary patterns.
"""
from __future__ import annotations

import re
from typing import Iterable, Iterator, List, Tuple


class IntelligentOutputChunker:
    """Chunk output lines using pattern hints."""

    def __init__(self, max_line_length: int = 4000, patterns: Iterable[str] | None = None) -> None:
        self.max_length = max_line_length
        self.ansi_pattern = re.compile(r"\x1b\[[0-9;]*m")
        self.patterns: List[str] = list(patterns or [",", " "])

    def chunk_line(self, line: str) -> Iterator[Tuple[str, bool]]:
        """Yield chunks of ``line`` no longer than ``max_line_length``.

        If ANSI escape sequences are present, they are preserved across
        chunks. When possible, chunks end at the provided ``patterns``.
        Returns tuples of ``(chunk, is_overflow)``.
        """
        if len(line) <= self.max_length:
            yield line, False
            return

        if self.ansi_pattern.search(line):
            yield from self._chunk_ansi_line(line)
        else:
            yield from self._chunk_by_pattern(line)

    def _chunk_ansi_line(self, line: str) -> Iterator[Tuple[str, bool]]:
        chunks: list[str] = []
        current = ""
        ansi_stack: list[str] = []
        i = 0
        while i < len(line):
            if line[i : i + 2] == "\x1b[":
                end = line.find("m", i)
                if end == -1:
                    break
                seq = line[i : end + 1]
                if len(current) + len(seq) > self.max_length:
                    yield current + "\x1b[0m", True
                    current = "".join(ansi_stack)
                current += seq
                ansi_stack.append(seq)
                i = end + 1
            else:
                if len(current) >= self.max_length:
                    yield current + "\x1b[0m", True
                    current = "".join(ansi_stack)
                current += line[i]
                i += 1
        if current:
            yield current + "\x1b[0m", True

    def _chunk_by_pattern(self, line: str) -> Iterator[Tuple[str, bool]]:
        start = 0
        length = len(line)
        while start < length:
            end = min(start + self.max_length, length)
            chunk = line[start:end]
            for pat in self.patterns:
                idx = chunk.rfind(pat)
                if idx > 0 and idx + start != end and idx > self.max_length // 2:
                    end = start + idx + 1
                    chunk = line[start:end]
                    break
            yield chunk, length > self.max_length
            start = end


