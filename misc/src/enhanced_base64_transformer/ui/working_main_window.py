<<<<<<< HEAD
"""
Working Enhanced Main Window Implementation
Based on the functional legacy code with improved architecture
"""

import sys
import base64
import os
import re
import binascii
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QTextEdit, QLabel, QTabWidget, QMessageBox, 
    QProgressBar, QLineEdit, QFormLayout, QApplication
)
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QDragLeaveEvent, QIntValidator, QAction
from PyQt6.QtCore import Qt, QSize, QObject, QThread, pyqtSignal


class EncodeWorker(QObject):
    """Worker object to perform file encoding to Base64 in a separate thread."""
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
            self.encoding_failed.emit(f"File not found: {self.file_path}")
        except IOError as e:
            self.encoding_failed.emit(f"An I/O error occurred: {e}")
        except Exception as e:
            self.encoding_failed.emit(f"Failed to encode file: {e}")
        finally:
            self.finished.emit()


class DecodeWorker(QObject):
    """Worker object to perform Base64 decoding in a separate thread."""
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
            self.decoding_failed.emit("Invalid Base64 string: The input is not a valid Base64 encoded string.")
        except Exception as e:
            self.decoding_failed.emit(f"Failed to decode Base64: {e}")
        finally:
            self.finished.emit()


