import sys
import base64
import os
import re
import argparse
import binascii
import sqlite3
from pathlib import Path
from datetime import datetime

from secondary_copilot_validator import (
    SecondaryCopilotValidator,
    run_dual_copilot_validation,
)
<<<<<<< HEAD

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QTextEdit, QLabel, QTabWidget, QHBoxLayout,
    QMessageBox, QProgressBar, QLineEdit, QFormLayout
)
=======

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QTextEdit, QLabel, QTabWidget, QHBoxLayout,
    QMessageBox, QProgressBar, QLineEdit, QFormLayout
)
>>>>>>> e58bf1982f62d575da5b851d7dfd7f30682e5195
from PyQt6.QtGui import (
    QPixmap,
    QDragEnterEvent,
    QDropEvent,
    QDragLeaveEvent,
    QResizeEvent,
    QIntValidator,
)
<<<<<<< HEAD
from PyQt6.QtCore import Qt, QByteArray, QMimeData, QUrl, QSize, QObject, QThread, pyqtSignal

=======
from PyQt6.QtCore import Qt, QByteArray, QMimeData, QUrl, QSize, QObject, QThread, pyqtSignal

>>>>>>> e58bf1982f62d575da5b851d7dfd7f30682e5195
from typing import Optional, List, Tuple

TEXT_INDICATORS = {
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "validation": "[VALIDATION]",
}


def log_metrics(event: str, status: str) -> None:
    """Record encode/decode metrics in ``analytics.db``."""

    analytics = Path(__file__).resolve().parents[2] / "databases" / "analytics.db"
    analytics.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS script_metrics (script TEXT, event TEXT, status TEXT, ts TEXT)"
        )
        conn.execute(
            "INSERT INTO script_metrics VALUES (?, ?, ?, ?)",
            (
                "Base64ImageTransformer",
                event,
                status,
                datetime.utcnow().isoformat(),
            ),
        )


def _run_secondary_validation() -> bool:
    validator = SecondaryCopilotValidator()
    return validator.validate_corrections([__file__])
<<<<<<< HEAD


class EncodeWorker(QObject):
    """
    Worker object to perform file encoding to Base64 in a separate thread.
    """
    encoding_successful = pyqtSignal(str)
    encoding_failed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path

    def run_encode(self) -> None:
        """Reads a file and encodes its content to a Base64 string."""
        try:
            with open(self.file_path, 'rb') as f:
                data: bytes = f.read()
            b64_str: str = base64.b64encode(data).decode('utf-8')
            self.encoding_successful.emit(b64_str)
        except FileNotFoundError:
            self.encoding_failed.emit(Base64ImageTransformer.UI_STRINGS.ERR_FILE_NOT_FOUND_MSG.format(filepath=self.file_path))
        except IOError as e:
            self.encoding_failed.emit(Base64ImageTransformer.UI_STRINGS.ERR_IO_MSG.format(error=e))
        except Exception as e:
            self.encoding_failed.emit(Base64ImageTransformer.UI_STRINGS.ERR_ENCODE_FAILED_MSG.format(error=e))
        finally:
            self.finished.emit()


class DecodeWorker(QObject):
    """
    Worker object to perform Base64 decoding in a separate thread.
    """
    decoding_successful = pyqtSignal(bytes)
    decoding_failed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, b64_text: str):
        super().__init__()
        self.b64_text = b64_text

    def run_decode(self) -> None:
        """Performs the Base64 decoding."""
        try:
            decoded_data = base64.b64decode(self.b64_text, validate=True)
            self.decoding_successful.emit(decoded_data)
        except binascii.Error:
            self.decoding_failed.emit(Base64ImageTransformer.UI_STRINGS.ERR_INVALID_B64_MSG)
        except Exception as e:
            self.decoding_failed.emit(Base64ImageTransformer.UI_STRINGS.ERR_DECODE_FAILED_MSG.format(error=e))
        finally:
            self.finished.emit()
            self.finished.emit()


