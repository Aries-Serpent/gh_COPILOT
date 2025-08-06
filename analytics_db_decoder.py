#!/usr/bin/env python3
"""
Analytics Database Base64 Decoder
Decodes the analytics_db_zip_base64.txt file
"""

import base64
import zipfile
import io
import os
import struct
import tempfile
from pathlib import Path

def read_base64_file():
    """Read the base64 content from the analytics file"""
    file_path = "databases/analytics_db_zip_base64.txt"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        print(f"Read {len(content)} characters from {file_path}")
        return content
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def decode_and_analyze(base64_content):
    """Decode base64 content and analyze the result"""
    try:
        # Decode base64
        decoded_data = base64.b64decode(base64_content)
        print(f"Decoded {len(decoded_data)} bytes from base64")
        
        # Check file signature
        if len(decoded_data) >= 4:
            signature = decoded_data[:4].hex()
            print(f"File signature: {signature}")
            
            # Check for ZIP signature
            if decoded_data[:2] == b'PK':
                print("ZIP signature detected!")
                return analyze_zip_content(decoded_data)
            else:
                print("Not a ZIP file, checking other formats...")
                return analyze_raw_content(decoded_data)
        
    except Exception as e:
        print(f"Error decoding base64: {e}")
        return None

def analyze_zip_content(data):
    """Analyze ZIP file content"""
    try:
        # Try to read as ZIP
        with zipfile.ZipFile(io.BytesIO(data), 'r') as zip_file:
            print("\nZIP File Analysis:")
            print("==================")
            
            # List files in ZIP
            file_list = zip_file.namelist()
            print(f"Files in ZIP: {len(file_list)}")
            
            for filename in file_list:
                file_info = zip_file.getinfo(filename)
                print(f"  - {filename}")
                print(f"    Size: {file_info.file_size} bytes")
                print(f"    Compressed: {file_info.compress_size} bytes")
                print(f"    Modified: {file_info.date_time}")
                
                # Extract and preview content
                if file_info.file_size < 10000:  # Only preview small files
                    try:
                        content = zip_file.read(filename)
                        if filename.endswith('.py'):
                            print(f"    Python file content preview:")
                            preview = content.decode('utf-8')[:500]
                            print(f"    {preview}...")
                        elif filename.endswith('.txt'):
                            print(f"    Text file content preview:")
                            preview = content.decode('utf-8')[:200]
                            print(f"    {preview}...")
                    except Exception as e:
                        print(f"    Error reading content: {e}")
            
            # Extract all files to a temp directory
            temp_dir = tempfile.mkdtemp(prefix="analytics_db_")
            print(f"\nExtracting files to: {temp_dir}")
            
            zip_file.extractall(temp_dir)
            print("Extraction complete!")
            
            return temp_dir
            
    except zipfile.BadZipFile:
        print("Invalid ZIP file, trying manual recovery...")
        return manual_zip_recovery(data)
    except Exception as e:
        print(f"Error analyzing ZIP: {e}")
        return None

def manual_zip_recovery(data):
    """Manual ZIP file recovery for corrupted archives"""
    print("\nManual ZIP Recovery:")
    print("===================")
    
    try:
        # Look for local file headers (PK\x03\x04)
        pos = 0
        files_found = []
        
        while pos < len(data) - 30:
            if data[pos:pos+4] == b'PK\x03\x04':
                print(f"Found local file header at position {pos}")
                
                # Parse local file header
                header = data[pos:pos+30]
                if len(header) >= 30:
                    # Extract filename length and extra field length
                    filename_len = struct.unpack('<H', header[26:28])[0]
                    extra_len = struct.unpack('<H', header[28:30])[0]
                    
                    # Extract filename
                    filename_start = pos + 30
                    filename_end = filename_start + filename_len
                    
                    if filename_end <= len(data):
                        filename = data[filename_start:filename_end].decode('utf-8', errors='ignore')
                        files_found.append({
                            'position': pos,
                            'filename': filename,
                            'header_size': 30 + filename_len + extra_len
                        })
                        print(f"  Filename: {filename}")
                
                pos += 4
            else:
                pos += 1
        
        print(f"Found {len(files_found)} file entries")
        return files_found
        
    except Exception as e:
        print(f"Error in manual recovery: {e}")
        return None

def analyze_raw_content(data):
    """Analyze raw binary content"""
    print("\nRaw Content Analysis:")
    print("====================")
    
    # Show hex dump of first 100 bytes
    hex_dump = data[:100].hex()
    print(f"First 100 bytes (hex): {hex_dump}")
    
    # Look for readable strings
    try:
        text_content = data.decode('utf-8', errors='ignore')
        readable_chars = ''.join(c for c in text_content if c.isprintable())
        if readable_chars:
            print(f"\nReadable content preview:")
            print(readable_chars[:500])
    except:
        pass
    
    return data

def main():
    print("Analytics Database Base64 Decoder")
    print("=================================")
    
    # Read base64 content
    base64_content = read_base64_file()
    if not base64_content:
        return
    
    # Decode and analyze
    result = decode_and_analyze(base64_content)
    
    if result:
        print(f"\nDecoding completed successfully!")
        if isinstance(result, str):
            print(f"Files extracted to: {result}")
        elif isinstance(result, list):
            print(f"Manual recovery found {len(result)} files")
    else:
        print("Decoding failed")

if __name__ == "__main__":
    main()
