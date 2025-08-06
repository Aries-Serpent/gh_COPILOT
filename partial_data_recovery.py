#!/usr/bin/env python3
"""
🔧 Partial Data Recovery Tool
Attempts to recover readable content from partial/corrupted data
"""

import re
from pathlib import Path

def analyze_raw_data(file_path: str):
    """Analyze raw data for readable content"""
    
    print(f"🔍 Analyzing raw data: {file_path}")
    
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        
        print(f"📊 File size: {len(data)} bytes")
        
        # Try to find readable ASCII/UTF-8 strings
        readable_strings = []
        current_string = ""
        
        for byte in data:
            if 32 <= byte <= 126:  # Printable ASCII
                current_string += chr(byte)
            else:
                if len(current_string) >= 4:  # Only keep strings of 4+ characters
                    readable_strings.append(current_string)
                current_string = ""
        
        if current_string and len(current_string) >= 4:
            readable_strings.append(current_string)
        
        print(f"📋 Found {len(readable_strings)} readable strings")
        
        # Filter for Python-like content
        python_keywords = ['def ', 'class ', 'import ', 'from ', 'return ', 'if ', 'else:', 'elif ', 'for ', 'while ', 'try:', 'except', '__init__', 'self.']
        python_strings = []
        
        for s in readable_strings:
            if any(keyword in s for keyword in python_keywords):
                python_strings.append(s)
        
        print(f"🐍 Found {len(python_strings)} Python-related strings")
        
        # Show the longest/most interesting strings
        all_strings = sorted(readable_strings, key=len, reverse=True)[:20]
        
        print(f"\n📝 Top readable content:")
        for i, s in enumerate(all_strings[:10], 1):
            clean_s = s.strip()
            if clean_s:
                print(f"{i:2d}: {clean_s}")
        
        # Look for file paths or URLs
        print(f"\n🗂️ Potential file paths/URLs:")
        for s in readable_strings:
            if '/' in s or '\\' in s or '.py' in s or '.json' in s:
                print(f"   - {s}")
        
        # Save all readable content to a text file
        output_file = file_path + ".readable.txt"
        with open(output_file, 'w', encoding='utf-8', errors='ignore') as f:
            f.write("=== READABLE STRINGS FROM CORRUPTED FILE ===\n\n")
            for s in readable_strings:
                if len(s.strip()) > 3:
                    f.write(s + '\n')
        
        print(f"\n💾 Saved readable content to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def hex_dump_analysis(file_path: str, max_bytes: int = 200):
    """Show hex dump of the beginning of the file"""
    
    print(f"\n🔍 Hex dump analysis (first {max_bytes} bytes):")
    
    try:
        with open(file_path, 'rb') as f:
            data = f.read(max_bytes)
        
        for i in range(0, len(data), 16):
            hex_part = ' '.join(f'{b:02x}' for b in data[i:i+16])
            ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in data[i:i+16])
            print(f'{i:08x}: {hex_part:<48} |{ascii_part}|')
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Find the recovered file
    recovered_dirs = list(Path('.').glob('recovered_files_*'))
    if recovered_dirs:
        latest_dir = max(recovered_dirs, key=lambda p: p.stat().st_mtime)
        files = list(latest_dir.glob('*'))
        if files:
            file_to_analyze = files[0]
            print(f"🎯 Found file to analyze: {file_to_analyze}")
            
            # Show hex dump
            hex_dump_analysis(str(file_to_analyze))
            
            # Analyze for readable content
            analyze_raw_data(str(file_to_analyze))
            
        else:
            print("❌ No files found in recovery directory")
    else:
        print("❌ No recovery directories found")