class Base64ImageTransformer(QWidget):
    """
    Main application window for transforming files to Base64 strings and vice-versa.
    """

    class UI_STRINGS:
        """Container for UI string constants."""
        WINDOW_TITLE: str = "Base64 File Transformer"
        TAB_FILE_TO_B64: str = "File to Base64"
        TAB_B64_TO_IMG: str = "Base64 to Image"
        BTN_SELECT_FILE: str = "Select File"
        BTN_COPY_B64: str = "Copy Base64 to Clipboard"
        BTN_CLEAR_B64_OUTPUT: str = "Clear Output"
        BTN_DECODE_B64: str = "Decode to Image"
        BTN_SAVE_IMG: str = "Save Image As..."
        BTN_CLEAR_B64_INPUT: str = "Clear Base64 Input"
        BTN_CLEAR_DECODED_IMAGE: str = "Clear Image"
        BTN_SET_PREVIEW_SIZE: str = "Set Max Preview Size"
        BTN_CLEAR_PREVIEW_SIZE: str = "Clear Custom Size"
        LBL_MAX_WIDTH: str = "Max Width:"
        LBL_MAX_HEIGHT: str = "Max Height:"
        LBL_DRAG_DROP_DEFAULT: str = "Drag & drop any file or select."
        LBL_DRAG_DROP_VALID: str = "Release to encode file."
        LBL_DRAG_DROP_INVALID_TYPE: str = "Cannot process this item. Drop a file."
        LBL_DRAG_DROP_NO_URL: str = "No file information in drag event."

        DIALOG_SELECT_FILE_TITLE: str = "Select File to Encode"
        DIALOG_ALL_FILES_FILTER: str = "All Files (*.*)"
        DIALOG_IMAGE_FILES_FILTER: str = "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        DIALOG_SAVE_IMAGE_TITLE: str = "Save Image As..."
        DIALOG_SAVE_IMAGE_FILTER: str = "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;BMP Files (*.bmp);;All Files (*)"
        INFO_COPIED_TITLE: str = "Copied"
        INFO_COPIED_MSG: str = "Base64 string copied to clipboard."
        INFO_IMAGE_SAVED_TITLE: str = "Saved"
        INFO_IMAGE_SAVED_MSG: str = "Image saved successfully."
        INFO_PREVIEW_SIZE_SET_TITLE: str = "Preview Size Set"
        INFO_PREVIEW_SIZE_SET_MSG: str = "Maximum preview size updated. Image will rescale if present."
        INFO_PREVIEW_SIZE_CLEARED_TITLE: str = "Preview Size Cleared"
        INFO_PREVIEW_SIZE_CLEARED_MSG: str = "Custom preview size cleared. Image will scale to fit window if present."
        WARN_INPUT_REQUIRED_TITLE: str = "Input Required"
        WARN_INPUT_REQUIRED_MSG: str = "Please enter a Base64 string."
        WARN_NO_IMAGE_TO_SAVE_TITLE: str = "No Image"
        WARN_NO_IMAGE_TO_SAVE_MSG: str = "No image has been decoded to save."
        WARN_INVALID_DROP_FILE: str = "Invalid File"
        WARN_INVALID_DROP_MSG: str = "Please drop a valid file."
        WARN_INVALID_B64_FORMAT_TITLE: str = "Invalid Format"
        WARN_INVALID_B64_FORMAT_MSG: str = (
            "The input string does not appear to be a valid Base64 format. "
            "It may contain invalid characters or have an incorrect length/padding."
        )
        WARN_INVALID_PREVIEW_SIZE_TITLE: str = "Invalid Size"
        WARN_INVALID_PREVIEW_SIZE_MSG: str = "Please enter positive integer values for both width and height."
        ERR_ENCODE_FAILED_TITLE: str = "Encoding Error"
        ERR_ENCODE_FAILED_MSG: str = "Failed to encode file: {error}"
        ERR_DECODE_FAILED_TITLE: str = "Decoding Error"
        ERR_DECODE_FAILED_MSG: str = "Failed to decode Base64: {error}"
        ERR_SAVE_FAILED_TITLE: str = "Save Error"
        ERR_SAVE_FAILED_MSG: str = "Failed to save image: {error}"
        ERR_FILE_NOT_FOUND_MSG: str = "File not found: {filepath}"
        ERR_IO_MSG: str = "An I/O error occurred: {error}"
        ERR_INVALID_B64_MSG: str = "Invalid Base64 string: The input is not a valid Base64 encoded string."

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(self.UI_STRINGS.WINDOW_TITLE)
        self.resize(900, 600)
        self.setAcceptDrops(True)

        self.last_file_selection_dir: str = ""
        self.last_image_save_dir: str = ""

        self.decoded_image_data: Optional[bytes] = None
        self.original_decoded_pixmap: Optional[QPixmap] = None
        self.custom_preview_size: Optional[QSize] = None
        
        self.encode_thread: Optional[QThread] = None
        self.encode_worker: Optional[EncodeWorker] = None
        self.decode_thread: Optional[QThread] = None
        self.decode_worker: Optional[DecodeWorker] = None

        main_layout: QVBoxLayout = QVBoxLayout(self)
        self.tabs: QTabWidget = QTabWidget()
        main_layout.addWidget(self.tabs)

        self._init_file_to_b64_tab()
        self._init_b64_to_img_tab()

        self.progress: QProgressBar = QProgressBar()
        self.progress.setVisible(False)
        main_layout.addWidget(self.progress)

        self.tab_file_to_b64.setStyleSheet("QWidget { background-color: white; }")


    def _init_file_to_b64_tab(self) -> None:
        self.tab_file_to_b64: QWidget = QWidget()
        layout: QVBoxLayout = QVBoxLayout(self.tab_file_to_b64)

        self.btn_select_file: QPushButton = QPushButton(self.UI_STRINGS.BTN_SELECT_FILE)
        self.btn_select_file.clicked.connect(self.select_file_for_encoding)
        layout.addWidget(self.btn_select_file)

        self.lbl_drag_drop_status: QLabel = QLabel(self.UI_STRINGS.LBL_DRAG_DROP_DEFAULT)
        self.lbl_drag_drop_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_drag_drop_status)

        self.txt_b64_output: QTextEdit = QTextEdit()
        self.txt_b64_output.setReadOnly(True)
        self.txt_b64_output.textChanged.connect(self._update_copy_button_state)
        layout.addWidget(self.txt_b64_output)

        b64_output_btn_layout: QHBoxLayout = QHBoxLayout()
        self.btn_copy_b64_output: QPushButton = QPushButton(self.UI_STRINGS.BTN_COPY_B64)
        self.btn_copy_b64_output.clicked.connect(self.copy_b64)
        self.btn_copy_b64_output.setEnabled(False)
        b64_output_btn_layout.addWidget(self.btn_copy_b64_output)

        btn_clear_output: QPushButton = QPushButton(self.UI_STRINGS.BTN_CLEAR_B64_OUTPUT)
        btn_clear_output.clicked.connect(self.clear_file_to_b64_output)
        b64_output_btn_layout.addWidget(btn_clear_output)
        layout.addLayout(b64_output_btn_layout)

        layout.addStretch()
        self.tabs.addTab(self.tab_file_to_b64, self.UI_STRINGS.TAB_FILE_TO_B64)

    def _init_b64_to_img_tab(self) -> None:
        self.tab_b64_to_img: QWidget = QWidget()
        layout: QVBoxLayout = QVBoxLayout(self.tab_b64_to_img)

        self.txt_b64_input: QTextEdit = QTextEdit()
        self.txt_b64_input.setPlaceholderText("Paste Base64 string here...")
        layout.addWidget(self.txt_b64_input)

        decode_btn_layout: QHBoxLayout = QHBoxLayout()
        self.btn_decode: QPushButton = QPushButton(self.UI_STRINGS.BTN_DECODE_B64)
        self.btn_decode.clicked.connect(self.decode_b64)
        decode_btn_layout.addWidget(self.btn_decode)

        btn_clear_input: QPushButton = QPushButton(self.UI_STRINGS.BTN_CLEAR_B64_INPUT)
        btn_clear_input.clicked.connect(self.clear_b64_input)
        decode_btn_layout.addWidget(btn_clear_input)
        layout.addLayout(decode_btn_layout)

        preview_size_form_layout: QFormLayout = QFormLayout()
        self.txt_max_width: QLineEdit = QLineEdit()
        self.txt_max_width.setPlaceholderText("e.g., 800")
        self.txt_max_width.setValidator(QIntValidator(1, 9999))
        preview_size_form_layout.addRow(self.UI_STRINGS.LBL_MAX_WIDTH, self.txt_max_width)

        self.txt_max_height: QLineEdit = QLineEdit()
        self.txt_max_height.setPlaceholderText("e.g., 600")
        self.txt_max_height.setValidator(QIntValidator(1, 9999))
        preview_size_form_layout.addRow(self.UI_STRINGS.LBL_MAX_HEIGHT, self.txt_max_height)
        layout.addLayout(preview_size_form_layout)

        preview_size_btn_layout: QHBoxLayout = QHBoxLayout()
        btn_set_preview_size: QPushButton = QPushButton(self.UI_STRINGS.BTN_SET_PREVIEW_SIZE)
        btn_set_preview_size.clicked.connect(self.set_custom_preview_size)
        preview_size_btn_layout.addWidget(btn_set_preview_size)

        btn_clear_preview_size: QPushButton = QPushButton(self.UI_STRINGS.BTN_CLEAR_PREVIEW_SIZE)
        btn_clear_preview_size.clicked.connect(self.clear_custom_preview_size)
        preview_size_btn_layout.addWidget(btn_clear_preview_size)
        layout.addLayout(preview_size_btn_layout)

        self.lbl_image: QLabel = QLabel()
        self.lbl_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_image.setMinimumSize(200, 200)
        layout.addWidget(self.lbl_image, stretch=1)

        save_clear_img_btn_layout: QHBoxLayout = QHBoxLayout()
        btn_save_image: QPushButton = QPushButton(self.UI_STRINGS.BTN_SAVE_IMG)
        btn_save_image.clicked.connect(self.save_decoded_image)
        save_clear_img_btn_layout.addWidget(btn_save_image)

        btn_clear_decoded_image: QPushButton = QPushButton(self.UI_STRINGS.BTN_CLEAR_DECODED_IMAGE)
        btn_clear_decoded_image.clicked.connect(self.clear_b64_to_img_output)
        save_clear_img_btn_layout.addWidget(btn_clear_decoded_image)
        layout.addLayout(save_clear_img_btn_layout)

        layout.addStretch()
        self.tabs.addTab(self.tab_b64_to_img, self.UI_STRINGS.TAB_B64_TO_IMG)

    def _update_copy_button_state(self) -> None:
        """Enable or disable the 'Copy Base64' button based on output text content."""
        is_empty = not self.txt_b64_output.toPlainText()
        self.btn_copy_b64_output.setEnabled(not is_empty)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag enter events, primarily for file-to-Base64 tab."""
        mime_data: Optional[QMimeData] = event.mimeData()
        current_tab = self.tabs.currentWidget()

        if current_tab == self.tab_file_to_b64:
            if mime_data and mime_data.hasUrls():
                event.acceptProposedAction()
                self.tab_file_to_b64.setStyleSheet("QWidget { background-color: lightgreen; border: 2px dashed green; }")
                self.lbl_drag_drop_status.setText(self.UI_STRINGS.LBL_DRAG_DROP_VALID)
                return
            else:
                event.ignore()
                self.tab_file_to_b64.setStyleSheet("QWidget { background-color: lightcoral; border: 2px dashed red; }")
                self.lbl_drag_drop_status.setText(self.UI_STRINGS.LBL_DRAG_DROP_INVALID_TYPE)
        else:
            event.ignore()
            self.tab_file_to_b64.setStyleSheet("QWidget { background-color: white; }")
            self.lbl_drag_drop_status.setText(self.UI_STRINGS.LBL_DRAG_DROP_DEFAULT)


    def dragLeaveEvent(self, event: QDragLeaveEvent) -> None:
        """Reset UI elements when a drag operation leaves the widget."""
        self.tab_file_to_b64.setStyleSheet("QWidget { background-color: white; }")
        self.lbl_drag_drop_status.setText(self.UI_STRINGS.LBL_DRAG_DROP_DEFAULT)
        super().dragLeaveEvent(event)


    def dropEvent(self, event: QDropEvent) -> None:
        """Handle drop events, primarily for file-to-Base64 tab."""
        self.tab_file_to_b64.setStyleSheet("QWidget { background-color: white; }")
        self.lbl_drag_drop_status.setText(self.UI_STRINGS.LBL_DRAG_DROP_DEFAULT)

        mime_data: Optional[QMimeData] = event.mimeData()
        if self.tabs.currentWidget() == self.tab_file_to_b64:
            if mime_data and mime_data.hasUrls():
                urls: List[QUrl] = mime_data.urls()
                if urls:
                    file_path: str = urls[0].toLocalFile()
                    self._start_encode_file_to_base64(file_path)
                    event.acceptProposedAction()
                    return
            event.ignore()
            QMessageBox.warning(self, self.UI_STRINGS.WARN_INVALID_DROP_FILE, self.UI_STRINGS.WARN_INVALID_DROP_MSG)
        else:
            event.ignore()

    def select_file_for_encoding(self) -> None:
        """Open a file dialog to select any file for Base64 encoding."""
        options = QFileDialog.Option(0)
        file_path_tuple: Tuple[str, str] = QFileDialog.getOpenFileName(
            self,
            self.UI_STRINGS.DIALOG_SELECT_FILE_TITLE,
            self.last_file_selection_dir,
            self.UI_STRINGS.DIALOG_ALL_FILES_FILTER,
            options=options
        )
        file_path: str = file_path_tuple[0]
        if file_path:
            self.last_file_selection_dir = os.path.dirname(file_path)
            self._start_encode_file_to_base64(file_path)

    def _start_encode_file_to_base64(self, file_path: str) -> None:
        """Initiates the file encoding process in a background thread."""
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.btn_select_file.setEnabled(False)
        QApplication.processEvents()

        self.encode_thread = QThread()
        self.encode_worker = EncodeWorker(file_path)
        self.encode_worker.moveToThread(self.encode_thread)

        self.encode_worker.encoding_successful.connect(self._handle_encoding_success)
        self.encode_worker.encoding_failed.connect(self._handle_encoding_failure)
        
        self.encode_worker.finished.connect(self.encode_thread.quit)
        self.encode_worker.finished.connect(self.encode_worker.deleteLater)
        self.encode_thread.finished.connect(self.encode_thread.deleteLater)
        self.encode_thread.finished.connect(self._on_encode_thread_finished)

        self.encode_thread.started.connect(self.encode_worker.run_encode)
        self.encode_thread.start()

    def _on_encode_thread_finished(self) -> None:
        """Handles cleanup and UI updates after the encode thread finishes."""
        self.progress.setVisible(False)
        self.progress.setRange(0, 100)
        self.btn_select_file.setEnabled(True)
        self.encode_thread = None
        self.encode_worker = None

=======


class EncodeWorker(QObject):
    """
    Worker object to perform file encoding to Base64 in a separate thread.
    """
    encoding_successful = pyqtSignal(str)
    encoding_failed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path

    def run_encode(self) -> None:
        """Reads a file and encodes its content to a Base64 string."""
        try:
            with open(self.file_path, 'rb') as f:
                data: bytes = f.read()
            b64_str: str = base64.b64encode(data).decode('utf-8')
            self.encoding_successful.emit(b64_str)
        except FileNotFoundError:
            self.encoding_failed.emit(Base64ImageTransformer.UI_STRINGS.ERR_FILE_NOT_FOUND_MSG.format(filepath=self.file_path))
        except IOError as e:
            self.encoding_failed.emit(Base64ImageTransformer.UI_STRINGS.ERR_IO_MSG.format(error=e))
        except Exception as e:
            self.encoding_failed.emit(Base64ImageTransformer.UI_STRINGS.ERR_ENCODE_FAILED_MSG.format(error=e))
        finally:
            self.finished.emit()


class DecodeWorker(QObject):
    """
    Worker object to perform Base64 decoding in a separate thread.
    """
    decoding_successful = pyqtSignal(bytes)
    decoding_failed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, b64_text: str):
        super().__init__()
        self.b64_text = b64_text

    def run_decode(self) -> None:
        """Performs the Base64 decoding."""
        try:
            decoded_data = base64.b64decode(self.b64_text, validate=True)
            self.decoding_successful.emit(decoded_data)
        except binascii.Error:
            self.decoding_failed.emit(Base64ImageTransformer.UI_STRINGS.ERR_INVALID_B64_MSG)
        except Exception as e:
            self.decoding_failed.emit(Base64ImageTransformer.UI_STRINGS.ERR_DECODE_FAILED_MSG.format(error=e))
        finally:
            self.finished.emit()
            self.finished.emit()


class Base64ImageTransformer(QWidget):
    """
    Main application window for transforming files to Base64 strings and vice-versa.
    """

    class UI_STRINGS:
        """Container for UI string constants."""
        WINDOW_TITLE: str = "Base64 File Transformer"
        TAB_FILE_TO_B64: str = "File to Base64"
        TAB_B64_TO_IMG: str = "Base64 to Image"
        BTN_SELECT_FILE: str = "Select File"
        BTN_COPY_B64: str = "Copy Base64 to Clipboard"
        BTN_CLEAR_B64_OUTPUT: str = "Clear Output"
        BTN_DECODE_B64: str = "Decode to Image"
        BTN_SAVE_IMG: str = "Save Image As..."
        BTN_CLEAR_B64_INPUT: str = "Clear Base64 Input"
        BTN_CLEAR_DECODED_IMAGE: str = "Clear Image"
        BTN_SET_PREVIEW_SIZE: str = "Set Max Preview Size"
        BTN_CLEAR_PREVIEW_SIZE: str = "Clear Custom Size"
        LBL_MAX_WIDTH: str = "Max Width:"
        LBL_MAX_HEIGHT: str = "Max Height:"
        LBL_DRAG_DROP_DEFAULT: str = "Drag & drop any file or select."
        LBL_DRAG_DROP_VALID: str = "Release to encode file."
        LBL_DRAG_DROP_INVALID_TYPE: str = "Cannot process this item. Drop a file."
        LBL_DRAG_DROP_NO_URL: str = "No file information in drag event."

        DIALOG_SELECT_FILE_TITLE: str = "Select File to Encode"
        DIALOG_ALL_FILES_FILTER: str = "All Files (*.*)"
        DIALOG_IMAGE_FILES_FILTER: str = "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        DIALOG_SAVE_IMAGE_TITLE: str = "Save Image As..."
        DIALOG_SAVE_IMAGE_FILTER: str = "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;BMP Files (*.bmp);;All Files (*)"
        INFO_COPIED_TITLE: str = "Copied"
        INFO_COPIED_MSG: str = "Base64 string copied to clipboard."
        INFO_IMAGE_SAVED_TITLE: str = "Saved"
        INFO_IMAGE_SAVED_MSG: str = "Image saved successfully."
        INFO_PREVIEW_SIZE_SET_TITLE: str = "Preview Size Set"
        INFO_PREVIEW_SIZE_SET_MSG: str = "Maximum preview size updated. Image will rescale if present."
        INFO_PREVIEW_SIZE_CLEARED_TITLE: str = "Preview Size Cleared"
        INFO_PREVIEW_SIZE_CLEARED_MSG: str = "Custom preview size cleared. Image will scale to fit window if present."
        WARN_INPUT_REQUIRED_TITLE: str = "Input Required"
        WARN_INPUT_REQUIRED_MSG: str = "Please enter a Base64 string."
        WARN_NO_IMAGE_TO_SAVE_TITLE: str = "No Image"
        WARN_NO_IMAGE_TO_SAVE_MSG: str = "No image has been decoded to save."
        WARN_INVALID_DROP_FILE: str = "Invalid File"
        WARN_INVALID_DROP_MSG: str = "Please drop a valid file."
        WARN_INVALID_B64_FORMAT_TITLE: str = "Invalid Format"
        WARN_INVALID_B64_FORMAT_MSG: str = (
            "The input string does not appear to be a valid Base64 format. "
            "It may contain invalid characters or have an incorrect length/padding."
        )
        WARN_INVALID_PREVIEW_SIZE_TITLE: str = "Invalid Size"
        WARN_INVALID_PREVIEW_SIZE_MSG: str = "Please enter positive integer values for both width and height."
        ERR_ENCODE_FAILED_TITLE: str = "Encoding Error"
        ERR_ENCODE_FAILED_MSG: str = "Failed to encode file: {error}"
        ERR_DECODE_FAILED_TITLE: str = "Decoding Error"
        ERR_DECODE_FAILED_MSG: str = "Failed to decode Base64: {error}"
        ERR_SAVE_FAILED_TITLE: str = "Save Error"
        ERR_SAVE_FAILED_MSG: str = "Failed to save image: {error}"
        ERR_FILE_NOT_FOUND_MSG: str = "File not found: {filepath}"
        ERR_IO_MSG: str = "An I/O error occurred: {error}"
        ERR_INVALID_B64_MSG: str = "Invalid Base64 string: The input is not a valid Base64 encoded string."

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(self.UI_STRINGS.WINDOW_TITLE)
        self.resize(900, 600)
        self.setAcceptDrops(True)

        self.last_file_selection_dir: str = ""
        self.last_image_save_dir: str = ""

        self.decoded_image_data: Optional[bytes] = None
        self.original_decoded_pixmap: Optional[QPixmap] = None
        self.custom_preview_size: Optional[QSize] = None
        
        self.encode_thread: Optional[QThread] = None
        self.encode_worker: Optional[EncodeWorker] = None
        self.decode_thread: Optional[QThread] = None
        self.decode_worker: Optional[DecodeWorker] = None

        main_layout: QVBoxLayout = QVBoxLayout(self)
        self.tabs: QTabWidget = QTabWidget()
        main_layout.addWidget(self.tabs)

        self._init_file_to_b64_tab()
        self._init_b64_to_img_tab()

        self.progress: QProgressBar = QProgressBar()
        self.progress.setVisible(False)
        main_layout.addWidget(self.progress)

        self.tab_file_to_b64.setStyleSheet("QWidget { background-color: white; }")


    def _init_file_to_b64_tab(self) -> None:
        self.tab_file_to_b64: QWidget = QWidget()
        layout: QVBoxLayout = QVBoxLayout(self.tab_file_to_b64)

        self.btn_select_file: QPushButton = QPushButton(self.UI_STRINGS.BTN_SELECT_FILE)
        self.btn_select_file.clicked.connect(self.select_file_for_encoding)
        layout.addWidget(self.btn_select_file)

        self.lbl_drag_drop_status: QLabel = QLabel(self.UI_STRINGS.LBL_DRAG_DROP_DEFAULT)
        self.lbl_drag_drop_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_drag_drop_status)

        self.txt_b64_output: QTextEdit = QTextEdit()
        self.txt_b64_output.setReadOnly(True)
        self.txt_b64_output.textChanged.connect(self._update_copy_button_state)
        layout.addWidget(self.txt_b64_output)

        b64_output_btn_layout: QHBoxLayout = QHBoxLayout()
        self.btn_copy_b64_output: QPushButton = QPushButton(self.UI_STRINGS.BTN_COPY_B64)
        self.btn_copy_b64_output.clicked.connect(self.copy_b64)
        self.btn_copy_b64_output.setEnabled(False)
        b64_output_btn_layout.addWidget(self.btn_copy_b64_output)

        btn_clear_output: QPushButton = QPushButton(self.UI_STRINGS.BTN_CLEAR_B64_OUTPUT)
        btn_clear_output.clicked.connect(self.clear_file_to_b64_output)
        b64_output_btn_layout.addWidget(btn_clear_output)
        layout.addLayout(b64_output_btn_layout)

        layout.addStretch()
        self.tabs.addTab(self.tab_file_to_b64, self.UI_STRINGS.TAB_FILE_TO_B64)

    def _init_b64_to_img_tab(self) -> None:
        self.tab_b64_to_img: QWidget = QWidget()
        layout: QVBoxLayout = QVBoxLayout(self.tab_b64_to_img)

        self.txt_b64_input: QTextEdit = QTextEdit()
        self.txt_b64_input.setPlaceholderText("Paste Base64 string here...")
        layout.addWidget(self.txt_b64_input)

        decode_btn_layout: QHBoxLayout = QHBoxLayout()
        self.btn_decode: QPushButton = QPushButton(self.UI_STRINGS.BTN_DECODE_B64)
        self.btn_decode.clicked.connect(self.decode_b64)
        decode_btn_layout.addWidget(self.btn_decode)

        btn_clear_input: QPushButton = QPushButton(self.UI_STRINGS.BTN_CLEAR_B64_INPUT)
        btn_clear_input.clicked.connect(self.clear_b64_input)
        decode_btn_layout.addWidget(btn_clear_input)
        layout.addLayout(decode_btn_layout)

        preview_size_form_layout: QFormLayout = QFormLayout()
        self.txt_max_width: QLineEdit = QLineEdit()
        self.txt_max_width.setPlaceholderText("e.g., 800")
        self.txt_max_width.setValidator(QIntValidator(1, 9999))
        preview_size_form_layout.addRow(self.UI_STRINGS.LBL_MAX_WIDTH, self.txt_max_width)

        self.txt_max_height: QLineEdit = QLineEdit()
        self.txt_max_height.setPlaceholderText("e.g., 600")
        self.txt_max_height.setValidator(QIntValidator(1, 9999))
        preview_size_form_layout.addRow(self.UI_STRINGS.LBL_MAX_HEIGHT, self.txt_max_height)
        layout.addLayout(preview_size_form_layout)

        preview_size_btn_layout: QHBoxLayout = QHBoxLayout()
        btn_set_preview_size: QPushButton = QPushButton(self.UI_STRINGS.BTN_SET_PREVIEW_SIZE)
        btn_set_preview_size.clicked.connect(self.set_custom_preview_size)
        preview_size_btn_layout.addWidget(btn_set_preview_size)

        btn_clear_preview_size: QPushButton = QPushButton(self.UI_STRINGS.BTN_CLEAR_PREVIEW_SIZE)
        btn_clear_preview_size.clicked.connect(self.clear_custom_preview_size)
        preview_size_btn_layout.addWidget(btn_clear_preview_size)
        layout.addLayout(preview_size_btn_layout)

        self.lbl_image: QLabel = QLabel()
        self.lbl_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_image.setMinimumSize(200, 200)
        layout.addWidget(self.lbl_image, stretch=1)

        save_clear_img_btn_layout: QHBoxLayout = QHBoxLayout()
        btn_save_image: QPushButton = QPushButton(self.UI_STRINGS.BTN_SAVE_IMG)
        btn_save_image.clicked.connect(self.save_decoded_image)
        save_clear_img_btn_layout.addWidget(btn_save_image)

        btn_clear_decoded_image: QPushButton = QPushButton(self.UI_STRINGS.BTN_CLEAR_DECODED_IMAGE)
        btn_clear_decoded_image.clicked.connect(self.clear_b64_to_img_output)
        save_clear_img_btn_layout.addWidget(btn_clear_decoded_image)
        layout.addLayout(save_clear_img_btn_layout)

        layout.addStretch()
        self.tabs.addTab(self.tab_b64_to_img, self.UI_STRINGS.TAB_B64_TO_IMG)

    def _update_copy_button_state(self) -> None:
        """Enable or disable the 'Copy Base64' button based on output text content."""
        is_empty = not self.txt_b64_output.toPlainText()
        self.btn_copy_b64_output.setEnabled(not is_empty)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag enter events, primarily for file-to-Base64 tab."""
        mime_data: Optional[QMimeData] = event.mimeData()
        current_tab = self.tabs.currentWidget()

        if current_tab == self.tab_file_to_b64:
            if mime_data and mime_data.hasUrls():
                event.acceptProposedAction()
                self.tab_file_to_b64.setStyleSheet("QWidget { background-color: lightgreen; border: 2px dashed green; }")
                self.lbl_drag_drop_status.setText(self.UI_STRINGS.LBL_DRAG_DROP_VALID)
                return
            else:
                event.ignore()
                self.tab_file_to_b64.setStyleSheet("QWidget { background-color: lightcoral; border: 2px dashed red; }")
                self.lbl_drag_drop_status.setText(self.UI_STRINGS.LBL_DRAG_DROP_INVALID_TYPE)
        else:
            event.ignore()
            self.tab_file_to_b64.setStyleSheet("QWidget { background-color: white; }")
            self.lbl_drag_drop_status.setText(self.UI_STRINGS.LBL_DRAG_DROP_DEFAULT)


    def dragLeaveEvent(self, event: QDragLeaveEvent) -> None:
        """Reset UI elements when a drag operation leaves the widget."""
        self.tab_file_to_b64.setStyleSheet("QWidget { background-color: white; }")
        self.lbl_drag_drop_status.setText(self.UI_STRINGS.LBL_DRAG_DROP_DEFAULT)
        super().dragLeaveEvent(event)


    def dropEvent(self, event: QDropEvent) -> None:
        """Handle drop events, primarily for file-to-Base64 tab."""
        self.tab_file_to_b64.setStyleSheet("QWidget { background-color: white; }")
        self.lbl_drag_drop_status.setText(self.UI_STRINGS.LBL_DRAG_DROP_DEFAULT)

        mime_data: Optional[QMimeData] = event.mimeData()
        if self.tabs.currentWidget() == self.tab_file_to_b64:
            if mime_data and mime_data.hasUrls():
                urls: List[QUrl] = mime_data.urls()
                if urls:
                    file_path: str = urls[0].toLocalFile()
                    self._start_encode_file_to_base64(file_path)
                    event.acceptProposedAction()
                    return
            event.ignore()
            QMessageBox.warning(self, self.UI_STRINGS.WARN_INVALID_DROP_FILE, self.UI_STRINGS.WARN_INVALID_DROP_MSG)
        else:
            event.ignore()

    def select_file_for_encoding(self) -> None:
        """Open a file dialog to select any file for Base64 encoding."""
        options = QFileDialog.Option(0)
        file_path_tuple: Tuple[str, str] = QFileDialog.getOpenFileName(
            self,
            self.UI_STRINGS.DIALOG_SELECT_FILE_TITLE,
            self.last_file_selection_dir,
            self.UI_STRINGS.DIALOG_ALL_FILES_FILTER,
            options=options
        )
        file_path: str = file_path_tuple[0]
        if file_path:
            self.last_file_selection_dir = os.path.dirname(file_path)
            self._start_encode_file_to_base64(file_path)

    def _start_encode_file_to_base64(self, file_path: str) -> None:
        """Initiates the file encoding process in a background thread."""
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.btn_select_file.setEnabled(False)
        QApplication.processEvents()

        self.encode_thread = QThread()
        self.encode_worker = EncodeWorker(file_path)
        self.encode_worker.moveToThread(self.encode_thread)

        self.encode_worker.encoding_successful.connect(self._handle_encoding_success)
        self.encode_worker.encoding_failed.connect(self._handle_encoding_failure)
        
        self.encode_worker.finished.connect(self.encode_thread.quit)
        self.encode_worker.finished.connect(self.encode_worker.deleteLater)
        self.encode_thread.finished.connect(self.encode_thread.deleteLater)
        self.encode_thread.finished.connect(self._on_encode_thread_finished)

        self.encode_thread.started.connect(self.encode_worker.run_encode)
        self.encode_thread.start()

    def _on_encode_thread_finished(self) -> None:
        """Handles cleanup and UI updates after the encode thread finishes."""
        self.progress.setVisible(False)
        self.progress.setRange(0, 100)
        self.btn_select_file.setEnabled(True)
        self.encode_thread = None
        self.encode_worker = None

