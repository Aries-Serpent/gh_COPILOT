# Enhanced Base64 Image Transformer - Quick Start

## Installation

1. **Install Python 3.8+** (if not already installed)

2. **Install PyQt6:**
   ```bash
   pip install PyQt6
   ```

## Usage

### Option 1: Use the launcher script
```bash
python run.py
```

### Option 2: Run directly
```bash
python main.py
```

## Features

- **File to Base64**: Drag & drop files or use file picker
- **Base64 to Image**: Paste Base64 text and preview images  
- **Theme Toggle**: Switch between light and dark themes
- **Multi-format Support**: PNG, JPEG, BMP image formats
- **Background Processing**: Non-blocking file operations

## Troubleshooting

If you get import errors, make sure PyQt6 is installed:
```bash
pip install PyQt6
```

Enjoy using the Enhanced Base64 Image Transformer! 🎉

## ZIP Variant

Launch the archive-focused edition:

```bash
python -m enhanced_base64_transformer_zip
```

Use "ZIP to Base64" to encode archives and "Base64 to ZIP" to decode and list entries. The `zipfile` module is part of the Python standard library, so no additional installation is required.
