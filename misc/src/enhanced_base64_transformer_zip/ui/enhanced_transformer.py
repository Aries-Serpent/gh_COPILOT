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
        tab_layout = self.tab_zip_to_b64.layout()
        if isinstance(tab_layout, QVBoxLayout):
            tab_layout.addLayout(theme_layout)

    def toggle_theme(self) -> None:
        if self.is_dark_theme:
            self.apply_light_theme()
            self.theme_button.setText("Toggle Dark Theme")
        else:
            self.apply_dark_theme()
            self.theme_button.setText("Toggle Light Theme")
        self.is_dark_theme = not self.is_dark_theme

    def apply_light_theme(self) -> None:
        self.setStyleSheet("")

    def apply_dark_theme(self) -> None:
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
        QTextEdit {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #666666;
            border-radius: 4px;
            padding: 4px;
            selection-background-color: #4a90e2;
        }
        QTreeWidget {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #666666;
            border-radius: 4px;
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
        }
        QTabBar::tab:selected {
            background-color: #4a90e2;
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
        }
        """
        self.setStyleSheet(dark_style)


def main() -> None:  # pragma: no cover - UI entry
    app = QApplication(sys.argv)
    window = EnhancedBase64ZipTransformer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":  # pragma: no cover - UI entry
    main()
