from pathlib import Path

from utils.file_utils import quarantine_zero_byte_files


def test_quarantine_zero_byte_files(tmp_path: Path) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    qb_dir = tmp_path / "_ZERO_BYTE_QUARANTINE"
    (logs / "a.log").touch()
    (logs / "b.log").write_text("data")

    moved = quarantine_zero_byte_files(logs, qb_dir)
    assert moved == 1
    assert not (logs / "a.log").exists()
    assert (qb_dir / "a.log").exists()
