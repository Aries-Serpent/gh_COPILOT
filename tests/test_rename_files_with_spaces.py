from pathlib import PurePosixPath, PureWindowsPath

from rename_files_with_spaces import FileRenamer


def test_target_directory_path():
    posix_path = PurePosixPath("/workspace/gh_COPILOT/rename_files_with_spaces.py")
    windows_path = PureWindowsPath("C:/workspace/gh_COPILOT/rename_files_with_spaces.py")

    expected_posix = posix_path.parent / "documentation/generated/daily_state_update"
    expected_windows = windows_path.parent / "documentation/generated/daily_state_update"

    assert str(expected_posix).endswith("documentation/generated/daily_state_update")
    assert str(expected_windows).endswith("documentation\\generated\\daily_state_update")


def test_file_renamer(tmp_path):
    file_with_spaces = tmp_path / "file with space.txt"
    file_with_spaces.write_text("sample")

    renamer = FileRenamer(tmp_path)
    summary = renamer.rename_all_files()

    assert summary["files_renamed"] == 1
    assert (tmp_path / "file_with_space.txt").exists()
