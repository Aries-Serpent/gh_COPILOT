#!/usr/bin/env python3
"""Utility to archive and Base64-encode binary files.

Enterprise Standards Compliance:
- Flake8/PEP 8 Compliant
- Emoji-free code (text-based indicators only)
- Database-first architecture (not applicable)

This script helps standardize handling of binary artifacts within the
repository. Given a binary file, it will:

1. Remove the file from Git tracking (if tracked).
2. Append the file path to ``.gitignore``.
3. Create a ZIP archive containing the binary.
4. Base64-encode the archive using the existing ``EncodeWorker``.
5. Write the encoded text to ``<name>_zip_base64.txt`` alongside the
   original file.
6. Clean up the intermediate ZIP archive.

The generated text file and updated ``.gitignore`` are staged for commit.

Example
-------

```
python scripts/binary_to_base64.py databases/analytics.db
```

After running the script, commit the staged changes with an appropriate
message.
"""

from __future__ import annotations

import argparse
import subprocess
import zipfile
from pathlib import Path

from misc.legacy.Base64ImageTransformer import EncodeWorker
from enterprise_modules.compliance import (
    anti_recursion_guard,
    validate_enterprise_operation,
)

TEXT_INDICATORS = {
    "start": "[START]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
}


@anti_recursion_guard
def run_git(*args: str) -> None:
    """Run a Git command, ignoring errors."""

    command = f"git {' '.join(args)}"
    if not validate_enterprise_operation(command=command):
        raise RuntimeError("forbidden command")
    subprocess.run(["git", *args], check=False)


@anti_recursion_guard
def append_gitignore(path: Path) -> None:
    """Append the given path to .gitignore if not already present."""

    gitignore = Path(".gitignore")
    if not validate_enterprise_operation(str(gitignore)):
        raise RuntimeError("Invalid target path")
    existing = gitignore.read_text(encoding="utf-8").splitlines()
    if str(path) not in existing:
        with gitignore.open("a", encoding="utf-8") as fh:
            fh.write(f"\n{path}\n")
    run_git("add", ".gitignore")


def encode_zip(zip_path: Path) -> str:
    """Encode the ZIP archive to Base64 using EncodeWorker."""

    encoded: list[str] = []
    worker = EncodeWorker(str(zip_path))
    worker.encoding_successful.connect(encoded.append)
    worker.run_encode()
    if not encoded:
        raise RuntimeError("encoding failed")
    return encoded[0]


@anti_recursion_guard
def process_file(file_path: Path) -> Path:
    """Process a single file and return path to the encoded text file."""

    if not validate_enterprise_operation(str(file_path)):
        raise RuntimeError("Invalid target path")
    run_git("rm", "--cached", str(file_path))
    append_gitignore(file_path)

    zip_path = file_path.with_suffix(file_path.suffix + ".zip")
    if not validate_enterprise_operation(str(zip_path)):
        raise RuntimeError("Invalid target path")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(file_path, arcname=file_path.name)

    b64_text = encode_zip(zip_path)
    zip_path.unlink()

    output_path = file_path.with_name(f"{file_path.name}_zip_base64.txt")
    if not validate_enterprise_operation(str(output_path)):
        raise RuntimeError("Invalid target path")
    output_path.write_text(b64_text, encoding="utf-8")
    run_git("add", str(output_path))
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive and encode binary files")
    parser.add_argument("file", type=Path, help="Path to the binary file")
    args = parser.parse_args()

    file_path = args.file
    if not validate_enterprise_operation(str(file_path)):
        raise RuntimeError("Invalid target path")
    if not file_path.exists():
        print(f"{TEXT_INDICATORS['error']} File not found: {file_path}")
        return 1

    print(f"{TEXT_INDICATORS['start']} Processing {file_path}")
    try:
        output = process_file(file_path)
    except Exception as exc:  # pragma: no cover - unexpected failures
        print(f"{TEXT_INDICATORS['error']} {exc}")
        return 1

    print(f"{TEXT_INDICATORS['success']} Created {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

