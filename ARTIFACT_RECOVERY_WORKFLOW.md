# Artifact Recovery Workflow

This guide explains how the repository packages, commits, and restores
session artifacts while keeping large binary files under Git LFS. It is
intended for contributors and CI jobs running in the Codex environment.

## 1. Continuous Integration Overview

All automation uses `.github/workflows/artifact_lfs.yml` to manage
artifacts. Centralising on a single workflow avoids per-branch
divergence and ensures every run applies the same rules.

## 2. Key CI Workflow Step: Artifact Packaging, Commit, and Sync

Every job that produces artifacts should include:

```yaml
- name: Package, Commit, and Sync Artifacts
  run: python artifact_manager.py --package --commit --sync-gitattributes
```

This single step bundles new files from the temporary directory, commits
the resulting archive, and updates `.gitattributes` so newly introduced
binary types are tracked automatically.

## 3. Why This Approach Works

- Artifacts are never skipped; every run commits its outputs.
- LFS pointers remain accurate, keeping git history lightweight.
- `.gitattributes` stays current, simplifying onboarding and reviews.

## 4. Troubleshooting & Verification

- After packaging, run `git lfs ls-files` to ensure all archives are
  tracked. Missing entries should cause the workflow to fail with a clear
  log message.
- If packaging fails, inspect logs for permission issues, missing
  directories, or absent Git LFS installations.
- Test workflow updates in feature branches to catch platform-specific
  quirks before merging.

## 5. Important Configuration Files & CLI Options

### `.codex_lfs_policy.yaml`

Controls automatic Git LFS behaviour. Key settings include
`enable_autolfs`, `session_artifact_dir`, `size_threshold_mb`, and
`binary_extensions`.

### `.gitattributes`

Generated from the policy file. Lists patterns handled by Git LFS to keep
clones small and prevent accidental binary commits.

### `artifact_manager.py` CLI

Unified command-line interface:

- `--package` – bundle modified files from the temp directory into an
  archive.
- `--commit` – stage and commit the archive using Git LFS.
- `--sync-gitattributes` – regenerate `.gitattributes` from policy.
- `--recover <archive>` – extract a session archive back into the temp
  directory.
- `--tmp-dir <path>` – select a custom temporary directory (defaults to
  `tmp`).

Examples:

```bash
python artifact_manager.py --package
ALLOW_AUTOLFS=1 python artifact_manager.py --package --commit "archive session"
python artifact_manager.py --sync-gitattributes --package
python artifact_manager.py --recover codex-session_<UTC-YYYYmmdd_HHMMSS>.zip
```

Archives live in `codex_sessions/` and are tracked with Git LFS when the
policy file enables `enable_autolfs`.

## 6. Limitations and Recommendations

- Git LFS must be installed locally; otherwise packaging and commit
  steps fail.
- Pointer errors may only appear at `git push`, so always review CI logs
  and test locally before pushing.
- Future improvements could add automated notifications for LFS
  validation failures or scheduled cleanup of old temporary files.

Following this workflow ensures reproducible artifact handling and keeps
large files out of regular git history.

