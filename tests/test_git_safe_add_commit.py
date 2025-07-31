from pathlib import Path

from tools.git_safe_add_commit import exceeds_size, is_binary


def test_exceeds_size(tmp_path: Path) -> None:
    big = tmp_path / "big.bin"
    big.write_bytes(b"0" * (50 * 1024 * 1024 + 1))
    assert exceeds_size(big)


def test_is_binary(tmp_path: Path) -> None:
    binary = tmp_path / "test.bin"
    binary.write_bytes(b"\x00\x01")
    assert is_binary(binary)
