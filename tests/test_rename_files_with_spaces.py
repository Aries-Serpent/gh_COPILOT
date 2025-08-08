from pathlib import Path, PureWindowsPath
import rename_files_with_spaces as rfs
import shutil

try:
    from tools.convert_daily_whitepaper import PdfReader
except ModuleNotFoundError:  # pragma: no cover - dependency optional
    PdfReader = None
import pytest

def test_relative_path_unix():
    expected = Path(rfs.__file__).resolve().parent / 'documentation/generated/daily_state_update'
    assert expected.exists()


def test_relative_path_windows():
    base = PureWindowsPath('C:/gh_COPILOT')
    target = base / 'documentation/generated/daily_state_update'
    assert str(target).endswith('documentation\\generated\\daily_state_update')


@pytest.mark.skipif(PdfReader is None, reason="PyPDF2 not installed")
def test_renamer_converts_pdf(tmp_path):
    source_pdf = next((Path('documentation') / 'generated' / 'daily_state_update').glob('*.pdf'))
    shutil.copy(source_pdf, tmp_path / 'sample report.pdf')
    renamer = rfs.FileRenamer(tmp_path)
    renamer.rename_all_files()
    assert (tmp_path / 'sample_report.pdf').exists()
    assert (tmp_path / 'sample_report.md').exists()


def test_rename_file_target_exists(tmp_path):
    original = tmp_path / "file name.txt"
    original.write_text("data")
    target = tmp_path / "file_name.txt"
    target.write_text("existing")
    renamer = rfs.FileRenamer(tmp_path)
    result = renamer.rename_file_safely(original)
    assert result is False
    assert original.exists()
    assert target.read_text() == "existing"
    assert any("target exists" in s for s in renamer.skipped_files)


def test_get_files_with_spaces_unreadable_directory(monkeypatch, tmp_path):
    renamer = rfs.FileRenamer(tmp_path)

    def raise_permission_error(_self):
        raise PermissionError("mocked permission error")

    monkeypatch.setattr(Path, "iterdir", raise_permission_error)
    files = renamer.get_files_with_spaces()
    assert files == []
    assert renamer.errors and "Directory scan error" in renamer.errors[0]
