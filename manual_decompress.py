#!/usr/bin/env python3
"""
🔧 Manual File Decompression Tool
Attempts to decompress the extracted file using different methods
"""

import zlib
from pathlib import Path

def try_decompress_file(file_path: str):
    """Try different decompression methods on a file"""
    
    print(f"🔧 Attempting to decompress: {file_path}")
    
    try:
        with open(file_path, 'rb') as f:
            compressed_data = f.read()
        
        print(f"📊 File size: {len(compressed_data)} bytes")
        print(f"🔍 First 32 bytes: {compressed_data[:32].hex()}")
        
        # Try different decompression methods
        methods = [
            ("Raw DEFLATE (-15)", lambda data: zlib.decompress(data, -15)),
            ("Standard DEFLATE", lambda data: zlib.decompress(data)),
            ("GZIP", lambda data: zlib.decompress(data, 16+zlib.MAX_WBITS)),
            ("Auto DEFLATE", lambda data: zlib.decompress(data, -zlib.MAX_WBITS)),
        ]
        
        for method_name, decompress_func in methods:
            try:
                print(f"\n🔄 Trying {method_name}...")
                decompressed = decompress_func(compressed_data)
                print(f"✅ SUCCESS! Decompressed to {len(decompressed)} bytes")
                
                # Save decompressed file
                output_path = file_path + ".decompressed"
                with open(output_path, 'wb') as f:
                    f.write(decompressed)
                print(f"💾 Saved decompressed file to: {output_path}")
                
                # Show first few lines if it's text
                try:
                    text_content = decompressed.decode('utf-8')
                    lines = text_content.split('\n')[:10]
                    print(f"\n📋 First 10 lines of content:")
                    for i, line in enumerate(lines, 1):
                        print(f"{i:2d}: {line}")
                    
                    if len(lines) >= 10:
                        print("    ... (truncated)")
                    
                    return True
                    
                except UnicodeDecodeError:
                    print("📋 Content appears to be binary data")
                    return True
                    
            except Exception as e:
                print(f"❌ {method_name} failed: {e}")
        
        print("\n❌ All decompression methods failed")
        return False
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

if __name__ == "__main__":
    # Find the recovered file
    recovered_dirs = list(Path('.').glob('recovered_files_*'))
    if recovered_dirs:
        latest_dir = max(recovered_dirs, key=lambda p: p.stat().st_mtime)
        files = list(latest_dir.glob('*'))
        if files:
            file_to_decompress = files[0]
            print(f"🎯 Found file to decompress: {file_to_decompress}")
            success = try_decompress_file(str(file_to_decompress))
            
            if success:
                print(f"\n🎉 Decompression successful!")
            else:
                print(f"\n❌ Decompression failed")
        else:
            print("❌ No files found in recovery directory")
    else:
        print("❌ No recovery directories found")
