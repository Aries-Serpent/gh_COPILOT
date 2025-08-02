"""Legacy Base64 ZIP Transformer.

This module mirrors the structure of ``Base64ImageTransformer`` but focuses on
ZIP archives.  The ``EncodeWorker`` is reused to convert binary files to a
Base64 string, while ``DecodeWorker`` validates decoded data as a ZIP archive
and exposes the contained entries.
"""

from __future__ import annotations

import base64
import binascii
import io
import zipfile
from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import QObject, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class EncodeWorker(QObject):
    """Worker object to perform file encoding to Base64."""

    encoding_successful = pyqtSignal(str)
    encoding_failed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, file_path: str) -> None:
        super().__init__()
        self.file_path = file_path

    def run_encode(self) -> None:
        """Read the file and emit a Base64 string."""
        try:
            data = Path(self.file_path).read_bytes()
            b64_str = base64.b64encode(data).decode("utf-8")
            self.encoding_successful.emit(b64_str)
        except FileNotFoundError:
            self.encoding_failed.emit(f"File not found: {self.file_path}")
        except Exception as exc:  # noqa: BLE001 - broad to surface errors in UI
            self.encoding_failed.emit(f"Failed to encode file: {exc}")
        finally:
            self.finished.emit()


class DecodeWorker(QObject):
    """Worker object to decode Base64 text into ZIP bytes and list entries."""

    decoding_successful = pyqtSignal(bytes, list)
    decoding_failed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, b64_text: str) -> None:
        super().__init__()
        self.b64_text = b64_text

    def run_decode(self) -> None:
        """Decode Base64 text and validate it is a ZIP archive."""
        try:
            decoded = base64.b64decode(self.b64_text, validate=True)
            with zipfile.ZipFile(io.BytesIO(decoded)) as zf:
                entries = zf.namelist()
            self.decoding_successful.emit(decoded, entries)
        except binascii.Error:
            self.decoding_failed.emit("Invalid Base64 string")
        except zipfile.BadZipFile:
            self.decoding_failed.emit("Decoded data is not a valid ZIP archive")
        except Exception as exc:  # noqa: BLE001 - broad to surface errors in UI
            self.decoding_failed.emit(f"Failed to decode Base64: {exc}")
        finally:
            self.finished.emit()


class Base64ZipTransformer(QWidget):
    """GUI application for transforming ZIP archives to and from Base64."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Base64 ZIP Transformer")
        self.resize(800, 600)

        self.tabs = QTabWidget()
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tabs)

        self._init_zip_to_b64_tab()
        self._init_b64_to_zip_tab()

        self.encode_thread: Optional[QThread] = None
        self.decode_thread: Optional[QThread] = None
        self.decoded_zip_data: Optional[bytes] = None

    # ------------------------------------------------------------------
    # Tab 1: ZIP to Base64
    # ------------------------------------------------------------------
    def _init_zip_to_b64_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        select_btn = QPushButton("Select ZIP File")
        select_btn.clicked.connect(self.select_zip_for_encoding)
        layout.addWidget(select_btn)

        self.b64_output = QTextEdit()
        self.b64_output.setReadOnly(True)
        layout.addWidget(self.b64_output)

        copy_btn = QPushButton("Copy Base64")
        copy_btn.clicked.connect(
            lambda: QApplication.clipboard().setText(self.b64_output.toPlainText())
        )
        layout.addWidget(copy_btn)

        self.tabs.addTab(tab, "ZIP to Base64")

    def select_zip_for_encoding(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select ZIP", "", "ZIP Files (*.zip);;All Files (*)"
        )
        if not file_path:
            return

        self.encode_thread = QThread()
        worker = EncodeWorker(file_path)
        worker.moveToThread(self.encode_thread)
        self.encode_thread.started.connect(worker.run_encode)
        worker.encoding_successful.connect(self.b64_output.setText)
        worker.encoding_failed.connect(
            lambda msg: QMessageBox.critical(self, "Encoding Error", msg)
        )
        worker.finished.connect(self.encode_thread.quit)
        worker.finished.connect(worker.deleteLater)
        self.encode_thread.finished.connect(self.encode_thread.deleteLater)
        self.encode_thread.start()

    # ------------------------------------------------------------------
    # Tab 2: Base64 to ZIP
    # ------------------------------------------------------------------
    def _init_b64_to_zip_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.b64_input = QTextEdit()
        layout.addWidget(self.b64_input)

        btn_layout = QHBoxLayout()
        decode_btn = QPushButton("Decode")
        decode_btn.clicked.connect(self.decode_zip_from_base64)
        btn_layout.addWidget(decode_btn)

        self.save_zip_btn = QPushButton("Save ZIP As...")
        self.save_zip_btn.setEnabled(False)
        self.save_zip_btn.clicked.connect(self.save_decoded_zip)
        btn_layout.addWidget(self.save_zip_btn)

        layout.addLayout(btn_layout)

        self.zip_tree = QTreeWidget()
        self.zip_tree.setHeaderLabels(["Entries"])
        layout.addWidget(self.zip_tree)

        self.tabs.addTab(tab, "Base64 to ZIP")

    def decode_zip_from_base64(self) -> None:
        text = self.b64_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Input Required", "Please enter a Base64 string")
            return

        self.decode_thread = QThread()
        worker = DecodeWorker(text)
        worker.moveToThread(self.decode_thread)
        self.decode_thread.started.connect(worker.run_decode)
        worker.decoding_successful.connect(self._on_decode_success)
        worker.decoding_failed.connect(
            lambda msg: QMessageBox.critical(self, "Decoding Error", msg)
        )
        worker.finished.connect(self.decode_thread.quit)
        worker.finished.connect(worker.deleteLater)
        self.decode_thread.finished.connect(self.decode_thread.deleteLater)
        self.decode_thread.start()

    def _on_decode_success(self, data: bytes, entries: List[str]) -> None:
        self.decoded_zip_data = data
        self.zip_tree.clear()
        for name in entries:
            QTreeWidgetItem(self.zip_tree, [name])
        self.save_zip_btn.setEnabled(True)

    def save_decoded_zip(self) -> None:
        if not self.decoded_zip_data:
            QMessageBox.warning(self, "No Data", "Nothing to save")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save ZIP", "", "ZIP Files (*.zip);;All Files (*)"
        )
        if not file_path:
            return
        try:
            Path(file_path).write_bytes(self.decoded_zip_data)
            QMessageBox.information(self, "Saved", "ZIP file saved successfully")
        except Exception as exc:  # noqa: BLE001 - broad to surface errors in UI
            QMessageBox.critical(self, "Save Error", f"Failed to save ZIP: {exc}")


__all__ = [
    "EncodeWorker",
    "DecodeWorker",
    "Base64ZipTransformer",
]

