"""Pattern aware output chunker.

This module provides ``IntelligentOutputChunker`` which splits lines while
respecting ANSI escape sequences and configurable boundary patterns.
"""
from __future__ import annotations

import re
from typing import Dict, Iterable, Iterator, List, Pattern, Tuple


class IntelligentOutputChunker:
    """Chunk output lines using pattern hints."""

    def __init__(self, max_line_length: int = 4000, patterns: Iterable[str] | None = None) -> None:
        self.max_length = max_line_length
        # Detection regexes
        self.ansi_pattern: Pattern[str] = re.compile(r"\x1b\[[0-9;]*m")
        self.json_pattern: Pattern[str] = re.compile(r"^\s*(?:\{.*\}|\[.*\])\s*$")
        self.log_pattern: Pattern[str] = re.compile(r"^\d{4}-\d{2}-\d{2}[ T].*")
        self.csv_pattern: Pattern[str] = re.compile(r"^[^,\n]+(,[^,\n]+)+")
        self.code_pattern: Pattern[str] = re.compile(r"^```")
        self.git_pattern: Pattern[str] = re.compile(
            r"^(?:diff --git |@@|commit [0-9a-f]{7,40})"
        )
        self.detectors: Dict[str, Pattern[str]] = {
            "ansi": self.ansi_pattern,
            "json": self.json_pattern,
            "log": self.log_pattern,
            "csv": self.csv_pattern,
            "code": self.code_pattern,
            "git": self.git_pattern,
        }
        self.patterns: List[str] = list(patterns or [",", " "])

    def classify(self, line: str) -> str:
        """Return detected output pattern type."""
        for name, regex in self.detectors.items():
            if regex.search(line):
                return name
        return "generic"

    def chunk_line(self, line: str) -> Iterator[Tuple[str, bool]]:
        """Yield chunks of ``line`` no longer than ``max_line_length``.

        If ANSI escape sequences are present, they are preserved across
        chunks. When possible, chunks end at the provided ``patterns``.
        Returns tuples of ``(chunk, is_overflow)``.
        """
        if len(line) <= self.max_length:
            yield line, False
            return

        pattern_type = self.classify(line)
        handler = getattr(self, f"_chunk_{pattern_type}_line", None)
        if handler is None:
            handler = self._chunk_by_pattern
        yield from handler(line)

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

    def _chunk_by_pattern(
        self, line: str, patterns: Iterable[str] | None = None
    ) -> Iterator[Tuple[str, bool]]:
        pats = list(patterns or self.patterns)
        start = 0
        length = len(line)
        while start < length:
            end = min(start + self.max_length, length)
            chunk = line[start:end]
            for pat in pats:
                idx = chunk.rfind(pat)
                if idx > 0 and idx + start != end and idx > self.max_length // 2:
                    end = start + idx + 1
                    chunk = line[start:end]
                    break
            yield chunk, length > self.max_length
            start = end

    # Specialized chunkers -------------------------------------------------

    def _chunk_json_line(self, line: str) -> Iterator[Tuple[str, bool]]:
        yield from self._chunk_by_pattern(line, [",", "}", "]"])

    def _chunk_log_line(self, line: str) -> Iterator[Tuple[str, bool]]:
        yield from self._chunk_by_pattern(line, [" ", "|", ","])

    def _chunk_csv_line(self, line: str) -> Iterator[Tuple[str, bool]]:
        yield from self._chunk_by_pattern(line, [","])

    def _chunk_code_line(self, line: str) -> Iterator[Tuple[str, bool]]:
        yield from self._chunk_by_pattern(line, [" ", ",", "(", ")"])

    def _chunk_git_line(self, line: str) -> Iterator[Tuple[str, bool]]:
        yield from self._chunk_by_pattern(line, [" ", "@@", "+++", "---"])


