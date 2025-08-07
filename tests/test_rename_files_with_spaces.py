from pathlib import Path, PureWindowsPath
import rename_files_with_spaces as rfs

def test_relative_path_unix():
    expected = Path(rfs.__file__).resolve().parent / 'documentation/generated/daily_state_update'
    assert expected.exists()


def test_relative_path_windows():
    base = PureWindowsPath('C:/gh_COPILOT')
    target = base / 'documentation/generated/daily_state_update'
    assert str(target).endswith('documentation\\generated\\daily_state_update')
