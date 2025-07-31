# Artifact Recovery Workflow

This document describes how the repository manages large binary artifacts using Git LFS and how to recover artifacts from prior sessions.

## Purpose of `.codex_lfs_policy.yaml`

The `.codex_lfs_policy.yaml` file defines the automatic Git LFS configuration used by the Codex environment. It enables automatic tracking of large or binary files and specifies which file types must always use LFS.

Key settings include:

- `enable_autolfs`: ensures automatic LFS setup.
- `session_artifact_dir`: directory where session artifacts are stored.
- `size_threshold_mb`: files larger than this threshold trigger LFS tracking.
- `binary_extensions`: list of extensions that should always be tracked via LFS.

## Purpose of `.gitattributes`

The `.gitattributes` file explicitly lists patterns that Git LFS should manage. These rules prevent large files from bloating the normal Git history and keep repository clones lightweight. The patterns are generated from the policy file and include rules for each binary extension and the session archives directory.

## Workflow

1. **Initial Clone**: When cloning the repository, run `git lfs install` to ensure LFS support is active.
2. **Packaging Artifacts**: Run `python artifact_manager.py` to detect new files in the temp directory and create a timestamped archive. If the archive meets LFS criteria, it is automatically tracked and committed.
3. **Adding Files**: Files matching the configured extensions or exceeding the size threshold are automatically tracked via Git LFS. Check with `git lfs status` before committing.
4. **Recovering Artifacts**: To unpack the most recent archive after a fresh clone or CI reset, run `python artifact_manager.py --recover`.
5. **Committing**: The packaging step commits the archive for you. Ensure CI runs succeed by verifying `git lfs ls-files` lists the new archive.

Following this workflow ensures consistent handling of binary data and prevents accidental commits of large files outside Git LFS. Integrate the packaging command into CI so that session artifacts are preserved automatically.
