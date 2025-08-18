<<<<<<< HEAD
# Enhanced Base64 Image Transformer

A modern, feature-rich PyQt6-based application for encoding files to Base64 and decoding Base64 strings back to files, with enhanced user experience and performance improvements.

## Features

### 🚀 Enhanced Features
- **Modern PyQt6 Interface**: Updated from PyQt5 with better performance and modern styling
- **Batch Processing**: Process multiple files simultaneously
- **File History**: Track recently processed files for quick access
- **Progress Tracking**: Real progress indication for large file operations
- **Drag & Drop**: Enhanced drag-and-drop with multi-file support
- **Preview Improvements**: Better image preview with zoom and pan capabilities
- **Settings Management**: Persistent user preferences and configuration
- **Error Recovery**: Robust error handling with detailed feedback

### 🔧 Technical Improvements
- **Modular Architecture**: Clean separation of concerns with dedicated modules
- **Modern Threading**: Uses QThreadPool and QRunnable for better resource management
- **Type Safety**: Comprehensive type hints throughout the codebase
- **Memory Management**: Proper resource cleanup and memory optimization
- **File Validation**: Advanced file type detection and validation
- **Async Operations**: Non-blocking UI with proper progress feedback

## Installation

### Requirements
- Python 3.8 or higher
- PyQt6
- Pillow (PIL)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Development Installation
```bash
pip install -e .
```

## Usage

### Running the Application
```bash
python main.py
```

Or if installed as a package:
```bash
base64-transformer
```

### Basic Operations

#### File to Base64
1. Switch to the "File to Base64" tab
2. Click "Select File" or drag & drop files
3. Copy the generated Base64 string to clipboard
4. Use batch processing for multiple files

#### Base64 to Image
1. Switch to the "Base64 to Image" tab
2. Paste Base64 string in the input area
3. Click "Decode" to preview the image
4. Save the decoded image in various formats

### Enhanced Base64 ZIP Transformer

The ZIP-oriented variant mirrors the image tool but works with archive files.

#### ZIP to Base64
1. Switch to the "ZIP to Base64" tab.
2. Select a `.zip` file.
3. Copy the generated Base64 string.

#### Base64 to ZIP
1. Switch to the "Base64 to ZIP" tab.
2. Paste a Base64 string and decode.
3. Inspect the listed archive entries and save the reconstructed `.zip` file.

Run the ZIP variant with:

```bash
python -m enhanced_base64_transformer_zip
```

### ZIP to Base64
1. Switch to the "ZIP to Base64" tab.
2. Select a `.zip` file to encode.
3. Copy the resulting Base64 text.

### Base64 to ZIP
1. Switch to the "Base64 to ZIP" tab.
2. Paste Base64 text representing a ZIP archive.
3. Decode to view archive entries and optionally save the ZIP file.

### Advanced Features

#### Custom Preview Sizes
- Set maximum width/height for image previews
- Dynamic scaling based on window size
- Zoom and pan capabilities for large images

#### Batch Processing
- Select multiple files for encoding
- Queue management with progress tracking
- Export results to various formats

#### Settings & Preferences
- Customize default directories
- Set file size limits
- Configure UI themes and layouts

## Project Structure

