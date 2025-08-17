# setup_ingest_audit

The `setup_ingest_audit` helper orchestrates initial database creation,
asset ingestion, and a placeholder audit with dual-copilot validation.

## Usage

Run the automation from the repository root:

```bash
python scripts/automation/setup_ingest_audit.py
```

Ensure `GH_COPILOT_WORKSPACE` points at the workspace root and
`ALLOW_AUTOLFS=1` so any large artifacts remain Git LFS managed.

## Detecting LFS pointer mismatches

A file tracked by Git LFS should contain only a small pointer file. To verify
that a file still contains the pointer rather than raw binary data, compare the
pointer metadata with the file's SHA:

```bash
git lfs pointer --file path/to/file
sha256sum path/to/file
```

If `git lfs pointer` reports an `oid` that does **not** match the `sha256sum`
output, the file has likely been replaced by its binary contents.

## Recovery

Use the `lfs_restore.sh` helper to rehydrate the pointer and download the
binary object in one step:

```bash
./scripts/lfs_restore.sh path/to/file
```

The script removes the bad file, checks out the pointer from Git, and pulls the
referenced LFS object. If the helper is unavailable, perform those steps
manually:

```bash
rm path/to/file
git checkout HEAD -- path/to/file
git lfs pull -I path/to/file
```



### Installation
```bash
pip install -r requirements.txt
```

> Note: This project requires `PyYAML>=6.0.1`.