>>>>>>> e58bf1982f62d575da5b851d7dfd7f30682e5195
    def _handle_encoding_success(self, b64_string: str) -> None:
        """Handles successful file encoding."""
        self.txt_b64_output.setPlainText(b64_string)
        try:
            result = run_dual_copilot_validation(lambda: True, _run_secondary_validation)
            if result:
                print(f"{TEXT_INDICATORS['validation']} Encoding validated")
                log_metrics("encode", "success")
            else:
                print(f"{TEXT_INDICATORS['error']} Secondary validation failed")
                log_metrics("encode", "validation_failed")
        except RuntimeError as exc:
            print(f"{TEXT_INDICATORS['error']} Validation error: {exc}")
            log_metrics("encode", "validation_error")
<<<<<<< HEAD

=======

>>>>>>> e58bf1982f62d575da5b851d7dfd7f30682e5195
    def _handle_encoding_failure(self, error_message: str) -> None:
        """Handles failed file encoding."""
        QMessageBox.critical(self, self.UI_STRINGS.ERR_ENCODE_FAILED_TITLE, error_message)
        self.txt_b64_output.clear()
        try:
            run_dual_copilot_validation(lambda: False, _run_secondary_validation)
        except RuntimeError as exc:
            print(f"{TEXT_INDICATORS['error']} Validation error: {exc}")
        log_metrics("encode", "failure")
