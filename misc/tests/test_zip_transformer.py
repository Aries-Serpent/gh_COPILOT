"""Tests for the Base64 ZIP transformer."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

try:  # Prefer real PyQt6 when available
    import PyQt6  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - depends on environment
    from tests.stubs import pyqt6 as PyQt6
    sys.modules.setdefault("PyQt6", PyQt6)
    sys.modules.setdefault("PyQt6.QtCore", PyQt6.QtCore)
    sys.modules.setdefault("PyQt6.QtWidgets", PyQt6.QtWidgets)

from PyQt6.QtCore import QCoreApplication

import base64
import types

EncodeModule = types.ModuleType("Base64ImageTransformer")


class EncodeWorker(PyQt6.QtCore.QObject):
    encoding_successful = PyQt6.QtCore.pyqtSignal(str)

    def __init__(self, file_path: str) -> None:
        super().__init__()
        self.file_path = file_path

    def run_encode(self) -> None:  # pragma: no cover - simple stub
        with open(self.file_path, "rb") as fh:
            data = fh.read()
        b64 = base64.b64encode(data).decode("utf-8")
        self.encoding_successful.emit(b64)


EncodeModule.EncodeWorker = EncodeWorker
sys.modules.setdefault("Base64ImageTransformer", EncodeModule)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "legacy"))
from Base64ZipTransformer import DecodeWorker, EncodeWorker  # noqa: E402


def test_encode_and_decode_roundtrip(tmp_path) -> None:
    """Encode a ZIP file to Base64 and decode it back."""

    # Ensure a Qt application exists for signal dispatch
    app = QCoreApplication.instance() or QCoreApplication([])

    # Create a sample ZIP file
    sample_file = tmp_path / "file.txt"
    sample_file.write_text("hello zip")
    zip_path = tmp_path / "sample.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write(sample_file, arcname="file.txt")

    # Encode using worker
    encoded: dict[str, str] = {}
    enc_worker = EncodeWorker(str(zip_path))
    enc_worker.encoding_successful.connect(lambda s: encoded.update({"b64": s}))
    enc_worker.run_encode()

    # Decode back
    decoded: dict[str, bytes | list[str]] = {}
    dec_worker = DecodeWorker(encoded["b64"])
    dec_worker.decoding_successful.connect(
        lambda data, entries: decoded.update({"data": data, "entries": entries})
    )
    dec_worker.run_decode()

    # Verify entries
    assert "file.txt" in decoded["entries"]

    # Verify file contents after extraction
    out_zip = tmp_path / "out.zip"
    out_zip.write_bytes(decoded["data"])
    with zipfile.ZipFile(out_zip) as zf:
        assert zf.read("file.txt") == b"hello zip"

    app.quit()

