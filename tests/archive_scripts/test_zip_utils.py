"""Tests for :mod:`src.scripts.archive.zip_utils`."""

from pathlib import Path
import zipfile

import pytest

from src.scripts.archive.zip_utils import create_zip, extract_zip


def _make_zip(tmp_path: Path, files: dict[str, str]) -> Path:
    path = tmp_path / "data.zip"
    with zipfile.ZipFile(path, "w") as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return path


def test_extract_basic(tmp_path):
    archive = _make_zip(tmp_path, {"hello.txt": "world"})
    dest = tmp_path / "out"
    extracted = extract_zip(archive, dest)
    assert (dest / "hello.txt").read_text() == "world"
    assert extracted == [dest / "hello.txt"]


def test_extract_prevents_traversal(tmp_path):
    archive = _make_zip(tmp_path, {"../evil.txt": "bad"})
    dest = tmp_path / "out"
    with pytest.raises(ValueError):
        extract_zip(archive, dest)


def test_create_zip_ignores_missing(tmp_path):
    existing = tmp_path / "a.txt"
    existing.write_text("data")
    missing = tmp_path / "missing.txt"
    archive = create_zip(tmp_path / "out.zip", [existing, missing])
    with zipfile.ZipFile(archive) as zf:
        assert zf.namelist() == ["a.txt"]


def test_create_zip_includes_directories(tmp_path):
    folder = tmp_path / "src"
    (folder / "sub").mkdir(parents=True)
    (folder / "file1.txt").write_text("1")
    (folder / "sub" / "file2.txt").write_text("2")
    archive = create_zip(tmp_path / "out_dir.zip", [folder])
    with zipfile.ZipFile(archive) as zf:
        assert sorted(zf.namelist()) == ["file1.txt", "sub/file2.txt"]


def test_extract_overwrite(tmp_path):
    archive = _make_zip(tmp_path, {"hello.txt": "new"})
    dest = tmp_path / "out"
    dest.mkdir()
    existing = dest / "hello.txt"
    existing.write_text("old")

    # Default behaviour skips existing files
    assert extract_zip(archive, dest) == []
    assert existing.read_text() == "old"

    # When overwrite=True the file is replaced
    extracted = extract_zip(archive, dest, overwrite=True)
    assert extracted == [existing]
    assert existing.read_text() == "new"


def test_create_zip_includes_empty_directories(tmp_path):
    folder = tmp_path / "src"
    (folder / "empty").mkdir(parents=True)
    archive = create_zip(tmp_path / "out_empty.zip", [folder])
    with zipfile.ZipFile(archive) as zf:
        assert "empty/" in zf.namelist()