<<<<<<< HEAD


    def copy_b64(self) -> None:
        """Copies the Base64 output text to the clipboard."""
        b64_text: str = self.txt_b64_output.toPlainText()
        if b64_text:
            clipboard = QApplication.clipboard()
            if clipboard is not None:
                clipboard.setText(b64_text)
                QMessageBox.information(self, self.UI_STRINGS.INFO_COPIED_TITLE, self.UI_STRINGS.INFO_COPIED_MSG)
            else:
                QMessageBox.warning(self, "Clipboard Error", "Clipboard is not available.")

    def clear_file_to_b64_output(self) -> None:
        """Clears the Base64 output text field."""
        self.txt_b64_output.clear()

    def clear_b64_input(self) -> None:
        """Clears the Base64 input text field."""
        self.txt_b64_input.clear()

    def clear_b64_to_img_output(self) -> None:
        """Clears the decoded image preview and associated data."""
        self.lbl_image.clear()
        self.decoded_image_data = None
        self.original_decoded_pixmap = None

    def _is_valid_base64_string(self, s: str) -> bool:
        """Validates if a string is a potentially valid Base64 string."""
        # Uses re.fullmatch for stricter validation against the entire string.
        if not re.fullmatch(r'[A-Za-z0-9+/]*={0,2}', s): # Task N8: Changed from re.match
            return False
        if len(s) % 4 != 0: # Check if length is a multiple of 4
            return False
        return True

    def set_custom_preview_size(self) -> None:
        """Sets a custom maximum size for the image preview area."""
        max_w_str = self.txt_max_width.text()
        max_h_str = self.txt_max_height.text()

        try:
            max_w = int(max_w_str)
            max_h = int(max_h_str)
            if max_w > 0 and max_h > 0:
                self.custom_preview_size = QSize(max_w, max_h)
                QMessageBox.information(self, self.UI_STRINGS.INFO_PREVIEW_SIZE_SET_TITLE,
                                        self.UI_STRINGS.INFO_PREVIEW_SIZE_SET_MSG)
                self._update_displayed_image()
            else:
                raise ValueError("Dimensions must be positive.")
        except ValueError:
            QMessageBox.warning(self, self.UI_STRINGS.WARN_INVALID_PREVIEW_SIZE_TITLE,
                                self.UI_STRINGS.WARN_INVALID_PREVIEW_SIZE_MSG)
            self.custom_preview_size = None

    def clear_custom_preview_size(self) -> None:
        """Clears any custom maximum preview size, reverting to dynamic scaling."""
        self.custom_preview_size = None
        self.txt_max_width.clear()
        self.txt_max_height.clear()
        QMessageBox.information(self, self.UI_STRINGS.INFO_PREVIEW_SIZE_CLEARED_TITLE,
                                self.UI_STRINGS.INFO_PREVIEW_SIZE_CLEARED_MSG)
        self._update_displayed_image()


    def decode_b64(self) -> None:
        """Decodes a Base64 string from input to an image preview."""
        b64_text: str = self.txt_b64_input.toPlainText().strip()
        if not b64_text:
            QMessageBox.warning(self, self.UI_STRINGS.WARN_INPUT_REQUIRED_TITLE, self.UI_STRINGS.WARN_INPUT_REQUIRED_MSG)
            return

        if not self._is_valid_base64_string(b64_text):
            QMessageBox.warning(self, self.UI_STRINGS.WARN_INVALID_B64_FORMAT_TITLE,
                                self.UI_STRINGS.WARN_INVALID_B64_FORMAT_MSG)
            return

        self.progress.setVisible(True)
        self.progress.setRange(0, 0) 
        self.btn_decode.setEnabled(False) 
        QApplication.processEvents()

        self.decode_thread = QThread()
        self.decode_worker = DecodeWorker(b64_text)
        self.decode_worker.moveToThread(self.decode_thread)

        self.decode_worker.decoding_successful.connect(self._handle_decoding_success)
        self.decode_worker.decoding_failed.connect(self._handle_decoding_failure)
        
        self.decode_worker.finished.connect(self.decode_thread.quit)
        self.decode_worker.finished.connect(self.decode_worker.deleteLater)
        self.decode_thread.finished.connect(self.decode_thread.deleteLater)
        self.decode_thread.finished.connect(self._on_decode_thread_finished)

        self.decode_thread.started.connect(self.decode_worker.run_decode)
        self.decode_thread.start()

    def _on_decode_thread_finished(self) -> None:
        """Handles cleanup and UI updates after the decode thread finishes."""
        self.progress.setVisible(False)
        self.progress.setRange(0,100)
        self.btn_decode.setEnabled(True)
        self.decode_thread = None 
        self.decode_worker = None 


