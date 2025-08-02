"""Entry point for the enhanced Base64 ZIP transformer."""

from __future__ import annotations

import sys
from PyQt6.QtWidgets import QApplication

from .ui.enhanced_transformer import EnhancedBase64ZipTransformer


def main() -> None:  # pragma: no cover - UI entry
    app = QApplication(sys.argv)
    window = EnhancedBase64ZipTransformer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":  # pragma: no cover - UI entry
    main()

