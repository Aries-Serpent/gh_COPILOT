<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
"""
Main entry point for the Enhanced Base64 Transformer package.
This allows the package to be run with: python -m enhanced_base64_transformer
"""

import sys
import os
from pathlib import Path

def main() -> None:
    """Main entry point for the application."""
    try:
        # Add project root to path for legacy imports
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))
        
        # Import the working legacy transformer
        from legacy.Base64ImageTransformer import Base64ImageTransformer
        from PyQt6.QtWidgets import QApplication, QPushButton, QHBoxLayout
        
        class EnhancedBase64Transformer(Base64ImageTransformer):
            """Enhanced version with theme support"""
            
            def __init__(self):
                super().__init__()
                self.setWindowTitle("Enhanced Base64 Image Transformer")
                self.is_dark_theme = False
                self.add_theme_controls()
                
            def add_theme_controls(self):
                """Add theme toggle controls"""
                from PyQt6.QtWidgets import QVBoxLayout
                
                theme_layout = QHBoxLayout()
                
                self.theme_button = QPushButton("Toggle Dark Theme")
                self.theme_button.clicked.connect(self.toggle_theme)
                theme_layout.addWidget(self.theme_button)
                theme_layout.addStretch()
                
                # Insert at top of first tab
                tab_layout = self.tab_file_to_b64.layout()
                if isinstance(tab_layout, QVBoxLayout):
                    tab_layout.insertLayout(0, theme_layout)
                
            def toggle_theme(self):
                """Toggle theme"""
                if self.is_dark_theme:
                    self.setStyleSheet("")
                    self.theme_button.setText("Toggle Dark Theme")
                else:
                    self.apply_dark_theme()
                    self.theme_button.setText("Toggle Light Theme")
                self.is_dark_theme = not self.is_dark_theme
                
            def apply_dark_theme(self):
                """Apply comprehensive dark theme"""
                self.setStyleSheet("""
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
                }
                QProgressBar::chunk {
                    background-color: #4a90e2;
                    border-radius: 4px;
                }
                """)
        
        # Create and run the application
        app = QApplication(sys.argv)
        app.setApplicationName("Enhanced Base64 Image Transformer")
        app.setApplicationVersion("2.0")
        
        window = EnhancedBase64Transformer()
        window.show()
        
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"Error importing application components: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
=======
"""
Main entry point for the Enhanced Base64 Transformer package.
This allows the package to be run with: python -m enhanced_base64_transformer
"""

import sys
import os
from pathlib import Path

def main() -> None:
    """Main entry point for the application."""
    try:
        # Add project root to path for legacy imports
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))
        
        # Import the working legacy transformer
        from legacy.Base64ImageTransformer import Base64ImageTransformer
        from PyQt6.QtWidgets import QApplication, QPushButton, QHBoxLayout
        
        class EnhancedBase64Transformer(Base64ImageTransformer):
            """Enhanced version with theme support"""
            
            def __init__(self):
                super().__init__()
                self.setWindowTitle("Enhanced Base64 Image Transformer")
                self.is_dark_theme = False
                self.add_theme_controls()
                
            def add_theme_controls(self):
                """Add theme toggle controls"""
                from PyQt6.QtWidgets import QVBoxLayout
                
                theme_layout = QHBoxLayout()
                
                self.theme_button = QPushButton("Toggle Dark Theme")
                self.theme_button.clicked.connect(self.toggle_theme)
                theme_layout.addWidget(self.theme_button)
                theme_layout.addStretch()
                
                # Insert at top of first tab
                tab_layout = self.tab_file_to_b64.layout()
                if isinstance(tab_layout, QVBoxLayout):
                    tab_layout.insertLayout(0, theme_layout)
                
            def toggle_theme(self):
                """Toggle theme"""
                if self.is_dark_theme:
                    self.setStyleSheet("")
                    self.theme_button.setText("Toggle Dark Theme")
                else:
                    self.apply_dark_theme()
                    self.theme_button.setText("Toggle Light Theme")
                self.is_dark_theme = not self.is_dark_theme
                
            def apply_dark_theme(self):
                """Apply comprehensive dark theme"""
                self.setStyleSheet("""
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
                }
                QProgressBar::chunk {
                    background-color: #4a90e2;
                    border-radius: 4px;
                }
                """)
        
        # Create and run the application
        app = QApplication(sys.argv)
        app.setApplicationName("Enhanced Base64 Image Transformer")
        app.setApplicationVersion("2.0")
        
        window = EnhancedBase64Transformer()
        window.show()
        
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"Error importing application components: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
>>>>>>> da3aa0d9bd1300a182f7306f879a5bc66263a78f
=======
"""
Main entry point for the Enhanced Base64 Transformer package.
This allows the package to be run with: python -m enhanced_base64_transformer
"""

