# Git Safe Add Commit Utilities

This repository includes helper wrappers for committing large or binary files using Git LFS.

## Python Utility

`tools/git_safe_add_commit.py` scans staged files and ensures binary or large files are tracked with Git LFS. If `ALLOW_AUTOLFS=1` is set, it automatically installs Git LFS, updates `.gitattributes`, re-stages the file, and commits.

Usage:

```bash
ALLOW_AUTOLFS=1 python tools/git_safe_add_commit.py "commit message" [--push]
```

## Bash Fallback

`tools/git_safe_add_commit.sh` provides similar functionality for environments without Python. Enable auto LFS by exporting `ALLOW_AUTOLFS=1`.

```bash
export ALLOW_AUTOLFS=1
bash tools/git_safe_add_commit.sh "commit message" --push
```

## Policy File

`.codex_lfs_policy.yaml` defines the size threshold and default LFS patterns. The wrappers read this file when available to determine which extensions to track.

## Integration

Include these wrappers in your workflow to prevent accidental commits of large binaries. See the example workflow in `README.md` for invocation patterns.
