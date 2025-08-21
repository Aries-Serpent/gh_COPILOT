"""Regression tests for the Base64 ZIP transformer."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

try:
    import PyQt6  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    import tests.stubs.PyQt6 as PyQt6  # type: ignore
    sys.modules.setdefault("PyQt6", PyQt6)
    sys.modules.setdefault("PyQt6.QtCore", PyQt6.QtCore)
    sys.modules.setdefault("PyQt6.QtWidgets", PyQt6.QtWidgets)

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

# Make legacy module importable
sys.path.append(str(Path(__file__).resolve().parents[1] / "legacy"))
from Base64ZipTransformer import DecodeWorker, EncodeWorker  # noqa: E402


def _run_encode(path: Path) -> str:
    result = {}

    def handle(text: str) -> None:
        result["b64"] = text

    worker = EncodeWorker(str(path))
    worker.encoding_successful.connect(handle)
    worker.run_encode()
    return result["b64"]


def _run_decode(b64: str) -> bytes:
    result = {}

    def handle(data: bytes, names: list[str]) -> None:
        result["data"] = data
        result["names"] = names

    worker = DecodeWorker(b64)
    worker.decoding_successful.connect(handle)
    worker.run_decode()
    assert result["names"]  # ensure entries were reported
    return result["data"]


def test_round_trip_zip(tmp_path: Path) -> None:
    archive_path = tmp_path / "sample.zip"
    inner_path = tmp_path / "hello.txt"
    inner_path.write_text("hello world", encoding="utf-8")

    with zipfile.ZipFile(archive_path, "w") as zf:
        zf.write(inner_path, arcname="hello.txt")

    b64 = _run_encode(archive_path)
    decoded = _run_decode(b64)

    with zipfile.ZipFile(io.BytesIO(decoded)) as zf:
        assert zf.read("hello.txt").decode("utf-8") == "hello world"