```
src/
├── ui/                 # User interface modules
│   ├── main_window.py  # Main application window
│   ├── tabs/          # Individual tab implementations
│   └── dialogs/       # Dialog windows
├── workers/           # Background processing
│   ├── encode_worker.py
│   ├── decode_worker.py
│   └── batch_worker.py
├── utils/             # Utility functions
│   ├── file_utils.py
│   ├── validation.py
│   └── settings.py
└── resources/         # Application resources
    ├── styles.qss
    └── settings.json
```

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Quality
```bash
# Type checking
mypy src/

# Linting
flake8 src/

# Formatting
black src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Changelog

### Version 2.0.0
- Complete rewrite with PyQt6
- Modular architecture implementation
- Added batch processing capabilities
- Enhanced error handling and user feedback
- Improved memory management and performance
- Added comprehensive test suite

### Version 1.0.0
- Initial PyQt5 implementation
- Basic file encoding/decoding functionality
- Simple drag-and-drop support
=======
# Enhanced Base64 Image Transformer

A modern, feature-rich PyQt6-based application for encoding files to Base64 and decoding Base64 strings back to files, with enhanced user experience and performance improvements.

## Features

### 🚀 Enhanced Features
- **Modern PyQt6 Interface**: Updated from PyQt5 with better performance and modern styling
- **Batch Processing**: Process multiple files simultaneously
- **File History**: Track recently processed files for quick access
- **Progress Tracking**: Real progress indication for large file operations
- **Drag & Drop**: Enhanced drag-and-drop with multi-file support
- **Preview Improvements**: Better image preview with zoom and pan capabilities
- **Settings Management**: Persistent user preferences and configuration
- **Error Recovery**: Robust error handling with detailed feedback

### 🔧 Technical Improvements
- **Modular Architecture**: Clean separation of concerns with dedicated modules
- **Modern Threading**: Uses QThreadPool and QRunnable for better resource management
- **Type Safety**: Comprehensive type hints throughout the codebase
- **Memory Management**: Proper resource cleanup and memory optimization
- **File Validation**: Advanced file type detection and validation
- **Async Operations**: Non-blocking UI with proper progress feedback

## Installation

### Requirements
- Python 3.8 or higher
- PyQt6
- Pillow (PIL)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Development Installation
```bash
pip install -e .
```

## Usage

### Running the Application
```bash
python main.py
```

Or if installed as a package:
```bash
base64-transformer
```

### Basic Operations

#### File to Base64
1. Switch to the "File to Base64" tab
2. Click "Select File" or drag & drop files
3. Copy the generated Base64 string to clipboard
4. Use batch processing for multiple files

#### Base64 to Image
1. Switch to the "Base64 to Image" tab
2. Paste Base64 string in the input area
3. Click "Decode" to preview the image
4. Save the decoded image in various formats

### Enhanced Base64 ZIP Transformer

The ZIP-oriented variant mirrors the image tool but works with archive files.

#### ZIP to Base64
1. Switch to the "ZIP to Base64" tab.
2. Select a `.zip` file.
3. Copy the generated Base64 string.

#### Base64 to ZIP
1. Switch to the "Base64 to ZIP" tab.
2. Paste a Base64 string and decode.
3. Inspect the listed archive entries and save the reconstructed `.zip` file.

Run the ZIP variant with:

```bash
python -m enhanced_base64_transformer_zip
```

### ZIP to Base64
1. Switch to the "ZIP to Base64" tab.
2. Select a `.zip` file to encode.
3. Copy the resulting Base64 text.

### Base64 to ZIP
1. Switch to the "Base64 to ZIP" tab.
2. Paste Base64 text representing a ZIP archive.
3. Decode to view archive entries and optionally save the ZIP file.

### Advanced Features

#### Custom Preview Sizes
- Set maximum width/height for image previews
- Dynamic scaling based on window size
- Zoom and pan capabilities for large images

#### Batch Processing
- Select multiple files for encoding
- Queue management with progress tracking
- Export results to various formats

#### Settings & Preferences
- Customize default directories
- Set file size limits
- Configure UI themes and layouts

## Project Structure

```
src/
├── ui/                 # User interface modules
│   ├── main_window.py  # Main application window
│   ├── tabs/          # Individual tab implementations
│   └── dialogs/       # Dialog windows
├── workers/           # Background processing
│   ├── encode_worker.py
│   ├── decode_worker.py
│   └── batch_worker.py
├── utils/             # Utility functions
│   ├── file_utils.py
│   ├── validation.py
│   └── settings.py
└── resources/         # Application resources
    ├── styles.qss
    └── settings.json
```

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Quality
```bash
# Type checking
mypy src/

# Linting
flake8 src/

# Formatting
black src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Changelog

### Version 2.0.0
- Complete rewrite with PyQt6
- Modular architecture implementation
- Added batch processing capabilities
- Enhanced error handling and user feedback
- Improved memory management and performance
- Added comprehensive test suite

### Version 1.0.0
- Initial PyQt5 implementation
- Basic file encoding/decoding functionality
- Simple drag-and-drop support
>>>>>>> a129e6744e1b47cc89dc5c3c88d9a831f377652b
