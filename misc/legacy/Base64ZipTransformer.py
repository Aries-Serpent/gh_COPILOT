"""Legacy Base64 transformer specialized for ZIP archives."""

from __future__ import annotations

import base64
import binascii
import io
import zipfile
from typing import List, Optional

from PyQt6.QtCore import QObject, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

# Reuse the existing EncodeWorker from the image transformer
from Base64ImageTransformer import EncodeWorker


class DecodeWorker(QObject):
    """Worker that decodes Base64 text and validates it as a ZIP archive."""

    decoding_successful = pyqtSignal(bytes, list)
    decoding_failed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, b64_text: str) -> None:
        super().__init__()
        self.b64_text = b64_text

    def run_decode(self) -> None:
        try:
            data = base64.b64decode(self.b64_text, validate=True)
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                names = zf.namelist()
            self.decoding_successful.emit(data, names)
        except (binascii.Error, zipfile.BadZipFile):
            self.decoding_failed.emit(Base64ZipTransformer.UI_STRINGS.ERR_INVALID_ZIP_MSG)
        except Exception as exc:  # pragma: no cover - unexpected errors
            self.decoding_failed.emit(
                Base64ZipTransformer.UI_STRINGS.ERR_DECODE_FAILED_MSG.format(error=exc)
            )
        finally:
            self.finished.emit()