=======


    def copy_b64(self) -> None:
        """Copies the Base64 output text to the clipboard."""
        b64_text: str = self.txt_b64_output.toPlainText()
        if b64_text:
            clipboard = QApplication.clipboard()
            if clipboard is not None:
                clipboard.setText(b64_text)
                QMessageBox.information(self, self.UI_STRINGS.INFO_COPIED_TITLE, self.UI_STRINGS.INFO_COPIED_MSG)
            else:
                QMessageBox.warning(self, "Clipboard Error", "Clipboard is not available.")

    def clear_file_to_b64_output(self) -> None:
        """Clears the Base64 output text field."""
        self.txt_b64_output.clear()

    def clear_b64_input(self) -> None:
        """Clears the Base64 input text field."""
        self.txt_b64_input.clear()

    def clear_b64_to_img_output(self) -> None:
        """Clears the decoded image preview and associated data."""
        self.lbl_image.clear()
        self.decoded_image_data = None
        self.original_decoded_pixmap = None

    def _is_valid_base64_string(self, s: str) -> bool:
        """Validates if a string is a potentially valid Base64 string."""
        # Uses re.fullmatch for stricter validation against the entire string.
        if not re.fullmatch(r'[A-Za-z0-9+/]*={0,2}', s): # Task N8: Changed from re.match
            return False
        if len(s) % 4 != 0: # Check if length is a multiple of 4
            return False
        return True

    def set_custom_preview_size(self) -> None:
        """Sets a custom maximum size for the image preview area."""
        max_w_str = self.txt_max_width.text()
        max_h_str = self.txt_max_height.text()

        try:
            max_w = int(max_w_str)
            max_h = int(max_h_str)
            if max_w > 0 and max_h > 0:
                self.custom_preview_size = QSize(max_w, max_h)
                QMessageBox.information(self, self.UI_STRINGS.INFO_PREVIEW_SIZE_SET_TITLE,
                                        self.UI_STRINGS.INFO_PREVIEW_SIZE_SET_MSG)
                self._update_displayed_image()
            else:
                raise ValueError("Dimensions must be positive.")
        except ValueError:
            QMessageBox.warning(self, self.UI_STRINGS.WARN_INVALID_PREVIEW_SIZE_TITLE,
                                self.UI_STRINGS.WARN_INVALID_PREVIEW_SIZE_MSG)
            self.custom_preview_size = None

    def clear_custom_preview_size(self) -> None:
        """Clears any custom maximum preview size, reverting to dynamic scaling."""
        self.custom_preview_size = None
        self.txt_max_width.clear()
        self.txt_max_height.clear()
        QMessageBox.information(self, self.UI_STRINGS.INFO_PREVIEW_SIZE_CLEARED_TITLE,
                                self.UI_STRINGS.INFO_PREVIEW_SIZE_CLEARED_MSG)
        self._update_displayed_image()


    def decode_b64(self) -> None:
        """Decodes a Base64 string from input to an image preview."""
        b64_text: str = self.txt_b64_input.toPlainText().strip()
        if not b64_text:
            QMessageBox.warning(self, self.UI_STRINGS.WARN_INPUT_REQUIRED_TITLE, self.UI_STRINGS.WARN_INPUT_REQUIRED_MSG)
            return

        if not self._is_valid_base64_string(b64_text):
            QMessageBox.warning(self, self.UI_STRINGS.WARN_INVALID_B64_FORMAT_TITLE,
                                self.UI_STRINGS.WARN_INVALID_B64_FORMAT_MSG)
            return

        self.progress.setVisible(True)
        self.progress.setRange(0, 0) 
        self.btn_decode.setEnabled(False) 
        QApplication.processEvents()

        self.decode_thread = QThread()
        self.decode_worker = DecodeWorker(b64_text)
        self.decode_worker.moveToThread(self.decode_thread)

        self.decode_worker.decoding_successful.connect(self._handle_decoding_success)
        self.decode_worker.decoding_failed.connect(self._handle_decoding_failure)
        
        self.decode_worker.finished.connect(self.decode_thread.quit)
        self.decode_worker.finished.connect(self.decode_worker.deleteLater)
        self.decode_thread.finished.connect(self.decode_thread.deleteLater)
        self.decode_thread.finished.connect(self._on_decode_thread_finished)

        self.decode_thread.started.connect(self.decode_worker.run_decode)
        self.decode_thread.start()

    def _on_decode_thread_finished(self) -> None:
        """Handles cleanup and UI updates after the decode thread finishes."""
        self.progress.setVisible(False)
        self.progress.setRange(0,100)
        self.btn_decode.setEnabled(True)
        self.decode_thread = None 
        self.decode_worker = None 


