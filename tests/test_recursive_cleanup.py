from pathlib import Path

from scripts.utilities.recursive_violation_cleanup import remove_folders, scan_forbidden_folders


def test_scan_forbidden_folders(tmp_path: Path) -> None:
    (tmp_path / "good").mkdir()
    bad = tmp_path / "bad_backup"
    bad.mkdir()
    found = scan_forbidden_folders([tmp_path], ["*backup*"])
    assert bad in found


def test_remove_folders(tmp_path: Path) -> None:
    folder = tmp_path / "toremove"
    folder.mkdir()
    removed, errors = remove_folders([folder])
    assert str(folder) in removed
    assert not errors
    assert not folder.exists()
