#!/usr/bin/env python3
"""
🔓 Base64 ZIP Decoder and Extractor
Decodes base64-encoded ZIP files and extracts their contents
"""

import base64
import binascii
import logging
import os
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

def decode_and_extract_base64_zip(base64_string: str, output_dir: str = None) -> dict:
    """
    🔓 Decode base64 ZIP file and extract contents
    
    Args:
        base64_string: The base64-encoded ZIP content
        output_dir: Directory to extract files (optional, defaults to temp)
    
    Returns:
        dict: Extraction results with file list and metadata
    """
    
    logger.info("Base64 ZIP decoder starting")
    logger.info("Input size: %d characters", len(base64_string))

    try:
        zip_bytes = base64.b64decode(base64_string)
        logger.info("Decoded %d bytes", len(zip_bytes))
    except binascii.Error as exc:
        logger.error("Failed to decode base64: %s", exc)
        raise

    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip.write(zip_bytes)
        temp_zip_path = temp_zip.name
    logger.info("Temporary ZIP file: %s", temp_zip_path)

    if output_dir is None:
        output_dir = f"extracted_files_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    logger.info("Extracting to %s", output_path)

    extracted_files = []
    try:
        with zipfile.ZipFile(temp_zip_path, "r") as zip_ref:
            zip_info = zip_ref.infolist()
            logger.info("ZIP contains %d files", len(zip_info))
            for file_info in zip_info:
                logger.info("Extracting: %s", file_info.filename)
                zip_ref.extract(file_info, output_path)
                extracted_file_path = output_path / file_info.filename
                extracted_files.append(
                    {
                        "filename": file_info.filename,
                        "size": file_info.file_size,
                        "compressed_size": file_info.compress_size,
                        "modified": datetime(*file_info.date_time),
                        "full_path": str(extracted_file_path),
                    }
                )
    except zipfile.BadZipFile as exc:
        logger.error("Invalid ZIP file: %s", exc)
        raise
    except OSError as exc:
        logger.error("Filesystem error: %s", exc)
        raise
    finally:
        try:
            os.unlink(temp_zip_path)
        except OSError:
            logger.error("Failed to remove temporary file: %s", temp_zip_path)

    results = {
        "success": True,
        "output_directory": str(output_path),
        "total_files": len(extracted_files),
        "extracted_files": extracted_files,
        "total_size": sum(f["size"] for f in extracted_files),
        "extraction_time": datetime.now().isoformat(),
    }
    logger.info(
        "Extraction completed: output=%s files=%d size=%d bytes",
        output_path,
        len(extracted_files),
        results["total_size"],
    )
    return results

def analyze_extracted_files(results: dict):
    """📊 Analyze extracted files and show detailed information"""
    
    if not results["success"]:
        logger.error("Cannot analyze - extraction failed: %s", results.get("error"))
        return

    logger.info("DETAILED FILE ANALYSIS:")
    for file_info in results["extracted_files"]:
        logger.info("%s", file_info["filename"])
        logger.info("   Size: %d bytes", file_info["size"])
        logger.info("   Compressed: %d bytes", file_info["compressed_size"])
        logger.info("   Modified: %s", file_info["modified"])
        logger.info("   Path: %s", file_info["full_path"])

if __name__ == "__main__":
    # Your base64 ZIP content (you'll paste it here)
    base64_zip_content = """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"""
    
    logger.info("Base64 ZIP Decoder Utility")
    logger.info("=" * 50)
    
    # Extract to timestamped directory
    output_directory = f"decoded_zip_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Decode and extract
    results = decode_and_extract_base64_zip(base64_zip_content, output_directory)
    
    # Show detailed analysis
    analyze_extracted_files(results)
    
    if results['success']:
        logger.info("SUCCESS: Files extracted to '%s'", results['output_directory'])
        logger.info(
            "Summary: %d files, %d bytes total",
            results['total_files'],
            results['total_size'],
        )
    else:
        logger.error("FAILED: %s", results['error'])