>>>>>>> e58bf1982f62d575da5b851d7dfd7f30682e5195
    def _handle_decoding_success(self, decoded_data: bytes) -> None:
        """Handles successful Base64 decoding."""
        self.decoded_image_data = decoded_data
        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(self.decoded_image_data))
<<<<<<< HEAD
        self.original_decoded_pixmap = pixmap

=======
        self.original_decoded_pixmap = pixmap

>>>>>>> e58bf1982f62d575da5b851d7dfd7f30682e5195
        if self.original_decoded_pixmap is None or self.original_decoded_pixmap.isNull():
            # This indicates the Base64 was valid, but the data wasn't a recognized image format by QPixmap
            self._handle_decoding_failure("Base64 decoded, but data is not a recognized image format for preview.")
            return
        self._update_displayed_image()
        try:
            result = run_dual_copilot_validation(lambda: True, _run_secondary_validation)
            if result:
                print(f"{TEXT_INDICATORS['validation']} Decoding validated")
                log_metrics("decode", "success")
            else:
                print(f"{TEXT_INDICATORS['error']} Secondary validation failed")
                log_metrics("decode", "validation_failed")
        except RuntimeError as exc:
            print(f"{TEXT_INDICATORS['error']} Validation error: {exc}")
            log_metrics("decode", "validation_error")
