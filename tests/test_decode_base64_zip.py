"""Tests for base64 ZIP decoding and extraction."""

import base64
import binascii
import io
import zipfile

import pytest

from decode_base64_zip import decode_and_extract_base64_zip


def _create_zip_base64() -> str:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("test.txt", "hello")
    return base64.b64encode(buffer.getvalue()).decode()


def test_successful_extraction(tmp_path):
    b64_data = _create_zip_base64()
    result = decode_and_extract_base64_zip(b64_data, output_dir=str(tmp_path))

    assert result["success"] is True
    extracted = tmp_path / "test.txt"
    assert extracted.exists()
    assert extracted.read_text() == "hello"


def test_corrupted_base64(tmp_path):
    with pytest.raises(binascii.Error):
        decode_and_extract_base64_zip("not-base64", output_dir=str(tmp_path))


def test_bad_zip(tmp_path):
    bad_zip_b64 = base64.b64encode(b"notzip").decode()
    with pytest.raises(zipfile.BadZipFile):
        decode_and_extract_base64_zip(bad_zip_b64, output_dir=str(tmp_path))

