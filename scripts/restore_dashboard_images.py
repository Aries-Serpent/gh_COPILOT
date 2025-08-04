#!/usr/bin/env python3
"""Reconstruct PNG images from base64-encoded text files."""

from __future__ import annotations

import argparse
import base64
from pathlib import Path


def decode_image(path: Path) -> Path:
    """Decode a base64 file to a PNG with the same stem."""
    data = base64.b64decode(path.read_text())
    output_path = path.with_suffix(".png")
    output_path.write_bytes(data)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Restore PNG images from base64-encoded files",
    )
    parser.add_argument(
        "files", nargs="+", help="Paths to .b64 files to decode",
    )
    args = parser.parse_args()

    for file in args.files:
        output = decode_image(Path(file))
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
