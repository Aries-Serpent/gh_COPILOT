<<<<<<< HEAD
#!/usr/bin/env python3
"""
Enhanced Base64 Image Transformer v2.0
Main application entry point.
"""

import sys
import os
from pathlib import Path

def main():
    """Main application entry point."""
    try:
        # Try to import the modular version first
        # Add src to path for imports
        src_path = Path(__file__).parent / "src"
        sys.path.insert(0, str(src_path))
        
        # Import Qt modules
        from PyQt6.QtWidgets import QApplication, QMessageBox
        from PyQt6.QtCore import Qt, QTimer
        from PyQt6.QtGui import QIcon
        
        print("Loading Enhanced Base64 Image Transformer...")
        
        # Try to import application modules
        try:
            from ui.main_window import MainWindow, create_application
            
            # Create application
            app = create_application()
            
            # Create and show main window
            window = MainWindow()
            window.show()
            
            print("Application started successfully!")
            
            # Start event loop
            sys.exit(app.exec())
            
        except ImportError as import_err:
            print(f"Import error in modular version: {import_err}")
            print("Falling back to simple version...")
            
            # Fall back to simple version
            try:
                # Import the fallback version from src
                from fallback_main import main as fallback_main_main
                
                # Run the fallback version
                fallback_main_main()
                
            except Exception as fallback_err:
                print(f"Fallback to simple version failed: {fallback_err}")
                
                # Show error dialog if possible
                app = QApplication(sys.argv)
                QMessageBox.critical(
                    None, 
                    "Application Error", 
                    f"Failed to start application:\n\nModular version error: {import_err}\n\nSimple version error: {fallback_err}"
                )
                sys.exit(1)
        
    except ImportError as e:
        if "PyQt6" in str(e):
            print("Error: PyQt6 is not installed.")
            print("Please install the required dependencies with:")
            print("pip install -r requirements.txt")
            sys.exit(1)
        else:
            print(f"Import error: {e}")
            sys.exit(1)
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
=======
#!/usr/bin/env python3
"""
Enhanced Base64 Image Transformer v2.0
Main application entry point.
"""

import sys
import os
from pathlib import Path

def main():
    """Main application entry point."""
    try:
        # Try to import the modular version first
        # Add src to path for imports
        src_path = Path(__file__).parent / "src"
        sys.path.insert(0, str(src_path))
        
        # Import Qt modules
        from PyQt6.QtWidgets import QApplication, QMessageBox
        from PyQt6.QtCore import Qt, QTimer
        from PyQt6.QtGui import QIcon
        
        print("Loading Enhanced Base64 Image Transformer...")
        
        # Try to import application modules
        try:
            from ui.main_window import MainWindow, create_application
            
            # Create application
            app = create_application()
            
            # Create and show main window
            window = MainWindow()
            window.show()
            
            print("Application started successfully!")
            
            # Start event loop
            sys.exit(app.exec())
            
        except ImportError as import_err:
            print(f"Import error in modular version: {import_err}")
            print("Falling back to simple version...")
            
            # Fall back to simple version
            try:
                # Import the fallback version from src
                from fallback_main import main as fallback_main_main
                
                # Run the fallback version
                fallback_main_main()
                
            except Exception as fallback_err:
                print(f"Fallback to simple version failed: {fallback_err}")
                
                # Show error dialog if possible
                app = QApplication(sys.argv)
                QMessageBox.critical(
                    None, 
                    "Application Error", 
                    f"Failed to start application:\n\nModular version error: {import_err}\n\nSimple version error: {fallback_err}"
                )
                sys.exit(1)
        
    except ImportError as e:
        if "PyQt6" in str(e):
            print("Error: PyQt6 is not installed.")
            print("Please install the required dependencies with:")
            print("pip install -r requirements.txt")
            sys.exit(1)
        else:
            print(f"Import error: {e}")
            sys.exit(1)
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
>>>>>>> a129e6744e1b47cc89dc5c3c88d9a831f377652b
