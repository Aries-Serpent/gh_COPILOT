"""Utility for chunking overly long output lines.

This module provides the OutputChunker class which reads lines and yields
chunks that do not exceed a configurable length. It preserves ANSI escape
sequences and attempts to break JSON and other structured data at
natural boundaries.
"""
from __future__ import annotations

import re
import sys
import tempfile
from typing import Iterator, Tuple


class OutputChunker:
    """Chunk lines while preserving common structure."""

    def __init__(self, max_line_length: int = 4000) -> None:
        self.max_length = max_line_length
        self.ansi_pattern = re.compile(r"\x1b\[[0-9;]*m")
        self.chunk_counter = 0

    def detect_patterns(self, line: str) -> dict:
        """Identify line structure for intelligent chunking."""
        return {
            "ansi_colored": bool(self.ansi_pattern.search(line)),
            "json_like": line.strip().startswith("{")
            or line.strip().startswith("["),
            "log_entry": re.match(r"^\d{4}-\d{2}-\d{2}", line.strip()),
            "csv_like": "," in line and line.count(",") > 3,
            "whitespace_heavy": len(line.strip()) < len(line) * 0.3,
        }

    def chunk_line(self, line: str) -> Iterator[Tuple[str, bool]]:
        """Chunk line intelligently based on patterns."""
        if len(line) <= self.max_length:
            yield line, False
            return

        patterns = self.detect_patterns(line)

        if patterns["ansi_colored"]:
            yield from self._chunk_ansi_line(line)
        elif patterns["json_like"]:
            yield from self._chunk_json_line(line)
        elif patterns["log_entry"]:
            yield from self._chunk_log_line(line)
        elif patterns["csv_like"]:
            yield from self._chunk_csv_line(line)
        else:
            yield from self._chunk_simple(line)

    def _chunk_ansi_line(self, line: str) -> Iterator[Tuple[str, bool]]:
        """Chunk while preserving ANSI escape sequences."""
        chunks: list[str] = []
        current_chunk = ""
        ansi_stack: list[str] = []
        i = 0
        while i < len(line):
            if line[i : i + 2] == "\x1b[":
                ansi_end = line.find("m", i)
                if ansi_end != -1:
                    ansi_seq = line[i : ansi_end + 1]
                    if len(current_chunk + ansi_seq) < self.max_length:
                        current_chunk += ansi_seq
                        ansi_stack.append(ansi_seq)
                        i = ansi_end + 1
                    else:
                        yield self._close_ansi_chunk(
                            current_chunk, ansi_stack
                        ), True
                        current_chunk = self._open_ansi_chunk(ansi_stack) + ansi_seq
                        i = ansi_end + 1
                else:
                    i += 1
            else:
                if len(current_chunk) < self.max_length:
                    current_chunk += line[i]
                    i += 1
                else:
                    yield self._close_ansi_chunk(current_chunk, ansi_stack), True
                    current_chunk = self._open_ansi_chunk(ansi_stack)
        if current_chunk:
            yield self._close_ansi_chunk(current_chunk, ansi_stack), len(line) > self.max_length

    def _close_ansi_chunk(self, chunk: str, ansi_stack: list[str]) -> str:
        """Close ANSI sequences for clean chunk ending."""
        return chunk + "\x1b[0m"

    def _open_ansi_chunk(self, ansi_stack: list[str]) -> str:
        """Reopen ANSI sequences for chunk continuation."""
        return "".join(ansi_stack)

    def _chunk_json_line(self, line: str) -> Iterator[Tuple[str, bool]]:
        """Chunk JSON at logical boundaries."""
        brace_level = 0
        current_chunk = ""
        for char in line:
            current_chunk += char
            if char in "[{":
                brace_level += 1
            elif char in "}]":
                brace_level -= 1
            if len(current_chunk) >= self.max_length and brace_level == 0:
                yield current_chunk, True
                current_chunk = ""
        if current_chunk:
            yield current_chunk, len(line) > self.max_length

    def _chunk_log_line(self, line: str) -> Iterator[Tuple[str, bool]]:
        """Chunk log lines at whitespace boundaries."""
        parts = line.split()
        current = ""
        for part in parts:
            token = part if not current else f" {part}"
            if len(current) + len(token) <= self.max_length:
                current += token
            else:
                yield current, True
                current = part
        if current:
            yield current, len(line) > self.max_length

    def _chunk_csv_line(self, line: str) -> Iterator[Tuple[str, bool]]:
        """Chunk CSV-like lines at comma boundaries."""
        parts = line.split(",")
        current = ""
        for part in parts:
            token = part if not current else f",{part}"
            if len(current) + len(token) <= self.max_length:
                current += token
            else:
                yield current, True
                current = part
        if current:
            yield current, len(line) > self.max_length

    def _chunk_simple(self, line: str) -> Iterator[Tuple[str, bool]]:
        """Simple character-based chunking."""
        for i in range(0, len(line), self.max_length):
            chunk = line[i : i + self.max_length]
            is_overflow = len(line) > self.max_length
            yield chunk, is_overflow


def process_output() -> None:
    """Process STDIN and chunk any long lines."""
    chunker = OutputChunker()
    temp_file = None
    for line in sys.stdin:
        for chunk, is_overflow in chunker.chunk_line(line.rstrip("\n")):
            if is_overflow and temp_file is None:
                temp_file = tempfile.NamedTemporaryFile(
                    mode="w", delete=False, prefix="shell_overflow_", suffix=".log"
                )
                print(
                    f"[CHUNKED] Output overflow detected. Full content: {temp_file.name}",
                    file=sys.stderr,
                )
            print(chunk)
            if temp_file:
                temp_file.write(chunk + "\n")
    if temp_file:
        temp_file.close()


if __name__ == "__main__":
    process_output()
