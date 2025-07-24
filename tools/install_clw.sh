#!/usr/bin/env bash
# Install or recreate the clw line wrapping utility.
# This utility wraps lines longer than 1550 bytes to prevent terminal resets.
set -euo pipefail

TARGET="/usr/local/bin/clw"
cat > "$TARGET" <<'PYEOF'
#!/usr/bin/env python3
"""Line wrapper for Codex sessions."""
import binascii
import os
import re
import sys

DEFAULT_MAX_LINE_LENGTH = 1550
DEFAULT_WRAP_MARK = "⏎"


def split_into_chunks(s: bytes, chunk_size: int):
    rx_word_wrap = re.compile(rb"^.*(\b).+", re.DOTALL)
    start = 0
    while True:
        end = start + chunk_size
        chunk = s[start:end]
        if len(chunk) < chunk_size:
            yield False, chunk
            return
        m = rx_word_wrap.match(chunk)
        if m and m.start(1):
            chunk = chunk[: m.start(1)]
        yield True, chunk
        start += len(chunk)


def main() -> None:
    env_max_line_length = os.environ.get("CLW_MAX_LINE_LENGTH")
    max_line_length = int(env_max_line_length) if env_max_line_length else DEFAULT_MAX_LINE_LENGTH

    env_wrap_mark = os.environ.get("CLW_WRAP_MARK")
    wrap_mark = binascii.unhexlify(env_wrap_mark) if env_wrap_mark else DEFAULT_WRAP_MARK.encode("utf-8")
    wrap_mark = wrap_mark + b"\n"

    chunk_size = max_line_length - len(wrap_mark)
    assert chunk_size > 0

    for line in sys.stdin.buffer:
        for wrapped, chunk in split_into_chunks(line, chunk_size):
            sys.stdout.buffer.write(chunk)
            if wrapped:
                sys.stdout.buffer.write(wrap_mark)
            sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()
PYEOF
chmod +x "$TARGET"
echo "clw installed to $TARGET"
