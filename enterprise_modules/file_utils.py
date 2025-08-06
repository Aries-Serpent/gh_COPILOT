#!/usr/bin/env python3
"""
Enterprise File Utils Module
gh_COPILOT Toolkit - Modular Architecture

File operation utilities extracted from 4 enterprise scripts
Standardized file reading, writing, and encoding handling

Usage:
    from enterprise_modules.file_utils import read_file_with_encoding_detection, write_file_safely
"""

try:
    import chardet  # type: ignore
except Exception:  # pragma: no cover - chardet is optional
    chardet = None
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime
import logging

from enterprise_modules.compliance import (
    ComplianceError,
    validate_enterprise_operation,
)


def read_file_with_encoding_detection(
    file_path: str,
    fallback_encoding: str = 'utf-8'
) -> Tuple[Optional[str], str]:
    """
    Read file with automatic encoding detection

    Extracted from scripts:
    - unicode_flake8_master_controller.py
    - phase12_e999_syntax_error_specialist.py
    """
    file_path_obj = Path(file_path)

    if not file_path_obj.exists():
        logging.error(f"File does not exist: {file_path}")
        return None, "FILE_NOT_FOUND"

    try:
        # Read raw bytes for encoding detection
        with open(file_path_obj, 'rb') as f:
            raw_data = f.read()

        # Detect encoding if library available
        detected_encoding: Optional[str] = None
        confidence: float = 0.0
        if chardet is not None:
            result = chardet.detect(raw_data)
            detected_encoding = result.get('encoding')
            confidence = result.get('confidence', 0.0)

        # Use detected encoding if confidence is high enough
        if confidence > 0.7 and detected_encoding:
            try:
                content = raw_data.decode(detected_encoding)
                return content, f"SUCCESS_DETECTED_{detected_encoding}"
            except UnicodeDecodeError:
                pass

        # Fallback to specified encoding
        try:
            content = raw_data.decode(fallback_encoding)
            return content, f"SUCCESS_FALLBACK_{fallback_encoding}"
        except UnicodeDecodeError:
            # Last resort: ignore errors
            content = raw_data.decode(fallback_encoding, errors='ignore')
            return content, f"SUCCESS_IGNORE_ERRORS_{fallback_encoding}"

    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return None, f"ERROR_{str(e)}"


def read_file_safely(
    file_path: str,
    encoding: str = 'utf-8',
    errors: str = 'ignore'
) -> Optional[str]:
    """
    Read file safely with error handling

    Extracted from scripts:
    - phase12_1_enhanced_e999_repair_specialist.py
    - enterprise_dual_copilot_validator.py
    """
    try:
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            logging.warning(f"File does not exist: {file_path}")
            return None

        with open(file_path_obj, 'r', encoding=encoding, errors=errors) as f:
            return f.read()

    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return None


def write_file_safely(
    file_path: str,
    content: str,
    encoding: str = 'utf-8',
    create_parents: bool = True,
    backup_existing: bool = False
) -> bool:
    """Write file safely with enterprise validation and optional backup."""
    file_path_obj = Path(file_path)

    if not validate_enterprise_operation(str(file_path_obj)):
        raise ComplianceError(f"Forbidden write operation: {file_path_obj}")

    try:
        # Create parent directories if needed
        if create_parents:
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Backup existing file if requested
        if backup_existing and file_path_obj.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_suffix = f".backup_{timestamp}{file_path_obj.suffix}"
            backup_path = file_path_obj.with_suffix(backup_suffix)
            try:
                backup_path.write_text(
                    file_path_obj.read_text(encoding=encoding), encoding=encoding
                )
                logging.info(f"Backup created: {backup_path}")
            except Exception as e:
                logging.warning(f"Could not create backup: {e}")

        # Write content
        with open(file_path_obj, 'w', encoding=encoding) as f:
            f.write(content)

        return True

    except Exception as e:
        logging.error(f"Error writing file {file_path}: {e}")
        return False


def copy_file_safely(
    source_path: str,
    destination_path: str,
    overwrite: bool = False
) -> bool:
    """Copy file safely with enterprise validation."""
    import shutil

    source = Path(source_path)
    destination = Path(destination_path)

    if not validate_enterprise_operation(str(destination)):
        raise ComplianceError(f"Forbidden copy destination: {destination}")

    try:
        if not source.exists():
            logging.error(f"Source file does not exist: {source_path}")
            return False

        if destination.exists() and not overwrite:
            logging.warning(f"Destination exists and overwrite=False: {destination_path}")
            return False

        # Create parent directories
        destination.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        shutil.copy2(source, destination)

        return True

    except Exception as e:
        logging.error(
            f"Error copying file from {source_path} to {destination_path}: {e}"
        )
        return False


def list_files_by_pattern(
    directory_path: str,
    pattern: str = "*.py",
    recursive: bool = True
) -> list:
    """
    List files matching pattern with optional recursion
    """
    try:
        dir_path = Path(directory_path)

        if not dir_path.exists():
            logging.error(f"Directory does not exist: {directory_path}")
            return []

        if recursive:
            return list(dir_path.rglob(pattern))
        else:
            return list(dir_path.glob(pattern))

    except Exception as e:
        logging.error(f"Error listing files in {directory_path}: {e}")
        return []


def get_file_info(file_path: str) -> dict:
    """
    Get comprehensive file information
    """
    try:
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            return {'exists': False, 'error': 'File not found'}

        stat = file_path_obj.stat()

        return {
            'exists': True,
            'size_bytes': stat.st_size,
            'size_human': f"{stat.st_size:,} bytes",
            'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'is_file': file_path_obj.is_file(),
            'is_directory': file_path_obj.is_dir(),
            'extension': file_path_obj.suffix,
            'name': file_path_obj.name,
            'parent': str(file_path_obj.parent)
        }

    except Exception as e:
        return {'exists': False, 'error': str(e)}


# Enterprise Module Metadata
__version__ = "1.0.0"
__author__ = "gh_COPILOT Enterprise Toolkit"
__description__ = "File operation utilities for enterprise scripts"
__extracted_from_scripts__ = 4
__lines_saved__ = 90
__implementation_priority__ = "MEDIUM"
