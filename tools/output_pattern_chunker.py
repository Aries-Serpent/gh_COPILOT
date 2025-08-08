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
from typing import Dict, Iterable, Iterator, List, Pattern, Tuple

__all__ = [
    "OutputPatternChunker",
    "process_shell_output",
]

# Detection regexes for common output patterns
ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*m")
JSON_PATTERN = re.compile(r"^\s*(?:\{.*\}|\[.*\])\s*$")
LOG_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}[ T].*")
CSV_PATTERN = re.compile(r"^[^,\n]+(,[^,\n]+)+")
CODE_PATTERN = re.compile(r"^```")
GIT_PATTERN = re.compile(r"^(diff --git |@@|commit [0-9a-f]{7,40})")


@dataclass
class OutputPatternChunker:
    """Chunk lines while preserving common structures."""
    max_line_length: int = 4000
    patterns: Iterable[str] | None = None

    def __post_init__(self):
        # Compile regex detectors
        self.ansi_pattern: Pattern[str] = ANSI_PATTERN
        self.json_pattern: Pattern[str] = JSON_PATTERN
        self.log_pattern: Pattern[str] = LOG_PATTERN
        self.csv_pattern: Pattern[str] = CSV_PATTERN
        self.code_pattern: Pattern[str] = CODE_PATTERN
        self.git_pattern: Pattern[str] = GIT_PATTERN
        self.detectors: Dict[str, Pattern[str]] = {
            "ansi": self.ansi_pattern,
            "json": self.json_pattern,
            "log": self.log_pattern,
            "csv": self.csv_pattern,
            "code": self.code_pattern,
            "git": self.git_pattern,
        }
        self.chunk_patterns: List[str] = list(self.patterns or [",", " "])

    def classify(self, line: str) -> str:
        """Return detected output pattern type."""
        for name, regex in self.detectors.items():
            if regex.search(line):
                return name
        # Additional heuristics for code, csv, etc.
        stripped = line.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            return "json"
        if "," in line and line.count(",") >= 3:
            return "csv"
        if any(keyword in line for keyword in [
            "def ", "class ", "import ", "return", "if ", "for ", "while ", ";"
        ]):
            return "code"
        return "generic"

    def chunk_line(self, line: str) -> Iterator[Tuple[str, bool]]:
        """Yield chunks of ``line`` no longer than ``max_line_length``.

        Each yielded tuple is ``(chunk, overflow)`` where ``overflow`` is
        ``True`` when the original line exceeded ``max_line_length``.
        """
        if len(line) <= self.max_line_length:
            yield line, False
            return

        pattern_type = self.classify(line)
        handler = getattr(self, f"_chunk_{pattern_type}_line", None)
        if handler is None:
            handler = self._chunk_by_pattern
        yield from handler(line)

    def _chunk_ansi_line(self, line: str) -> Iterator[Tuple[str, bool]]:
        """Chunk while keeping ANSI sequences intact."""
        current = ""
        ansi_stack: list[str] = []
        i = 0
        while i < len(line):
            if line[i: i + 2] == "\x1b[":
                end = line.find("m", i)
                if end == -1:
                    i += 1
                    continue
                seq = line[i: end + 1]
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

    def _chunk_json_line(self, line: str) -> Iterator[Tuple[str, bool]]:
        """Chunk JSON by commas or brackets."""
        yield from self._chunk_by_pattern(line, [",", "}", "]"])

    def _chunk_log_line(self, line: str) -> Iterator[Tuple[str, bool]]:
        """Chunk log lines by space, pipe, or comma."""
        yield from self._chunk_by_pattern(line, [" ", "|", ","])

    def _chunk_csv_line(self, line: str) -> Iterator[Tuple[str, bool]]:
        """Chunk CSV lines by commas."""
        yield from self._chunk_by_pattern(line, [","])

    def _chunk_code_line(self, line: str) -> Iterator[Tuple[str, bool]]:
        """Chunk code lines by space, comma, and brackets."""
        yield from self._chunk_by_pattern(line, [" ", ",", "(", ")"])

    def _chunk_git_line(self, line: str) -> Iterator[Tuple[str, bool]]:
        """Chunk git output lines by space or patch markers."""
        yield from self._chunk_by_pattern(line, [" ", "@@", "+++", "---"])

    def _chunk_generic_line(self, line: str) -> Iterator[Tuple[str, bool]]:
        """Fallback: chunk by default patterns or size."""
        yield from self._chunk_by_pattern(line, self.chunk_patterns)

    def _chunk_by_pattern(
        self, line: str, patterns: Iterable[str] | None = None
    ) -> Iterator[Tuple[str, bool]]:
        """Chunk line by preferred patterns, fallback to max_line_length."""
        pats = list(patterns or self.chunk_patterns)
        start = 0
        length = len(line)
        while start < length:
            end = min(start + self.max_line_length, length)
            chunk = line[start:end]
            # Try to split at the last occurrence of any pattern
            for pat in pats:
                idx = chunk.rfind(pat)
                if idx > 0 and idx + start != end and idx > self.max_line_length // 2:
                    end = start + idx + 1
                    chunk = line[start:end]
                    break
            yield chunk, length > self.max_line_length
            start = end

def process_shell_output() -> None:
    """CLI helper reading from stdin and writing chunked lines to stdout."""
    chunker = OutputPatternChunker()
    temp_file = None
    try:
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
    except Exception as exc:
        print(f"Error during shell output processing: {exc}", file=sys.stderr)
    finally:
        if temp_file is not None:
            temp_file.close()

if __name__ == "__main__":
    process_shell_output()
