# Git LFS Workflow

This repository uses [Git LFS](https://git-lfs.com/) to manage large or binary files. Follow the steps below when adding or updating binary assets.

## Setup

1. Install Git LFS and local hooks:
   ```bash
   git lfs install
   cp tools/pre-commit-lfs.sh .git/hooks/pre-commit-lfs
   chmod +x .git/hooks/pre-commit-lfs
   cp tools/pre-commit-lfs.sh .git/hooks/pre-push
   chmod +x .git/hooks/pre-push
   ```
   The pre-push hook runs `tools/pre-commit-lfs.sh` and delegates to `git lfs pre-push`.

2. Sync LFS attributes:
   ```bash
   python artifact_manager.py --sync-gitattributes
   git add .gitattributes
   ```

## Verification

- Run the pre-commit hook before committing:
  ```bash
  .git/hooks/pre-commit-lfs
  ```
- The CI job `LFS Policy Check` ensures files ≥50&nbsp;MB or matching extensions in `.codex_lfs_policy.yaml` are tracked via Git LFS.

## Adding Files

1. Track required patterns:
   ```bash
   git lfs track "*.ext"
   python artifact_manager.py --sync-gitattributes
   git add .gitattributes path/to/file.ext
   ```
2. Commit changes:
   ```bash
   git commit -m "feat: add new binary asset"
   ```