class WorkingMainWindow(QMainWindow):
    """
    Working Enhanced Main Window with proper theming and functional buttons
    Based on the legacy code but with improved architecture
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Base64 Image Transformer")
        self.setMinimumSize(900, 600)
        self.setAcceptDrops(True)
        
        # Theme state
        self.is_dark_theme = False
        
        # File paths
        self.last_file_selection_dir = ""
        self.last_image_save_dir = ""
        
        # Image data
        self.decoded_image_data: Optional[bytes] = None
        self.original_decoded_pixmap: Optional[QPixmap] = None
        self.custom_preview_size: Optional[QSize] = None
        
        # Worker threads
        self.encode_thread: Optional[QThread] = None
        self.encode_worker: Optional[EncodeWorker] = None
        self.decode_thread: Optional[QThread] = None
        self.decode_worker: Optional[DecodeWorker] = None
        
        self.setup_ui()
        self.apply_light_theme()
        
    def setup_ui(self):
        """Setup the main window UI"""
        # Menu bar
        self.setup_menu_bar()
        
        # Status bar
        self.status_bar = self.statusBar()
        if self.status_bar:
            self.status_bar.showMessage("Ready")
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Initialize tabs
        self.init_file_to_b64_tab()
        self.init_b64_to_img_tab()
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        main_layout.addWidget(self.progress)
        
        # Footer buttons
        footer_layout = QHBoxLayout()
        
        self.theme_button = QPushButton("Toggle Dark Theme")
        self.theme_button.clicked.connect(self.toggle_theme)
        footer_layout.addWidget(self.theme_button)
        
        footer_layout.addStretch()
        
        help_button = QPushButton("Help")
        help_button.clicked.connect(self.show_help)
        footer_layout.addWidget(help_button)
        
        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(self.close)
        footer_layout.addWidget(exit_button)
        
        main_layout.addLayout(footer_layout)
        
    def setup_menu_bar(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        if not menubar:
            return
            
        # File menu
        file_menu = menubar.addMenu("File")
        if file_menu:
            exit_action = QAction("Exit", self)
            exit_action.setShortcut("Ctrl+Q")
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        if view_menu:
            theme_action = QAction("Toggle Theme", self)
            theme_action.triggered.connect(self.toggle_theme)
            view_menu.addAction(theme_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        if help_menu:
            about_action = QAction("About", self)
            about_action.triggered.connect(self.show_help)
            help_menu.addAction(about_action)
        
    def init_file_to_b64_tab(self):
        """Initialize file to Base64 tab"""
        self.tab_file_to_b64 = QWidget()
        layout = QVBoxLayout(self.tab_file_to_b64)
        
        # Select file button
        self.btn_select_file = QPushButton("Select File")
        self.btn_select_file.clicked.connect(self.select_file_for_encoding)
        layout.addWidget(self.btn_select_file)
        
        # Drag drop status
        self.lbl_drag_drop_status = QLabel("Drag & drop any file or select.")
        self.lbl_drag_drop_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_drag_drop_status)
        
        # Base64 output
        self.txt_b64_output = QTextEdit()
        self.txt_b64_output.setReadOnly(True)
        self.txt_b64_output.textChanged.connect(self.update_copy_button_state)
        layout.addWidget(self.txt_b64_output)
        
        # Output buttons
        output_btn_layout = QHBoxLayout()
        
        self.btn_copy_b64_output = QPushButton("Copy Base64 to Clipboard")
        self.btn_copy_b64_output.clicked.connect(self.copy_b64)
        self.btn_copy_b64_output.setEnabled(False)
        output_btn_layout.addWidget(self.btn_copy_b64_output)
        
        btn_clear_output = QPushButton("Clear Output")
        btn_clear_output.clicked.connect(self.clear_file_to_b64_output)
        output_btn_layout.addWidget(btn_clear_output)
        
        layout.addLayout(output_btn_layout)
        layout.addStretch()
        
        self.tabs.addTab(self.tab_file_to_b64, "File to Base64")
        
    def clear_file_to_b64_output(self):
        """Clear Base64 output in File to Base64 tab"""
        self.txt_b64_output.clear()
        if self.status_bar:
            self.status_bar.showMessage("Output cleared")
    def init_b64_to_img_tab(self):
        """Initialize Base64 to image tab"""
        self.tab_b64_to_img = QWidget()
        layout = QVBoxLayout(self.tab_b64_to_img)
        
        # Base64 input
        self.txt_b64_input = QTextEdit()
        self.txt_b64_input.setPlaceholderText("Paste Base64 string here...")
        layout.addWidget(self.txt_b64_input)
        
        # Decode buttons
        decode_btn_layout = QHBoxLayout()
        
        self.btn_decode = QPushButton("Decode to Image")
        self.btn_decode.clicked.connect(self.decode_b64)
        decode_btn_layout.addWidget(self.btn_decode)
        
        btn_clear_input = QPushButton("Clear Base64 Input")
        btn_clear_input.clicked.connect(self.clear_b64_input)
        decode_btn_layout.addWidget(btn_clear_input)
        
        layout.addLayout(decode_btn_layout)
        
        # Preview size controls
        preview_size_form_layout = QFormLayout()
        
        self.txt_max_width = QLineEdit()
        self.txt_max_width.setPlaceholderText("e.g., 800")
        self.txt_max_width.setValidator(QIntValidator(1, 9999))
        preview_size_form_layout.addRow("Max Width:", self.txt_max_width)
        
        self.txt_max_height = QLineEdit()
        self.txt_max_height.setPlaceholderText("e.g., 600")
        self.txt_max_height.setValidator(QIntValidator(1, 9999))
        preview_size_form_layout.addRow("Max Height:", self.txt_max_height)
        
        layout.addLayout(preview_size_form_layout)
        
        # Preview size buttons
        preview_size_btn_layout = QHBoxLayout()
        
        btn_set_preview_size = QPushButton("Set Max Preview Size")
        btn_set_preview_size.clicked.connect(self.set_custom_preview_size)
        preview_size_btn_layout.addWidget(btn_set_preview_size)
        
        btn_clear_preview_size = QPushButton("Clear Custom Size")
        btn_clear_preview_size.clicked.connect(self.clear_custom_preview_size)
        preview_size_btn_layout.addWidget(btn_clear_preview_size)
        
        layout.addLayout(preview_size_btn_layout)
        
        # Image display
        self.lbl_image = QLabel()
        self.lbl_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_image.setMinimumSize(200, 200)
        layout.addWidget(self.lbl_image, stretch=1)
        
        # Save/clear image buttons
        save_clear_img_btn_layout = QHBoxLayout()
        
        btn_save_image = QPushButton("Save Image As...")
        btn_save_image.clicked.connect(self.save_decoded_image)
        save_clear_img_btn_layout.addWidget(btn_save_image)
        
        btn_clear_decoded_image = QPushButton("Clear Image")
        btn_clear_decoded_image.clicked.connect(self.clear_b64_to_img_output)
        save_clear_img_btn_layout.addWidget(btn_clear_decoded_image)
        
        layout.addLayout(save_clear_img_btn_layout)
        layout.addStretch()
        
        self.tabs.addTab(self.tab_b64_to_img, "Base64 to Image")
        
    def show_status(self, message: str):
        """Show status message if status bar exists"""
        if self.status_bar:
            self.status_bar.showMessage(message)
            
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if self.is_dark_theme:
            self.apply_light_theme()
            self.theme_button.setText("Toggle Dark Theme")
            self.show_status("Switched to light theme")
        else:
            self.apply_dark_theme()
            self.theme_button.setText("Toggle Light Theme")
            self.show_status("Switched to dark theme")
        self.is_dark_theme = not self.is_dark_theme
        
    def apply_light_theme(self):
        """Apply light theme"""
        self.setStyleSheet("")
        
    def apply_dark_theme(self):
        """Apply dark theme"""
        try:
            dark_theme_path = Path(__file__).parent.parent.parent.parent / "resources" / "dark_theme.qss"
            if dark_theme_path.exists():
                with open(dark_theme_path, 'r', encoding='utf-8') as f:
                    dark_qss = f.read()
                self.setStyleSheet(dark_qss)
            else:
                # Fallback dark theme
                dark_style = """
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QWidget {
                    background-color: #3c3c3c;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #4a90e2;
                    color: #ffffff;
                    border: 1px solid #357abd;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #357abd;
                }
                QPushButton:pressed {
                    background-color: #2a5a8a;
                }
                QPushButton:disabled {
                    background-color: #555555;
                    color: #888888;
                }
                QTextEdit {
                    background-color: #404040;
                    color: #ffffff;
                    border: 1px solid #666666;
                    border-radius: 4px;
                    padding: 4px;
                }
                QLineEdit {
                    background-color: #404040;
                    color: #ffffff;
                    border: 1px solid #666666;
                    border-radius: 4px;
                    padding: 4px;
                }
                QTabWidget::pane {
                    border: 1px solid #666666;
                    background-color: #3c3c3c;
                }
                QTabBar::tab {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border: 1px solid #666666;
                    padding: 8px 16px;
                }
                QTabBar::tab:selected {
                    background-color: #4a90e2;
                }
                QProgressBar {
                    background-color: #404040;
                    border: 1px solid #666666;
                    border-radius: 4px;
                }
                QProgressBar::chunk {
                    background-color: #4a90e2;
                    border-radius: 4px;
                }
                QMenuBar {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 4px 8px;
                }
                QMenuBar::item:selected {
                    background-color: #4a90e2;
                }
                QMenu {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #666666;
                }
                QMenu::item:selected {
                    background-color: #4a90e2;
                }
                QStatusBar {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                """
                self.setStyleSheet(dark_style)
        except Exception as e:
            if self.status_bar:
                self.status_bar.showMessage(f"Failed to apply dark theme: {e}")
            else:
                print(f"Failed to apply dark theme: {e}")
            
    def update_copy_button_state(self):
        """Enable or disable the copy button based on output text content"""
        is_empty = not self.txt_b64_output.toPlainText()
        self.btn_copy_b64_output.setEnabled(not is_empty)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events"""
        mime_data = event.mimeData()
        current_tab = self.tabs.currentWidget()
        
        if current_tab == self.tab_file_to_b64:
            if mime_data and mime_data.hasUrls():
                event.acceptProposedAction()
                self.lbl_drag_drop_status.setText("Release to encode file.")
                if not self.is_dark_theme:
                    self.tab_file_to_b64.setStyleSheet("QWidget { background-color: lightgreen; border: 2px dashed green; }")
            else:
                event.ignore()
                self.lbl_drag_drop_status.setText("Cannot process this item. Drop a file.")
                if not self.is_dark_theme:
                    self.tab_file_to_b64.setStyleSheet("QWidget { background-color: lightcoral; border: 2px dashed red; }")
        else:
            event.ignore()
            
    def dragLeaveEvent(self, event: QDragLeaveEvent):
        """Reset UI elements when drag leaves"""
        if not self.is_dark_theme:
            self.tab_file_to_b64.setStyleSheet("")
        self.lbl_drag_drop_status.setText("Drag & drop any file or select.")
        super().dragLeaveEvent(event)
        
    def dropEvent(self, event: QDropEvent):
        """Handle drop events"""
        if not self.is_dark_theme:
            self.tab_file_to_b64.setStyleSheet("")
        self.lbl_drag_drop_status.setText("Drag & drop any file or select.")
        
        mime_data = event.mimeData()
        if self.tabs.currentWidget() == self.tab_file_to_b64:
            if mime_data and mime_data.hasUrls():
                urls = mime_data.urls()
                if urls:
                    file_path = urls[0].toLocalFile()
                    self.start_encode_file_to_base64(file_path)
                    event.acceptProposedAction()
                    return
            event.ignore()
            QMessageBox.warning(self, "Invalid File", "Please drop a valid file.")
        else:
            event.ignore()
            
    def select_file_for_encoding(self):
        """Open file dialog to select file for encoding"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File to Encode",
            self.last_file_selection_dir,
            "All Files (*.*)"
        )
        if file_path:
            self.last_file_selection_dir = os.path.dirname(file_path)
            self.start_encode_file_to_base64(file_path)
            
    def start_encode_file_to_base64(self, file_path: str):
        """Start file encoding in background thread"""
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.btn_select_file.setEnabled(False)
        if self.status_bar:
            self.status_bar.showMessage(f"Encoding file: {os.path.basename(file_path)}")
        
        self.encode_thread = QThread()
        self.encode_worker = EncodeWorker(file_path)
        self.encode_worker.moveToThread(self.encode_thread)
        
        self.encode_worker.encoding_successful.connect(self.handle_encoding_success)
        self.encode_worker.encoding_failed.connect(self.handle_encoding_failure)
        self.encode_worker.finished.connect(self.encode_thread.quit)
        self.encode_worker.finished.connect(self.encode_worker.deleteLater)
        self.encode_thread.finished.connect(self.encode_thread.deleteLater)
        self.encode_thread.finished.connect(self.on_encode_thread_finished)
        
        self.encode_thread.started.connect(self.encode_worker.run_encode)
        self.encode_thread.start()
        
    def on_encode_thread_finished(self):
        """Cleanup after encoding thread finishes"""
        self.progress.setVisible(False)
        self.progress.setRange(0, 100)
        self.btn_select_file.setEnabled(True)
        self.encode_thread = None
        self.encode_worker = None
        
    def handle_encoding_success(self, b64_string: str):
        """Handle successful encoding"""
        self.txt_b64_output.setPlainText(b64_string)
        if self.status_bar:
            self.status_bar.showMessage("File encoded successfully")
        
    def handle_encoding_failure(self, error_message: str):
        """Handle encoding failure"""
        QMessageBox.critical(self, "Encoding Error", error_message)
        if self.status_bar:
            self.status_bar.showMessage("Encoding failed")
    def copy_b64(self):
        """Copy Base64 text to clipboard"""
        b64_text = self.txt_b64_output.toPlainText()
        if b64_text:
            clipboard = QApplication.clipboard()
            if clipboard:
                clipboard.setText(b64_text)
                QMessageBox.information(self, "Copied", "Base64 string copied to clipboard.")
                if self.status_bar:
                    self.status_bar.showMessage("Base64 copied to clipboard")
            else:
                QMessageBox.warning(self, "Clipboard Error", "Clipboard is not available.")
        
    def clear_b64_input(self):
        """Clear Base64 input"""
        self.txt_b64_input.clear()
        
    def clear_b64_to_img_output(self):
        """Clear Base64 to image output"""
        if self.status_bar:
            self.status_bar.showMessage("Image cleared")
        self.lbl_image.clear()
        self.decoded_image_data = None
        self.original_decoded_pixmap = None
        
    def is_valid_base64_string(self, s: str) -> bool:
        """Validate Base64 string"""
        if not re.fullmatch(r'[A-Za-z0-9+/]*={0,2}', s):
            return False
        if len(s) % 4 != 0:
            return False
        return True
        
    def set_custom_preview_size(self):
        """Set custom preview size"""
        max_w_str = self.txt_max_width.text()
        max_h_str = self.txt_max_height.text()
        
        try:
            max_w = int(max_w_str)
            max_h = int(max_h_str)
            if max_w > 0 and max_h > 0:
                self.custom_preview_size = QSize(max_w, max_h)
                QMessageBox.information(self, "Preview Size Set", 
                                      "Maximum preview size updated. Image will rescale if present.")
                self.update_displayed_image()
                if self.status_bar:
                    self.status_bar.showMessage(f"Preview size set to {max_w}x{max_h}")
            else:
                raise ValueError("Dimensions must be positive.")
        except ValueError:
            QMessageBox.warning(self, "Invalid Size", 
                              "Please enter positive integer values for both width and height.")
            self.custom_preview_size = None
            
    def clear_custom_preview_size(self):
        """Clear custom preview size"""
        if self.status_bar:
            self.status_bar.showMessage("Preview size cleared")
        self.txt_max_width.clear()
        self.txt_max_height.clear()
        QMessageBox.information(self, "Preview Size Cleared", 
                              "Custom preview size cleared. Image will scale to fit window if present.")
        self.custom_preview_size = None
        self.update_displayed_image()
        
    def decode_b64(self):
        """Decode Base64 string to image"""
        b64_text = self.txt_b64_input.toPlainText().strip()
        if not b64_text:
            QMessageBox.warning(self, "Input Required", "Please enter a Base64 string.")
            return

        if not self.is_valid_base64_string(b64_text):
            QMessageBox.warning(self, "Invalid Base64", "The input string does not appear to be a valid Base64 format.")
            return

        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.btn_decode.setEnabled(False)
        if self.status_bar:
            self.status_bar.showMessage("Decoding Base64...")

        self.decode_thread = QThread()
        self.decode_worker = DecodeWorker(b64_text)
        self.decode_worker.moveToThread(self.decode_thread)

        self.decode_worker.decoding_successful.connect(self.handle_decoding_success)
        self.decode_worker.decoding_failed.connect(self.handle_decoding_failure)
        self.decode_worker.finished.connect(self.decode_thread.quit)
        self.decode_worker.finished.connect(self.decode_worker.deleteLater)
        self.decode_thread.finished.connect(self.decode_thread.deleteLater)
        self.decode_thread.finished.connect(self.on_decode_thread_finished)

        self.decode_thread.started.connect(self.decode_worker.run_decode)
        self.decode_thread.start()
        
    def on_decode_thread_finished(self):
        """Cleanup after decode thread finishes"""
        self.progress.setVisible(False)
        self.progress.setRange(0, 100)
        self.btn_decode.setEnabled(True)
        self.decode_thread = None
        self.decode_worker = None
        
    def handle_decoding_success(self, decoded_data: bytes):
        """Handle successful decoding"""
        self.decoded_image_data = decoded_data
        pixmap = QPixmap()
        pixmap.loadFromData(decoded_data)
        self.original_decoded_pixmap = pixmap

        if self.original_decoded_pixmap.isNull():
            self.handle_decoding_failure("Base64 decoded, but data is not a recognized image format for preview.")
            return

        self.update_displayed_image()
        if self.status_bar:
            self.status_bar.showMessage("Base64 decoded successfully")
            
    def handle_decoding_failure(self, error_message: str):
        """Handle decoding failure"""
        QMessageBox.critical(self, "Decoding Error", error_message)
        self.decoded_image_data = None
        self.original_decoded_pixmap = None
        self.lbl_image.clear()
        if self.status_bar:
            self.status_bar.showMessage("Decoding failed")
            
    def update_displayed_image(self):
        """Update the displayed image with proper scaling"""
        if self.original_decoded_pixmap and not self.original_decoded_pixmap.isNull():
            if self.custom_preview_size is not None:
                target_size = self.custom_preview_size
            elif self.lbl_image.width() > 0 and self.lbl_image.height() > 0:
                target_size = self.lbl_image.size()
            else:
                target_size = QSize(200, 200)
                
            scaled_pixmap = self.original_decoded_pixmap.scaled(
                target_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.lbl_image.setPixmap(scaled_pixmap)
        else:
            self.lbl_image.clear()
            
    def save_decoded_image(self):
        """Save decoded image to file"""
        if not self.decoded_image_data or not self.original_decoded_pixmap:
            QMessageBox.warning(self, "No Image", "No image has been decoded to save.")
            return

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save Image As...",
            self.last_image_save_dir,
            "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;BMP Files (*.bmp);;All Files (*)"
        )

        if file_path:
            self.last_image_save_dir = os.path.dirname(file_path)
            try:
                # Add extension if not present
                if "PNG Files" in selected_filter and not file_path.lower().endswith(".png"):
                    file_path += ".png"
                elif "JPEG Files" in selected_filter and not (file_path.lower().endswith(".jpg") or file_path.lower().endswith(".jpeg")):
                    file_path += ".jpg"
                elif "BMP Files" in selected_filter and not file_path.lower().endswith(".bmp"):
                    file_path += ".bmp"

                if not self.original_decoded_pixmap.save(file_path):
                    raise IOError(f"Failed to save pixmap. Check file permissions or path.")

                QMessageBox.information(self, "Saved", "Image saved successfully.")
                if self.status_bar:
                    self.status_bar.showMessage(f"Image saved to {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save image: {e}")
                if self.status_bar:
                    self.status_bar.showMessage("Save failed")
                    
    def show_help(self):
        """Show help dialog"""
        help_text = """
        Enhanced Base64 Image Transformer
        
        This application allows you to convert between files and Base64 encoding.
        
        File to Base64 Tab:
        - Select a file or drag & drop to encode it to Base64
        - Copy the result to clipboard
        
        Base64 to Image Tab:
        - Paste Base64 string to decode it to an image
        - Set custom preview size if needed
        - Save the decoded image
        
        Features:
        - Dark/Light theme toggle
        - Drag & drop support
        - Background processing
        - Image preview with scaling
        """
        QMessageBox.information(self, "Help", help_text)
        
    def resizeEvent(self, event):
        """Handle window resize"""
        super().resizeEvent(event)
        if (self.tabs.currentWidget() == self.tab_b64_to_img and 
            self.original_decoded_pixmap and 
            self.custom_preview_size is None):
            self.update_displayed_image()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Enhanced Base64 Image Transformer")
    app.setApplicationVersion("2.0")
    
    window = WorkingMainWindow()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
=======
"""
Working Enhanced Main Window Implementation
Based on the functional legacy code with improved architecture
"""

import sys
import base64
import os
import re
import binascii
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QTextEdit, QLabel, QTabWidget, QMessageBox, 
    QProgressBar, QLineEdit, QFormLayout, QApplication
)
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QDragLeaveEvent, QIntValidator, QAction
from PyQt6.QtCore import Qt, QSize, QObject, QThread, pyqtSignal


class EncodeWorker(QObject):
    """Worker object to perform file encoding to Base64 in a separate thread."""
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
            self.encoding_failed.emit(f"File not found: {self.file_path}")
        except IOError as e:
            self.encoding_failed.emit(f"An I/O error occurred: {e}")
        except Exception as e:
            self.encoding_failed.emit(f"Failed to encode file: {e}")
        finally:
            self.finished.emit()


class DecodeWorker(QObject):
    """Worker object to perform Base64 decoding in a separate thread."""
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
            self.decoding_failed.emit("Invalid Base64 string: The input is not a valid Base64 encoded string.")
        except Exception as e:
            self.decoding_failed.emit(f"Failed to decode Base64: {e}")
        finally:
            self.finished.emit()


class WorkingMainWindow(QMainWindow):
    """
    Working Enhanced Main Window with proper theming and functional buttons
    Based on the legacy code but with improved architecture
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Base64 Image Transformer")
        self.setMinimumSize(900, 600)
        self.setAcceptDrops(True)
        
        # Theme state
        self.is_dark_theme = False
        
        # File paths
        self.last_file_selection_dir = ""
        self.last_image_save_dir = ""
        
        # Image data
        self.decoded_image_data: Optional[bytes] = None
        self.original_decoded_pixmap: Optional[QPixmap] = None
        self.custom_preview_size: Optional[QSize] = None
        
        # Worker threads
        self.encode_thread: Optional[QThread] = None
        self.encode_worker: Optional[EncodeWorker] = None
        self.decode_thread: Optional[QThread] = None
        self.decode_worker: Optional[DecodeWorker] = None
        
        self.setup_ui()
        self.apply_light_theme()
        
    def setup_ui(self):
        """Setup the main window UI"""
        # Menu bar
        self.setup_menu_bar()
        
        # Status bar
        self.status_bar = self.statusBar()
        if self.status_bar:
            self.status_bar.showMessage("Ready")
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Initialize tabs
        self.init_file_to_b64_tab()
        self.init_b64_to_img_tab()
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        main_layout.addWidget(self.progress)
        
        # Footer buttons
        footer_layout = QHBoxLayout()
        
        self.theme_button = QPushButton("Toggle Dark Theme")
        self.theme_button.clicked.connect(self.toggle_theme)
        footer_layout.addWidget(self.theme_button)
        
        footer_layout.addStretch()
        
        help_button = QPushButton("Help")
        help_button.clicked.connect(self.show_help)
        footer_layout.addWidget(help_button)
        
        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(self.close)
        footer_layout.addWidget(exit_button)
        
        main_layout.addLayout(footer_layout)
        
    def setup_menu_bar(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        if not menubar:
            return
            
        # File menu
        file_menu = menubar.addMenu("File")
        if file_menu:
            exit_action = QAction("Exit", self)
            exit_action.setShortcut("Ctrl+Q")
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        if view_menu:
            theme_action = QAction("Toggle Theme", self)
            theme_action.triggered.connect(self.toggle_theme)
            view_menu.addAction(theme_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        if help_menu:
            about_action = QAction("About", self)
            about_action.triggered.connect(self.show_help)
            help_menu.addAction(about_action)
        
    def init_file_to_b64_tab(self):
        """Initialize file to Base64 tab"""
        self.tab_file_to_b64 = QWidget()
        layout = QVBoxLayout(self.tab_file_to_b64)
        
        # Select file button
        self.btn_select_file = QPushButton("Select File")
        self.btn_select_file.clicked.connect(self.select_file_for_encoding)
        layout.addWidget(self.btn_select_file)
        
        # Drag drop status
        self.lbl_drag_drop_status = QLabel("Drag & drop any file or select.")
        self.lbl_drag_drop_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_drag_drop_status)
        
        # Base64 output
        self.txt_b64_output = QTextEdit()
        self.txt_b64_output.setReadOnly(True)
        self.txt_b64_output.textChanged.connect(self.update_copy_button_state)
        layout.addWidget(self.txt_b64_output)
        
        # Output buttons
        output_btn_layout = QHBoxLayout()
        
        self.btn_copy_b64_output = QPushButton("Copy Base64 to Clipboard")
        self.btn_copy_b64_output.clicked.connect(self.copy_b64)
        self.btn_copy_b64_output.setEnabled(False)
        output_btn_layout.addWidget(self.btn_copy_b64_output)
        
        btn_clear_output = QPushButton("Clear Output")
        btn_clear_output.clicked.connect(self.clear_file_to_b64_output)
        output_btn_layout.addWidget(btn_clear_output)
        
        layout.addLayout(output_btn_layout)
        layout.addStretch()
        
        self.tabs.addTab(self.tab_file_to_b64, "File to Base64")
        
    def clear_file_to_b64_output(self):
        """Clear Base64 output in File to Base64 tab"""
        self.txt_b64_output.clear()
        if self.status_bar:
            self.status_bar.showMessage("Output cleared")
    def init_b64_to_img_tab(self):
        """Initialize Base64 to image tab"""
        self.tab_b64_to_img = QWidget()
        layout = QVBoxLayout(self.tab_b64_to_img)
        
        # Base64 input
        self.txt_b64_input = QTextEdit()
        self.txt_b64_input.setPlaceholderText("Paste Base64 string here...")
        layout.addWidget(self.txt_b64_input)
        
        # Decode buttons
        decode_btn_layout = QHBoxLayout()
        
        self.btn_decode = QPushButton("Decode to Image")
        self.btn_decode.clicked.connect(self.decode_b64)
        decode_btn_layout.addWidget(self.btn_decode)
        
        btn_clear_input = QPushButton("Clear Base64 Input")
        btn_clear_input.clicked.connect(self.clear_b64_input)
        decode_btn_layout.addWidget(btn_clear_input)
        
        layout.addLayout(decode_btn_layout)
        
        # Preview size controls
        preview_size_form_layout = QFormLayout()
        
        self.txt_max_width = QLineEdit()
        self.txt_max_width.setPlaceholderText("e.g., 800")
        self.txt_max_width.setValidator(QIntValidator(1, 9999))
        preview_size_form_layout.addRow("Max Width:", self.txt_max_width)
        
        self.txt_max_height = QLineEdit()
        self.txt_max_height.setPlaceholderText("e.g., 600")
        self.txt_max_height.setValidator(QIntValidator(1, 9999))
        preview_size_form_layout.addRow("Max Height:", self.txt_max_height)
        
        layout.addLayout(preview_size_form_layout)
        
        # Preview size buttons
        preview_size_btn_layout = QHBoxLayout()
        
        btn_set_preview_size = QPushButton("Set Max Preview Size")
        btn_set_preview_size.clicked.connect(self.set_custom_preview_size)
        preview_size_btn_layout.addWidget(btn_set_preview_size)
        
        btn_clear_preview_size = QPushButton("Clear Custom Size")
        btn_clear_preview_size.clicked.connect(self.clear_custom_preview_size)
        preview_size_btn_layout.addWidget(btn_clear_preview_size)
        
        layout.addLayout(preview_size_btn_layout)
        
        # Image display
        self.lbl_image = QLabel()
        self.lbl_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_image.setMinimumSize(200, 200)
        layout.addWidget(self.lbl_image, stretch=1)
        
        # Save/clear image buttons
        save_clear_img_btn_layout = QHBoxLayout()
        
        btn_save_image = QPushButton("Save Image As...")
        btn_save_image.clicked.connect(self.save_decoded_image)
        save_clear_img_btn_layout.addWidget(btn_save_image)
        
        btn_clear_decoded_image = QPushButton("Clear Image")
        btn_clear_decoded_image.clicked.connect(self.clear_b64_to_img_output)
        save_clear_img_btn_layout.addWidget(btn_clear_decoded_image)
        
        layout.addLayout(save_clear_img_btn_layout)
        layout.addStretch()
        
        self.tabs.addTab(self.tab_b64_to_img, "Base64 to Image")
        
    def show_status(self, message: str):
        """Show status message if status bar exists"""
        if self.status_bar:
            self.status_bar.showMessage(message)
            
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if self.is_dark_theme:
            self.apply_light_theme()
            self.theme_button.setText("Toggle Dark Theme")
            self.show_status("Switched to light theme")
        else:
            self.apply_dark_theme()
            self.theme_button.setText("Toggle Light Theme")
            self.show_status("Switched to dark theme")
        self.is_dark_theme = not self.is_dark_theme
        
    def apply_light_theme(self):
        """Apply light theme"""
        self.setStyleSheet("")
        
    def apply_dark_theme(self):
        """Apply dark theme"""
        try:
            dark_theme_path = Path(__file__).parent.parent.parent.parent / "resources" / "dark_theme.qss"
            if dark_theme_path.exists():
                with open(dark_theme_path, 'r', encoding='utf-8') as f:
                    dark_qss = f.read()
                self.setStyleSheet(dark_qss)
            else:
                # Fallback dark theme
                dark_style = """
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QWidget {
                    background-color: #3c3c3c;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #4a90e2;
                    color: #ffffff;
                    border: 1px solid #357abd;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #357abd;
                }
                QPushButton:pressed {
                    background-color: #2a5a8a;
                }
                QPushButton:disabled {
                    background-color: #555555;
                    color: #888888;
                }
                QTextEdit {
                    background-color: #404040;
                    color: #ffffff;
                    border: 1px solid #666666;
                    border-radius: 4px;
                    padding: 4px;
                }
                QLineEdit {
                    background-color: #404040;
                    color: #ffffff;
                    border: 1px solid #666666;
                    border-radius: 4px;
                    padding: 4px;
                }
                QTabWidget::pane {
                    border: 1px solid #666666;
                    background-color: #3c3c3c;
                }
                QTabBar::tab {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border: 1px solid #666666;
                    padding: 8px 16px;
                }
                QTabBar::tab:selected {
                    background-color: #4a90e2;
                }
                QProgressBar {
                    background-color: #404040;
                    border: 1px solid #666666;
                    border-radius: 4px;
                }
                QProgressBar::chunk {
                    background-color: #4a90e2;
                    border-radius: 4px;
                }
                QMenuBar {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 4px 8px;
                }
                QMenuBar::item:selected {
                    background-color: #4a90e2;
                }
                QMenu {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #666666;
                }
                QMenu::item:selected {
                    background-color: #4a90e2;
                }
                QStatusBar {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                """
                self.setStyleSheet(dark_style)
        except Exception as e:
            if self.status_bar:
                self.status_bar.showMessage(f"Failed to apply dark theme: {e}")
            else:
                print(f"Failed to apply dark theme: {e}")
            
    def update_copy_button_state(self):
        """Enable or disable the copy button based on output text content"""
        is_empty = not self.txt_b64_output.toPlainText()
        self.btn_copy_b64_output.setEnabled(not is_empty)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events"""
        mime_data = event.mimeData()
        current_tab = self.tabs.currentWidget()
        
        if current_tab == self.tab_file_to_b64:
            if mime_data and mime_data.hasUrls():
                event.acceptProposedAction()
                self.lbl_drag_drop_status.setText("Release to encode file.")
                if not self.is_dark_theme:
                    self.tab_file_to_b64.setStyleSheet("QWidget { background-color: lightgreen; border: 2px dashed green; }")
            else:
                event.ignore()
                self.lbl_drag_drop_status.setText("Cannot process this item. Drop a file.")
                if not self.is_dark_theme:
                    self.tab_file_to_b64.setStyleSheet("QWidget { background-color: lightcoral; border: 2px dashed red; }")
        else:
            event.ignore()
            
    def dragLeaveEvent(self, event: QDragLeaveEvent):
        """Reset UI elements when drag leaves"""
        if not self.is_dark_theme:
            self.tab_file_to_b64.setStyleSheet("")
        self.lbl_drag_drop_status.setText("Drag & drop any file or select.")
        super().dragLeaveEvent(event)
        
    def dropEvent(self, event: QDropEvent):
        """Handle drop events"""
        if not self.is_dark_theme:
            self.tab_file_to_b64.setStyleSheet("")
        self.lbl_drag_drop_status.setText("Drag & drop any file or select.")
        
        mime_data = event.mimeData()
        if self.tabs.currentWidget() == self.tab_file_to_b64:
            if mime_data and mime_data.hasUrls():
                urls = mime_data.urls()
                if urls:
                    file_path = urls[0].toLocalFile()
                    self.start_encode_file_to_base64(file_path)
                    event.acceptProposedAction()
                    return
            event.ignore()
            QMessageBox.warning(self, "Invalid File", "Please drop a valid file.")
        else:
            event.ignore()
            
    def select_file_for_encoding(self):
        """Open file dialog to select file for encoding"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File to Encode",
            self.last_file_selection_dir,
            "All Files (*.*)"
        )
        if file_path:
            self.last_file_selection_dir = os.path.dirname(file_path)
            self.start_encode_file_to_base64(file_path)
            
    def start_encode_file_to_base64(self, file_path: str):
        """Start file encoding in background thread"""
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.btn_select_file.setEnabled(False)
        if self.status_bar:
            self.status_bar.showMessage(f"Encoding file: {os.path.basename(file_path)}")
        
        self.encode_thread = QThread()
        self.encode_worker = EncodeWorker(file_path)
        self.encode_worker.moveToThread(self.encode_thread)
        
        self.encode_worker.encoding_successful.connect(self.handle_encoding_success)
        self.encode_worker.encoding_failed.connect(self.handle_encoding_failure)
        self.encode_worker.finished.connect(self.encode_thread.quit)
        self.encode_worker.finished.connect(self.encode_worker.deleteLater)
        self.encode_thread.finished.connect(self.encode_thread.deleteLater)
        self.encode_thread.finished.connect(self.on_encode_thread_finished)
        
        self.encode_thread.started.connect(self.encode_worker.run_encode)
        self.encode_thread.start()
        
    def on_encode_thread_finished(self):
        """Cleanup after encoding thread finishes"""
        self.progress.setVisible(False)
        self.progress.setRange(0, 100)
        self.btn_select_file.setEnabled(True)
        self.encode_thread = None
        self.encode_worker = None
        
    def handle_encoding_success(self, b64_string: str):
        """Handle successful encoding"""
        self.txt_b64_output.setPlainText(b64_string)
        if self.status_bar:
            self.status_bar.showMessage("File encoded successfully")
        
    def handle_encoding_failure(self, error_message: str):
        """Handle encoding failure"""
        QMessageBox.critical(self, "Encoding Error", error_message)
        if self.status_bar:
            self.status_bar.showMessage("Encoding failed")
    def copy_b64(self):
        """Copy Base64 text to clipboard"""
        b64_text = self.txt_b64_output.toPlainText()
        if b64_text:
            clipboard = QApplication.clipboard()
            if clipboard:
                clipboard.setText(b64_text)
                QMessageBox.information(self, "Copied", "Base64 string copied to clipboard.")
                if self.status_bar:
                    self.status_bar.showMessage("Base64 copied to clipboard")
            else:
                QMessageBox.warning(self, "Clipboard Error", "Clipboard is not available.")
        
    def clear_b64_input(self):
        """Clear Base64 input"""
        self.txt_b64_input.clear()
        
    def clear_b64_to_img_output(self):
        """Clear Base64 to image output"""
        if self.status_bar:
            self.status_bar.showMessage("Image cleared")
        self.lbl_image.clear()
        self.decoded_image_data = None
        self.original_decoded_pixmap = None
        
    def is_valid_base64_string(self, s: str) -> bool:
        """Validate Base64 string"""
        if not re.fullmatch(r'[A-Za-z0-9+/]*={0,2}', s):
            return False
        if len(s) % 4 != 0:
            return False
        return True
        
    def set_custom_preview_size(self):
        """Set custom preview size"""
        max_w_str = self.txt_max_width.text()
        max_h_str = self.txt_max_height.text()
        
        try:
            max_w = int(max_w_str)
            max_h = int(max_h_str)
            if max_w > 0 and max_h > 0:
                self.custom_preview_size = QSize(max_w, max_h)
                QMessageBox.information(self, "Preview Size Set", 
                                      "Maximum preview size updated. Image will rescale if present.")
                self.update_displayed_image()
                if self.status_bar:
                    self.status_bar.showMessage(f"Preview size set to {max_w}x{max_h}")
            else:
                raise ValueError("Dimensions must be positive.")
        except ValueError:
            QMessageBox.warning(self, "Invalid Size", 
                              "Please enter positive integer values for both width and height.")
            self.custom_preview_size = None
            
    def clear_custom_preview_size(self):
        """Clear custom preview size"""
        if self.status_bar:
            self.status_bar.showMessage("Preview size cleared")
        self.txt_max_width.clear()
        self.txt_max_height.clear()
        QMessageBox.information(self, "Preview Size Cleared", 
                              "Custom preview size cleared. Image will scale to fit window if present.")
        self.custom_preview_size = None
        self.update_displayed_image()
        
    def decode_b64(self):
        """Decode Base64 string to image"""
        b64_text = self.txt_b64_input.toPlainText().strip()
        if not b64_text:
            QMessageBox.warning(self, "Input Required", "Please enter a Base64 string.")
            return

        if not self.is_valid_base64_string(b64_text):
            QMessageBox.warning(self, "Invalid Base64", "The input string does not appear to be a valid Base64 format.")
            return

        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.btn_decode.setEnabled(False)
        if self.status_bar:
            self.status_bar.showMessage("Decoding Base64...")

        self.decode_thread = QThread()
        self.decode_worker = DecodeWorker(b64_text)
        self.decode_worker.moveToThread(self.decode_thread)

        self.decode_worker.decoding_successful.connect(self.handle_decoding_success)
        self.decode_worker.decoding_failed.connect(self.handle_decoding_failure)
        self.decode_worker.finished.connect(self.decode_thread.quit)
        self.decode_worker.finished.connect(self.decode_worker.deleteLater)
        self.decode_thread.finished.connect(self.decode_thread.deleteLater)
        self.decode_thread.finished.connect(self.on_decode_thread_finished)

        self.decode_thread.started.connect(self.decode_worker.run_decode)
        self.decode_thread.start()
        
    def on_decode_thread_finished(self):
        """Cleanup after decode thread finishes"""
        self.progress.setVisible(False)
        self.progress.setRange(0, 100)
        self.btn_decode.setEnabled(True)
        self.decode_thread = None
        self.decode_worker = None
        
    def handle_decoding_success(self, decoded_data: bytes):
        """Handle successful decoding"""
        self.decoded_image_data = decoded_data
        pixmap = QPixmap()
        pixmap.loadFromData(decoded_data)
        self.original_decoded_pixmap = pixmap

        if self.original_decoded_pixmap.isNull():
            self.handle_decoding_failure("Base64 decoded, but data is not a recognized image format for preview.")
            return

        self.update_displayed_image()
        if self.status_bar:
            self.status_bar.showMessage("Base64 decoded successfully")
            
    def handle_decoding_failure(self, error_message: str):
        """Handle decoding failure"""
        QMessageBox.critical(self, "Decoding Error", error_message)
        self.decoded_image_data = None
        self.original_decoded_pixmap = None
        self.lbl_image.clear()
        if self.status_bar:
            self.status_bar.showMessage("Decoding failed")
            
    def update_displayed_image(self):
        """Update the displayed image with proper scaling"""
        if self.original_decoded_pixmap and not self.original_decoded_pixmap.isNull():
            if self.custom_preview_size is not None:
                target_size = self.custom_preview_size
            elif self.lbl_image.width() > 0 and self.lbl_image.height() > 0:
                target_size = self.lbl_image.size()
            else:
                target_size = QSize(200, 200)
                
            scaled_pixmap = self.original_decoded_pixmap.scaled(
                target_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.lbl_image.setPixmap(scaled_pixmap)
        else:
            self.lbl_image.clear()
            
    def save_decoded_image(self):
        """Save decoded image to file"""
        if not self.decoded_image_data or not self.original_decoded_pixmap:
            QMessageBox.warning(self, "No Image", "No image has been decoded to save.")
            return

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save Image As...",
            self.last_image_save_dir,
            "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;BMP Files (*.bmp);;All Files (*)"
        )

        if file_path:
            self.last_image_save_dir = os.path.dirname(file_path)
            try:
                # Add extension if not present
                if "PNG Files" in selected_filter and not file_path.lower().endswith(".png"):
                    file_path += ".png"
                elif "JPEG Files" in selected_filter and not (file_path.lower().endswith(".jpg") or file_path.lower().endswith(".jpeg")):
                    file_path += ".jpg"
                elif "BMP Files" in selected_filter and not file_path.lower().endswith(".bmp"):
                    file_path += ".bmp"

                if not self.original_decoded_pixmap.save(file_path):
                    raise IOError(f"Failed to save pixmap. Check file permissions or path.")

                QMessageBox.information(self, "Saved", "Image saved successfully.")
                if self.status_bar:
                    self.status_bar.showMessage(f"Image saved to {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save image: {e}")
                if self.status_bar:
                    self.status_bar.showMessage("Save failed")
                    
    def show_help(self):
        """Show help dialog"""
        help_text = """
        Enhanced Base64 Image Transformer
        
        This application allows you to convert between files and Base64 encoding.
        
        File to Base64 Tab:
        - Select a file or drag & drop to encode it to Base64
        - Copy the result to clipboard
        
        Base64 to Image Tab:
        - Paste Base64 string to decode it to an image
        - Set custom preview size if needed
        - Save the decoded image
        
        Features:
        - Dark/Light theme toggle
        - Drag & drop support
        - Background processing
        - Image preview with scaling
        """
        QMessageBox.information(self, "Help", help_text)
        
    def resizeEvent(self, event):
        """Handle window resize"""
        super().resizeEvent(event)
        if (self.tabs.currentWidget() == self.tab_b64_to_img and 
            self.original_decoded_pixmap and 
            self.custom_preview_size is None):
            self.update_displayed_image()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Enhanced Base64 Image Transformer")
    app.setApplicationVersion("2.0")
    
    window = WorkingMainWindow()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
>>>>>>> e58bf1982f62d575da5b851d7dfd7f30682e5195
