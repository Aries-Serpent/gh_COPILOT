"""Enhanced UI wrapper for the Base64 ZIP Transformer."""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtWidgets import QPushButton, QHBoxLayout

# Import legacy transformer
legacy_path = Path(__file__).parent.parent.parent.parent / "legacy"
sys.path.insert(0, str(legacy_path.resolve()))
from legacy.Base64ZipTransformer import Base64ZipTransformer  # noqa: E402


class EnhancedBase64ZipTransformer(Base64ZipTransformer):
    """Enhanced version with theme toggle support."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Enhanced Base64 ZIP Transformer")
        self.is_dark_theme = False
        self.add_theme_controls()

    def add_theme_controls(self) -> None:
        """Insert a theme toggle button into the first tab."""
        theme_layout = QHBoxLayout()

        self.theme_button = QPushButton("Toggle Dark Theme")
        self.theme_button.clicked.connect(self.toggle_theme)
        theme_layout.addWidget(self.theme_button)
        theme_layout.addStretch()

        tab_layout = self.tabs.widget(0).layout()
        if tab_layout:
            tab_layout.addLayout(theme_layout)

    def toggle_theme(self) -> None:
        """Switch between light and dark themes."""
        if self.is_dark_theme:
            self.setStyleSheet("")
            self.theme_button.setText("Toggle Dark Theme")
        else:
            self.apply_dark_theme()
            self.theme_button.setText("Toggle Light Theme")
        self.is_dark_theme = not self.is_dark_theme

    def apply_dark_theme(self) -> None:
        """Apply a simple dark theme stylesheet."""
        self.setStyleSheet(
            """
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QPushButton {
                background-color: #4a90e2;
                color: #ffffff;
                border: 1px solid #357abd;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QTextEdit {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #666666;
                border-radius: 4px;
            }
            QTreeWidget {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #666666;
            }
            """
        )


__all__ = ["EnhancedBase64ZipTransformer"]

