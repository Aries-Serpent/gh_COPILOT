"""Entry 
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    """Start the PyQt application."""
    try:
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))

        from PyQt6.QtWidgets import QApplication
        from ui.enhanced_transformer import EnhancedBase64ZipTransformer

        app = QApplication(sys.argv)
        app.setApplicationName("Enhanced Base64 ZIP Transformer")

        window = EnhancedBase64ZipTransformer()
        window.show()

        sys.exit(app.exec())
    except ImportError as exc:  # noqa: BLE001 - surface errors to user
        print(f"Error importing application components: {exc}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    main()