import sys
import os
from pathlib import Path

def main() -> None:
    """Main entry point for the application."""
    try:
        # Add project root to path for legacy imports
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))
        
        # Import the working legacy transformer
        from legacy.Base64ImageTransformer import Base64ImageTransformer
        from PyQt6.QtWidgets import QApplication, QPushButton, QHBoxLayout
        
        class EnhancedBase64Transformer(Base64ImageTransformer):
            """Enhanced version with theme support"""
            
            def __init__(self):
                super().__init__()
                self.setWindowTitle("Enhanced Base64 Image Transformer")
                self.is_dark_theme = False
                self.add_theme_controls()
                
            def add_theme_controls(self):
                """Add theme toggle controls"""
                from PyQt6.QtWidgets import QVBoxLayout
                
                theme_layout = QHBoxLayout()
                
                self.theme_button = QPushButton("Toggle Dark Theme")
                self.theme_button.clicked.connect(self.toggle_theme)
                theme_layout.addWidget(self.theme_button)
                theme_layout.addStretch()
                
                # Insert at top of first tab
                tab_layout = self.tab_file_to_b64.layout()
                if isinstance(tab_layout, QVBoxLayout):
                    tab_layout.insertLayout(0, theme_layout)
                
            def toggle_theme(self):
                """Toggle theme"""
                if self.is_dark_theme:
                    self.setStyleSheet("")
                    self.theme_button.setText("Toggle Dark Theme")
                else:
                    self.apply_dark_theme()
                    self.theme_button.setText("Toggle Light Theme")
                self.is_dark_theme = not self.is_dark_theme
                
            def apply_dark_theme(self):
                """Apply comprehensive dark theme"""
                self.setStyleSheet("""
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
                }
                QProgressBar::chunk {
                    background-color: #4a90e2;
                    border-radius: 4px;
                }
                """)
        
        # Create and run the application
        app = QApplication(sys.argv)
        app.setApplicationName("Enhanced Base64 Image Transformer")
        app.setApplicationVersion("2.0")
        
        window = EnhancedBase64Transformer()
        window.show()
        
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"Error importing application components: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
>>>>>>> da3aa0d9bd1300a182f7306f879a5bc66263a78f
=======
"""
Main entry point for the Enhanced Base64 Transformer package.
This allows the package to be run with: python -m enhanced_base64_transformer
"""

import sys
import os
from pathlib import Path

def main() -> None:
    """Main entry point for the application."""
    try:
        # Add project root to path for legacy imports
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))
        
        # Import the working legacy transformer
        from legacy.Base64ImageTransformer import Base64ImageTransformer
        from PyQt6.QtWidgets import QApplication, QPushButton, QHBoxLayout
        
        class EnhancedBase64Transformer(Base64ImageTransformer):
            """Enhanced version with theme support"""
            
            def __init__(self):
                super().__init__()
                self.setWindowTitle("Enhanced Base64 Image Transformer")
                self.is_dark_theme = False
                self.add_theme_controls()
                
            def add_theme_controls(self):
                """Add theme toggle controls"""
                from PyQt6.QtWidgets import QVBoxLayout
                
                theme_layout = QHBoxLayout()
                
                self.theme_button = QPushButton("Toggle Dark Theme")
                self.theme_button.clicked.connect(self.toggle_theme)
                theme_layout.addWidget(self.theme_button)
                theme_layout.addStretch()
                
                # Insert at top of first tab
                tab_layout = self.tab_file_to_b64.layout()
                if isinstance(tab_layout, QVBoxLayout):
                    tab_layout.insertLayout(0, theme_layout)
                
            def toggle_theme(self):
                """Toggle theme"""
                if self.is_dark_theme:
                    self.setStyleSheet("")
                    self.theme_button.setText("Toggle Dark Theme")
                else:
                    self.apply_dark_theme()
                    self.theme_button.setText("Toggle Light Theme")
                self.is_dark_theme = not self.is_dark_theme
                
            def apply_dark_theme(self):
                """Apply comprehensive dark theme"""
                self.setStyleSheet("""
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
                }
                QProgressBar::chunk {
                    background-color: #4a90e2;
                    border-radius: 4px;
                }
                """)
        
        # Create and run the application
        app = QApplication(sys.argv)
        app.setApplicationName("Enhanced Base64 Image Transformer")
        app.setApplicationVersion("2.0")
        
        window = EnhancedBase64Transformer()
        window.show()
        
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"Error importing application components: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
>>>>>>> da3aa0d9bd1300a182f7306f879a5bc66263a78f
