"""Enhanced output chunker with pattern awareness.

This module exposes :class:`OutputPatternChunker` which detects common
output patterns such as ANSI coloured text, JSON blobs, log lines, CSV
rows, source code and git output. Long lines are split into manageable
chunks while preserving structural boundaries where possible. When a
line exceeds the configured ``max_line_length`` the full, unmodified
line is written to a temporary file so callers may inspect the original
content.

It also provides a small CLI utility :func:`process_shell_output` which
reads from ``stdin`` and writes the chunked lines to ``stdout``.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
import sys
import tempfile
from typing import Iterator, Tuple

ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*m")
LOG_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}")
GIT_PATTERN = re.compile(r"^(diff --git|@@|index [0-9a-f]{7,}|commit [0-9a-f]{7,})")


@dataclass
class OutputPatternChunker:
    """Chunk lines while preserving common structures."""

    max_line_length: int = 4000

    def detect_pattern(self, line: str) -> str:
        """Return a simple label describing the line pattern."""

        stripped = line.strip()
        if ANSI_PATTERN.search(line):
            return "ansi"
        if stripped.startswith("{") or stripped.startswith("["):
            return "json"
        if LOG_PATTERN.match(stripped):
            return "log"
        if "," in line and line.count(",") >= 3:
            return "csv"
        if GIT_PATTERN.match(stripped):
            return "git"
        if any(keyword in line for keyword in [
            "def ",
            "class ",
            "import ",
            "return",
            "if ",
            "for ",
            "while ",
            ";",
        ]):
            return "code"
        return "plain"

    # ------------------------------------------------------------------
    # chunking helpers
    # ------------------------------------------------------------------
    def chunk_line(self, line: str) -> Iterator[Tuple[str, bool]]:
        """Yield chunks of ``line`` no longer than ``max_line_length``.

        Each yielded tuple is ``(chunk, overflow)`` where ``overflow`` is
        ``True`` when the original line exceeded ``max_line_length``.
        """

        if len(line) <= self.max_line_length:
            yield line, False
            return

        pattern = self.detect_pattern(line)
        if pattern == "ansi":
            yield from self._chunk_ansi(line)
        elif pattern == "json":
            yield from self._chunk_json(line)
        elif pattern == "csv":
            yield from self._chunk_by_delimiter(line, ",")
        elif pattern in {"log", "code", "git"}:
            yield from self._chunk_by_delimiter(line, " ")
        else:
            yield from self._chunk_simple(line)

    def _chunk_ansi(self, line: str) -> Iterator[Tuple[str, bool]]:
        """Chunk while keeping ANSI sequences intact."""

        current = ""
        ansi_stack: list[str] = []
        i = 0
        while i < len(line):
            if line[i : i + 2] == "\x1b[":
                end = line.find("m", i)
                if end == -1:
                    i += 1
                    continue
                seq = line[i : end + 1]
                if len(current + seq) > self.max_line_length:
                    yield self._close_ansi(current, ansi_stack), True
                    current = self._open_ansi(ansi_stack) + seq
                else:
                    current += seq
                    ansi_stack.append(seq)
                i = end + 1
            else:
                if len(current) >= self.max_line_length:
                    yield self._close_ansi(current, ansi_stack), True
                    current = self._open_ansi(ansi_stack)
                current += line[i]
                i += 1
        if current:
            yield self._close_ansi(current, ansi_stack), True

    def _open_ansi(self, stack: list[str]) -> str:
        return "".join(stack)

    def _close_ansi(self, chunk: str, stack: list[str]) -> str:
        return chunk + "\x1b[0m"

    def _chunk_json(self, line: str) -> Iterator[Tuple[str, bool]]:
        level = 0
        current = ""
        for ch in line:
            current += ch
            if ch in "[{":
                level += 1
            elif ch in "}]":
                level -= 1
            if len(current) >= self.max_line_length and level == 0:
                yield current, True
                current = ""
        if current:
            yield current, True

    def _chunk_by_delimiter(self, line: str, delim: str) -> Iterator[Tuple[str, bool]]:
        tokens = line.split(delim)
        current = ""
        for token in tokens:
            candidate = f"{current}{delim}{token}" if current else token
            if len(candidate) > self.max_line_length:
                if current:
                    yield current, True
                if len(token) > self.max_line_length:
                    for i in range(0, len(token), self.max_line_length):
                        yield token[i : i + self.max_line_length], True
                    current = ""
                else:
                    current = token
            else:
                current = candidate
        if current:
            yield current, True

    def _chunk_simple(self, line: str) -> Iterator[Tuple[str, bool]]:
        for i in range(0, len(line), self.max_line_length):
            yield line[i : i + self.max_line_length], True


def process_shell_output() -> None:
    """CLI helper reading from stdin and writing chunked lines to stdout."""

    chunker = OutputPatternChunker()
    temp_file = None
    for raw_line in sys.stdin:
        line = raw_line.rstrip("\n")
        overflow = False
        for chunk, is_overflow in chunker.chunk_line(line):
            overflow = overflow or is_overflow
            print(chunk)
        if overflow:
            if temp_file is None:
                temp_file = tempfile.NamedTemporaryFile(
                    mode="w", delete=False, prefix="shell_output_", suffix=".log"
                )
                print(
                    f"[CHUNKED] Output overflow detected. Full content: {temp_file.name}",
                    file=sys.stderr,
                )
            temp_file.write(raw_line)
    if temp_file is not None:
        temp_file.close()


if __name__ == "__main__":
    process_shell_output()
