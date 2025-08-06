# Resolving Git LFS Pointer Mismatch

When a file tracked by Git LFS is replaced by its binary contents instead of the expected pointer, you may see a "pointer mismatch" error. Ensure `ALLOW_AUTOLFS=1` is set so large files remain LFS-managed.

## Detecting a mismatch

Compare the pointer metadata with the file's SHA hash:

```bash
git lfs pointer --file production.db
sha256sum production.db
```

If the `oid sha256` shown by `git lfs pointer` does not match the `sha256sum`
output, the file has been replaced by binary content.

## 1. Remove the mismatched file

```bash
rm production.db
```

## 2. Restore the LFS pointer

Checkout the pointer version from the current commit:

```bash
git checkout HEAD -- production.db
```

## 3. Pull the LFS object

Fetch the binary content referenced by the pointer:

```bash
git lfs pull -I production.db
```

## 4. Verify tracking and content

Confirm the file is tracked by LFS and the binary is restored:

```bash
git lfs ls-files | grep production.db
file production.db
```

If the output lists `production.db` and the `file` command reports a valid SQLite database, the pointer mismatch has been resolved.

## Helper script

The [`lfs_restore.sh`](../../scripts/lfs_restore.sh) helper automates steps 1–3:

```bash
../../scripts/lfs_restore.sh production.db
```

Use this script to quickly remove the bad file, check out the pointer, and
download the correct LFS object.
