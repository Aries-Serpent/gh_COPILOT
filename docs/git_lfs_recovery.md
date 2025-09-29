# Git LFS Recovery Guide

This guide defines the standardized procedure for restoring Git LFS managed artifacts in gh_COPILOT.

## 1. Verify the Environment

1. Run `bash setup.sh` and activate the virtual environment.
2. Ensure Git LFS is available:
   ```bash
   git lfs install
   ```
3. Review `.gitattributes` to confirm tracked patterns such as:
   - `codex_sessions/*.zip`
   - `*.db`, `*.7z`, `*.zip`, `*.bak`, `*.sqlite`, `*.exe`, `*.dot`
   - `web_gui/documentation/deployment/screenshots/*.png`

These patterns are defined in the repository's [`.gitattributes`](../.gitattributes).

## 2. Retrieve LFS Objects

Fetch and check out LFS pointers to restore missing files:

```bash
git lfs fetch --all
git lfs checkout
```

Use `git lfs ls-files` to verify that all required files are tracked.

## 3. Recover Session Artifacts

For session archives stored under `codex_sessions/`, use the artifact manager's recovery mode:

```bash
python artifact_manager.py --recover <archive>
```

See [ARTIFACT_RECOVERY_WORKFLOW.md](../ARTIFACT_RECOVERY_WORKFLOW.md) for a detailed explanation of packaging, committing, and verifying artifacts.

## 4. Re-track Missing Files

If a binary file is missing from LFS:

1. Track the extension and update pointers:
   ```bash
   git lfs track "*.ext"
   git add .gitattributes <file>
   ```
2. Re-run `git lfs ls-files` to confirm.

## 5. Commit the Recovery

After restoring files, commit the changes using the standard commit workflow. Set `ALLOW_AUTOLFS=1` to allow automatic LFS tracking if new binary types were added.

---

Following this procedure ensures the repository's binary artifacts stay consistent and recoverable.

### Quick refresh of attributes

If patterns change or new binary types appear, refresh tracked attributes and re-stage files:

```bash
bash tools/pre-commit-lfs.sh
git add .gitattributes
```
