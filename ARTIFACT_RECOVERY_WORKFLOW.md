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

The `.gitattributes` file explicitly lists patterns that Git LFS should manage. These rules prevent large files from bloating the normal Git history and keep repository clones lightweight.

## Workflow

1. **Initial Clone**: When cloning the repository, run `git lfs install` to ensure LFS support is active.
2. **Creating Artifacts**: Place generated artifacts inside the directory defined by `session_artifact_dir` (`codex_sessions/`).
3. **Adding Files**: When you add files that match the configured extensions or exceed the size threshold, Git LFS automatically tracks them. Verify with `git lfs status` before committing.
4. **Committing**: Commit your changes as usual. The large files are stored in LFS, keeping repository history small.
5. **Recovering Artifacts**: To fetch artifacts from previous sessions, run `git lfs pull`. This downloads the referenced binary objects into your working tree.

Following this workflow ensures consistent handling of binary data and prevents accidental commits of large files outside Git LFS.

## Using `artifact_manager.py`

The `artifact_manager.py` utility streamlines packaging and recovery:

```bash
python artifact_manager.py --package               # create archive
python artifact_manager.py --package --commit \
    --message "Add session artifact"               # archive and commit
python artifact_manager.py --recover               # restore latest archive
```

Archives are stored in `codex_sessions/` and tracked with Git LFS when
configured via `.codex_lfs_policy.yaml`.
