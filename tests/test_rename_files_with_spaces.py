from pathlib import Path, PureWindowsPath
import types
import sys

import pytest
import rename_files_with_spaces as rfs

def test_relative_path_unix():
    expected = Path(rfs.__file__).resolve().parent / 'documentation/generated/daily_state_update'
    assert expected.exists()


def test_relative_path_windows():
    base = PureWindowsPath('C:/gh_COPILOT')
    target = base / 'documentation/generated/daily_state_update'
    assert str(target).endswith('documentation\\generated\\daily_state_update')


def _create_pdf(path: Path) -> None:
    path.write_bytes(b"%PDF-1.4\n%EOF")


def test_renamer_conversion_enabled(monkeypatch, tmp_path):
    _create_pdf(tmp_path / "sample report.pdf")

    called = {"convert": False, "fetch": False, "index": False}

    def fake_convert_pdfs(directory: Path):
        called["convert"] = True
        for pdf in directory.glob("*.pdf"):
            pdf.with_suffix(".md").write_text("converted")
            yield f"converted {pdf.name}"

    def fake_fetch_lfs_objects():
        called["fetch"] = True

    def fake_update_index(*args, **kwargs):
        called["index"] = True

    monkeypatch.setitem(
        sys.modules,
        "tools.convert_daily_whitepaper",
        types.SimpleNamespace(
            convert_pdfs=fake_convert_pdfs, fetch_lfs_objects=fake_fetch_lfs_objects
        ),
    )
    monkeypatch.setitem(
        sys.modules,
        "scripts.documentation.update_daily_state_index",
        types.SimpleNamespace(update_index=fake_update_index),
    )

    renamer = rfs.FileRenamer(tmp_path)
    renamer.rename_all_files(run_conversion=True)

    assert (tmp_path / "sample_report.pdf").exists()
    assert (tmp_path / "sample_report.md").exists()
    assert called == {"convert": True, "fetch": True, "index": True}


def test_renamer_conversion_disabled(tmp_path):
    _create_pdf(tmp_path / "sample report.pdf")
    renamer = rfs.FileRenamer(tmp_path)
    renamer.rename_all_files(run_conversion=False)
    assert (tmp_path / "sample_report.pdf").exists()
    assert not (tmp_path / "sample_report.md").exists()
    assert "tools.convert_daily_whitepaper" not in sys.modules
