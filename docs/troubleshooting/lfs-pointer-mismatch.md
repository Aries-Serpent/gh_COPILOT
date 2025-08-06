# Resolving Git LFS Pointer Mismatch

When a file tracked by Git LFS is replaced by its binary contents instead of the expected pointer, you may see a "pointer mismatch" error. Follow these steps using `production.db` as an example. Ensure `ALLOW_AUTOLFS=1` is set so large files remain LFS-managed.

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
