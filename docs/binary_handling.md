# Binary Handling Standard

This repository stores binary artifacts as Base64‑encoded text files to keep
the Git history lightweight and reviewable. Use the helper script
`scripts/binary_to_base64.py` whenever a new binary file needs to be added.

## Steps

1. Run the script with the path to the binary file:

   ```bash
   python scripts/binary_to_base64.py path/to/file.bin
   ```

2. Commit the staged `.gitignore` and `*_zip_base64.txt` files.

The original binary remains on disk but is no longer tracked by Git. The Base64
representation can be decoded by reversing the steps in the script.