class Base64ZipTransformer(QWidget):
    """Simple UI for transforming ZIP archives to and from Base64."""

    class UI_STRINGS:
        WINDOW_TITLE = "Base64 ZIP Transformer"
        TAB_ZIP_TO_B64 = "ZIP to Base64"
        TAB_B64_TO_ZIP = "Base64 to ZIP"
        BTN_SELECT_ZIP = "Select ZIP File"
        BTN_COPY_B64 = "Copy Base64"
        BTN_CLEAR_B64_OUTPUT = "Clear Output"
        BTN_DECODE_B64 = "Decode"
        BTN_SAVE_ZIP = "Save ZIP As..."
        BTN_CLEAR_B64_INPUT = "Clear Input"
        ERR_DECODE_FAILED_MSG = "Failed to decode Base64: {error}"
        ERR_INVALID_ZIP_MSG = "Invalid Base64 or ZIP data"
        ERR_ENCODE_FAILED_TITLE = "Encoding Error"
        ERR_DECODE_FAILED_TITLE = "Decoding Error"
        INFO_ZIP_SAVED_TITLE = "Saved"
        INFO_ZIP_SAVED_MSG = "ZIP file saved successfully."

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(self.UI_STRINGS.WINDOW_TITLE)
        self.resize(800, 600)

        self.decoded_zip_data: Optional[bytes] = None

        self.encode_thread: Optional[QThread] = None
        self.encode_worker: Optional[EncodeWorker] = None
        self.decode_thread: Optional[QThread] = None
        self.decode_worker: Optional[DecodeWorker] = None

        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self._init_zip_to_b64_tab()
        self._init_b64_to_zip_tab()

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        main_layout.addWidget(self.progress)

    # ------------------------------------------------------------------
    # Encoding tab
    # ------------------------------------------------------------------
    def _init_zip_to_b64_tab(self) -> None:
        self.tab_zip_to_b64 = QWidget()
        layout = QVBoxLayout(self.tab_zip_to_b64)

        btn_select = QPushButton(self.UI_STRINGS.BTN_SELECT_ZIP)
        btn_select.clicked.connect(self.select_zip_for_encoding)
        layout.addWidget(btn_select)

        self.txt_b64_output = QTextEdit()
        self.txt_b64_output.setReadOnly(True)
        layout.addWidget(self.txt_b64_output)

        btn_row = QHBoxLayout()
        self.btn_copy_b64 = QPushButton(self.UI_STRINGS.BTN_COPY_B64)
        self.btn_copy_b64.setEnabled(False)
        self.btn_copy_b64.clicked.connect(self.copy_b64)
        btn_row.addWidget(self.btn_copy_b64)

        btn_clear = QPushButton(self.UI_STRINGS.BTN_CLEAR_B64_OUTPUT)
        btn_clear.clicked.connect(self.txt_b64_output.clear)
        btn_row.addWidget(btn_clear)

        layout.addLayout(btn_row)

        layout.addStretch()
        self.tabs.addTab(self.tab_zip_to_b64, self.UI_STRINGS.TAB_ZIP_TO_B64)

    def select_zip_for_encoding(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.UI_STRINGS.BTN_SELECT_ZIP,
            "",
            "ZIP Files (*.zip);;All Files (*)",
        )
        if not file_path:
            return

        self.progress.setRange(0, 0)
        self.progress.setVisible(True)
        self.txt_b64_output.clear()
        self.btn_copy_b64.setEnabled(False)

        self.encode_thread = QThread()
        self.encode_worker = EncodeWorker(file_path)
        self.encode_worker.moveToThread(self.encode_thread)
        self.encode_thread.started.connect(self.encode_worker.run_encode)
        self.encode_worker.encoding_successful.connect(self._on_encode_success)
        self.encode_worker.encoding_failed.connect(self._on_encode_fail)
        self.encode_worker.finished.connect(self.encode_thread.quit)
        self.encode_worker.finished.connect(self.encode_worker.deleteLater)
        self.encode_thread.finished.connect(self.encode_thread.deleteLater)
        self.encode_thread.finished.connect(lambda: self.progress.setVisible(False))
        self.encode_thread.start()

    def _on_encode_success(self, b64: str) -> None:
        self.txt_b64_output.setText(b64)
        self.btn_copy_b64.setEnabled(True)

    def _on_encode_fail(self, msg: str) -> None:  # pragma: no cover - UI path
        QMessageBox.critical(self, self.UI_STRINGS.ERR_ENCODE_FAILED_TITLE, msg)

    def copy_b64(self) -> None:  # pragma: no cover - simple UI helper
        QApplication.clipboard().setText(self.txt_b64_output.toPlainText())

    # ------------------------------------------------------------------
    # Decoding tab
    # ------------------------------------------------------------------
    def _init_b64_to_zip_tab(self) -> None:
        self.tab_b64_to_zip = QWidget()
        layout = QVBoxLayout(self.tab_b64_to_zip)

        self.txt_b64_input = QTextEdit()
        layout.addWidget(self.txt_b64_input)

        btn_row = QHBoxLayout()
        btn_decode = QPushButton(self.UI_STRINGS.BTN_DECODE_B64)
        btn_decode.clicked.connect(self.decode_zip_from_base64)
        btn_row.addWidget(btn_decode)

        self.btn_save_zip = QPushButton(self.UI_STRINGS.BTN_SAVE_ZIP)
        self.btn_save_zip.setEnabled(False)
        self.btn_save_zip.clicked.connect(self.save_decoded_zip)
        btn_row.addWidget(self.btn_save_zip)

        btn_clear = QPushButton(self.UI_STRINGS.BTN_CLEAR_B64_INPUT)
        btn_clear.clicked.connect(self.txt_b64_input.clear)
        btn_row.addWidget(btn_clear)

        layout.addLayout(btn_row)

        self.tree_entries = QTreeWidget()
        self.tree_entries.setHeaderLabel("Archive Contents")
        layout.addWidget(self.tree_entries)

        self.tabs.addTab(self.tab_b64_to_zip, self.UI_STRINGS.TAB_B64_TO_ZIP)

    def decode_zip_from_base64(self) -> None:
        text = self.txt_b64_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(
                self, self.UI_STRINGS.ERR_DECODE_FAILED_TITLE, self.UI_STRINGS.ERR_INVALID_ZIP_MSG
            )
            return

        self.progress.setRange(0, 0)
        self.progress.setVisible(True)
        self.tree_entries.clear()
        self.btn_save_zip.setEnabled(False)

        self.decode_thread = QThread()
        self.decode_worker = DecodeWorker(text)
        self.decode_worker.moveToThread(self.decode_thread)
        self.decode_thread.started.connect(self.decode_worker.run_decode)
        self.decode_worker.decoding_successful.connect(self._on_decode_success)
        self.decode_worker.decoding_failed.connect(self._on_decode_fail)
        self.decode_worker.finished.connect(self.decode_thread.quit)
        self.decode_worker.finished.connect(self.decode_worker.deleteLater)
        self.decode_thread.finished.connect(self.decode_thread.deleteLater)
        self.decode_thread.finished.connect(lambda: self.progress.setVisible(False))
        self.decode_thread.start()

    def _on_decode_success(self, data: bytes, names: List[str]) -> None:
        self.decoded_zip_data = data
        for name in names:
            QTreeWidgetItem(self.tree_entries, [name])
        self.btn_save_zip.setEnabled(True)

    def _on_decode_fail(self, msg: str) -> None:  # pragma: no cover - UI path
        QMessageBox.critical(self, self.UI_STRINGS.ERR_DECODE_FAILED_TITLE, msg)

    def save_decoded_zip(self) -> None:  # pragma: no cover - UI path
        if not self.decoded_zip_data:
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.UI_STRINGS.BTN_SAVE_ZIP,
            "",
            "ZIP Files (*.zip);;All Files (*)",
        )
        if not file_path:
            return
        try:
            with open(file_path, "wb") as fh:
                fh.write(self.decoded_zip_data)
            QMessageBox.information(
                self, self.UI_STRINGS.INFO_ZIP_SAVED_TITLE, self.UI_STRINGS.INFO_ZIP_SAVED_MSG
            )
        except OSError as exc:  # pragma: no cover - unlikely
            QMessageBox.critical(
                self, self.UI_STRINGS.ERR_DECODE_FAILED_TITLE, str(exc)
            )