<<<<<<< HEAD

=======

>>>>>>> e58bf1982f62d575da5b851d7dfd7f30682e5195
    def _handle_decoding_failure(self, error_message: str) -> None:
        """Handles failed Base64 decoding."""
        QMessageBox.critical(self, self.UI_STRINGS.ERR_DECODE_FAILED_TITLE, error_message)
        self.decoded_image_data = None
        self.original_decoded_pixmap = None
        self.lbl_image.clear()
        try:
            run_dual_copilot_validation(lambda: False, _run_secondary_validation)
        except RuntimeError as exc:
            print(f"{TEXT_INDICATORS['error']} Validation error: {exc}")
        log_metrics("decode", "failure")
<<<<<<< HEAD

    def _update_displayed_image(self) -> None:
        """Updates the displayed image preview, scaling it appropriately."""
        if self.original_decoded_pixmap and not self.original_decoded_pixmap.isNull():
            target_size: QSize
            if self.custom_preview_size is not None:
                target_size = self.custom_preview_size
            elif self.lbl_image.width() > 0 and self.lbl_image.height() > 0 :
                target_size = self.lbl_image.size()
            else: 
                target_size = QSize(200,200) 

            scaled_pixmap: QPixmap = self.original_decoded_pixmap.scaled(
                target_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.lbl_image.setPixmap(scaled_pixmap)
        else:
            self.lbl_image.clear()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handles window resize events to update image preview if necessary."""
        super().resizeEvent(event)
        if self.tabs.currentWidget() == self.tab_b64_to_img and self.original_decoded_pixmap and self.custom_preview_size is None:
            self._update_displayed_image()

    def save_decoded_image(self) -> None:
        """Saves the currently decoded image to a file."""
        if not self.decoded_image_data or not self.original_decoded_pixmap:
            QMessageBox.warning(self, self.UI_STRINGS.WARN_NO_IMAGE_TO_SAVE_TITLE, self.UI_STRINGS.WARN_NO_IMAGE_TO_SAVE_MSG)
            return

        options = QFileDialog.Option(0)
        file_path_tuple: Tuple[str, str] = QFileDialog.getSaveFileName(
            self,
            self.UI_STRINGS.DIALOG_SAVE_IMAGE_TITLE,
            self.last_image_save_dir,
            self.UI_STRINGS.DIALOG_SAVE_IMAGE_FILTER, 
            options=options
        )
        file_path: str = file_path_tuple[0]
        selected_filter: str = file_path_tuple[1]

        if file_path:
            self.last_image_save_dir = os.path.dirname(file_path)
            try:
                if "PNG Files" in selected_filter and not file_path.lower().endswith(".png"):
                    file_path += ".png"
                elif "JPEG Files" in selected_filter and not (file_path.lower().endswith(".jpg") or file_path.lower().endswith(".jpeg")):
                    file_path += ".jpg"
                elif "BMP Files" in selected_filter and not file_path.lower().endswith(".bmp"):
                    file_path += ".bmp"

                if not self.original_decoded_pixmap.save(file_path):
                    raise IOError(f"Failed to save pixmap. Check file permissions or path. Format: {os.path.splitext(file_path)[1]}")
                
                QMessageBox.information(self, self.UI_STRINGS.INFO_IMAGE_SAVED_TITLE, self.UI_STRINGS.INFO_IMAGE_SAVED_MSG)
            except Exception as e:
                QMessageBox.critical(self, self.UI_STRINGS.ERR_SAVE_FAILED_TITLE,
                                     self.UI_STRINGS.ERR_SAVE_FAILED_MSG.format(error=e))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Base64 File Transformer GUI application.")
    args = parser.parse_args() 

    app: QApplication = QApplication(sys.argv) 
    window: Base64ImageTransformer = Base64ImageTransformer()
    window.show()
    sys.exit(app.exec())
=======

    def _update_displayed_image(self) -> None:
        """Updates the displayed image preview, scaling it appropriately."""
        if self.original_decoded_pixmap and not self.original_decoded_pixmap.isNull():
            target_size: QSize
            if self.custom_preview_size is not None:
                target_size = self.custom_preview_size
            elif self.lbl_image.width() > 0 and self.lbl_image.height() > 0 :
                target_size = self.lbl_image.size()
            else: 
                target_size = QSize(200,200) 

            scaled_pixmap: QPixmap = self.original_decoded_pixmap.scaled(
                target_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.lbl_image.setPixmap(scaled_pixmap)
        else:
            self.lbl_image.clear()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handles window resize events to update image preview if necessary."""
        super().resizeEvent(event)
        if self.tabs.currentWidget() == self.tab_b64_to_img and self.original_decoded_pixmap and self.custom_preview_size is None:
            self._update_displayed_image()

    def save_decoded_image(self) -> None:
        """Saves the currently decoded image to a file."""
        if not self.decoded_image_data or not self.original_decoded_pixmap:
            QMessageBox.warning(self, self.UI_STRINGS.WARN_NO_IMAGE_TO_SAVE_TITLE, self.UI_STRINGS.WARN_NO_IMAGE_TO_SAVE_MSG)
            return

        options = QFileDialog.Option(0)
        file_path_tuple: Tuple[str, str] = QFileDialog.getSaveFileName(
            self,
            self.UI_STRINGS.DIALOG_SAVE_IMAGE_TITLE,
            self.last_image_save_dir,
            self.UI_STRINGS.DIALOG_SAVE_IMAGE_FILTER, 
            options=options
        )
        file_path: str = file_path_tuple[0]
        selected_filter: str = file_path_tuple[1]

        if file_path:
            self.last_image_save_dir = os.path.dirname(file_path)
            try:
                if "PNG Files" in selected_filter and not file_path.lower().endswith(".png"):
                    file_path += ".png"
                elif "JPEG Files" in selected_filter and not (file_path.lower().endswith(".jpg") or file_path.lower().endswith(".jpeg")):
                    file_path += ".jpg"
                elif "BMP Files" in selected_filter and not file_path.lower().endswith(".bmp"):
                    file_path += ".bmp"

                if not self.original_decoded_pixmap.save(file_path):
                    raise IOError(f"Failed to save pixmap. Check file permissions or path. Format: {os.path.splitext(file_path)[1]}")
                
                QMessageBox.information(self, self.UI_STRINGS.INFO_IMAGE_SAVED_TITLE, self.UI_STRINGS.INFO_IMAGE_SAVED_MSG)
            except Exception as e:
                QMessageBox.critical(self, self.UI_STRINGS.ERR_SAVE_FAILED_TITLE,
                                     self.UI_STRINGS.ERR_SAVE_FAILED_MSG.format(error=e))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Base64 File Transformer GUI application.")
    args = parser.parse_args() 

    app: QApplication = QApplication(sys.argv) 
    window: Base64ImageTransformer = Base64ImageTransformer()
    window.show()
    sys.exit(app.exec())
>>>>>>> e58bf1982f62d575da5b851d7dfd7f30682e5195
