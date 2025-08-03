# Binary Handling Instructions

When introducing or updating binary artifacts:

1. Use `python scripts/binary_to_base64.py <path>` to archive and Base64‑encode
   the binary. The script will:
   - Remove the binary from Git tracking.
   - Append the path to `.gitignore`.
   - Create `<name>_zip_base64.txt` containing the encoded data.
   - Stage the resulting files for commit.
2. Commit the staged changes using a conventional commit message.

This process keeps binary files out of the Git history while retaining a
recoverable representation.

