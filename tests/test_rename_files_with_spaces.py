from pathlib import Path, PureWindowsPath
import rename_files_with_spaces as rfs
import shutil

from tools.convert_daily_whitepaper import PdfReader
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
