<<<<<<< HEAD
"""
Working Enhanced Main Window Implementation
Fixed version without lint errors, based on legacy functionality
"""

import sys
import os
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal

# Import the working legacy code as base
legacy_path = Path(__file__).parent.parent.parent.parent / "legacy"
sys.path.insert(0, str(legacy_path.resolve()))
from legacy.Base64ImageTransformer import Base64ImageTransformer


class EnhancedBase64Transformer(Base64ImageTransformer):
    """
    Enhanced version of the Base64 transformer with theme support
    Inherits all working functionality from the legacy version
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Base64 Image Transformer")
        self.is_dark_theme = False
        
        # Add theme toggle button to the UI
        self.add_theme_controls()
        
    def add_theme_controls(self):
        """Add theme toggle controls to existing UI"""
        from PyQt6.QtWidgets import QPushButton, QHBoxLayout
        
        # Add theme button to first tab
        theme_layout = QHBoxLayout()
        
        self.theme_button = QPushButton("Toggle Dark Theme")
        self.theme_button.clicked.connect(self.toggle_theme)
        theme_layout.addWidget(self.theme_button)
        
        theme_layout.addStretch()
        
        # Add theme controls to the first tab's layout
        tab_layout = self.tab_file_to_b64.layout()
        if tab_layout:
            tab_layout.addItem(theme_layout)
        
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if self.is_dark_theme:
            self.apply_light_theme()
            self.theme_button.setText("Toggle Dark Theme")
        else:
            self.apply_dark_theme()
            self.theme_button.setText("Toggle Light Theme")
        self.is_dark_theme = not self.is_dark_theme
        
    def apply_light_theme(self):
        """Apply light theme"""
        self.setStyleSheet("")
        
    def apply_dark_theme(self):
        """Apply dark theme with proper colors for all elements"""
        dark_style = """
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        
        QPushButton {
            background-color: #4a90e2;
            color: #ffffff;
            border: 1px solid #357abd;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            min-height: 20px;
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
            selection-background-color: #4a90e2;
        }
        
        QLineEdit {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #666666;
            border-radius: 4px;
            padding: 4px;
            selection-background-color: #4a90e2;
        }
        
        QLabel {
            color: #ffffff;
            background-color: transparent;
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
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #4a90e2;
        }
        
        QTabBar::tab:hover {
            background-color: #357abd;
        }
        
        QProgressBar {
            background-color: #404040;
            border: 1px solid #666666;
            border-radius: 4px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #4a90e2;
            border-radius: 4px;
        }
        
        QMessageBox {
            background-color: #3c3c3c;
            color: #ffffff;
        }
        
        QMessageBox QPushButton {
            background-color: #4a90e2;
            color: #ffffff;
            border: 1px solid #357abd;
            border-radius: 4px;
            padding: 6px 12px;
            min-width: 60px;
        }
        
        QFileDialog {
            background-color: #3c3c3c;
            color: #ffffff;
        }
        
        QScrollBar:vertical {
            background-color: #404040;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #666666;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #777777;
        }
        
        QScrollBar:horizontal {
            background-color: #404040;
            height: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #666666;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #777777;
        }
        """
        self.setStyleSheet(dark_style)


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Enhanced Base64 Image Transformer")
    app.setApplicationVersion("2.0")
    
    # Create the enhanced window based on working legacy code
    window = EnhancedBase64Transformer()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
=======
"""
Working Enhanced Main Window Implementation
Fixed version without lint errors, based on legacy functionality
"""

import sys
import os
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal

# Import the working legacy code as base
legacy_path = Path(__file__).parent.parent.parent.parent / "legacy"
sys.path.insert(0, str(legacy_path.resolve()))
from legacy.Base64ImageTransformer import Base64ImageTransformer


class EnhancedBase64Transformer(Base64ImageTransformer):
    """
    Enhanced version of the Base64 transformer with theme support
    Inherits all working functionality from the legacy version
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Base64 Image Transformer")
        self.is_dark_theme = False
        
        # Add theme toggle button to the UI
        self.add_theme_controls()
        
    def add_theme_controls(self):
        """Add theme toggle controls to existing UI"""
        from PyQt6.QtWidgets import QPushButton, QHBoxLayout
        
        # Add theme button to first tab
        theme_layout = QHBoxLayout()
        
        self.theme_button = QPushButton("Toggle Dark Theme")
        self.theme_button.clicked.connect(self.toggle_theme)
        theme_layout.addWidget(self.theme_button)
        
        theme_layout.addStretch()
        
        # Add theme controls to the first tab's layout
        tab_layout = self.tab_file_to_b64.layout()
        if tab_layout:
            tab_layout.addItem(theme_layout)
        
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if self.is_dark_theme:
            self.apply_light_theme()
            self.theme_button.setText("Toggle Dark Theme")
        else:
            self.apply_dark_theme()
            self.theme_button.setText("Toggle Light Theme")
        self.is_dark_theme = not self.is_dark_theme
        
    def apply_light_theme(self):
        """Apply light theme"""
        self.setStyleSheet("")
        
    def apply_dark_theme(self):
        """Apply dark theme with proper colors for all elements"""
        dark_style = """
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        
        QPushButton {
            background-color: #4a90e2;
            color: #ffffff;
            border: 1px solid #357abd;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            min-height: 20px;
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
            selection-background-color: #4a90e2;
        }
        
        QLineEdit {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #666666;
            border-radius: 4px;
            padding: 4px;
            selection-background-color: #4a90e2;
        }
        
        QLabel {
            color: #ffffff;
            background-color: transparent;
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
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #4a90e2;
        }
        
        QTabBar::tab:hover {
            background-color: #357abd;
        }
        
        QProgressBar {
            background-color: #404040;
            border: 1px solid #666666;
            border-radius: 4px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #4a90e2;
            border-radius: 4px;
        }
        
        QMessageBox {
            background-color: #3c3c3c;
            color: #ffffff;
        }
        
        QMessageBox QPushButton {
            background-color: #4a90e2;
            color: #ffffff;
            border: 1px solid #357abd;
            border-radius: 4px;
            padding: 6px 12px;
            min-width: 60px;
        }
        
        QFileDialog {
            background-color: #3c3c3c;
            color: #ffffff;
        }
        
        QScrollBar:vertical {
            background-color: #404040;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #666666;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #777777;
        }
        
        QScrollBar:horizontal {
            background-color: #404040;
            height: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #666666;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #777777;
        }
        """
        self.setStyleSheet(dark_style)


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Enhanced Base64 Image Transformer")
    app.setApplicationVersion("2.0")
    
    # Create the enhanced window based on working legacy code
    window = EnhancedBase64Transformer()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
>>>>>>> a129e6744e1b47cc89dc5c3c88d9a831f377652b
