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
2. **Packaging Artifacts**: Run `python artifact_manager.py` to detect new files in the temp directory and create a timed archive. If the archive meets LFS criteria, it is automatically tracked and committed using Git LFS.
3. **Adding Files**: Files matching the configured extensions or exceeding the size threshold are automatically tracked via Git LFS. Check with `git lfs status` before committing.
4. **Recovering Artifacts**: To unpack the most recent archive after a fresh clone or CI reset, run `python artifact_manager.py --recover`.
5. **Committing**: The packaging step commits the archive for you. Ensure CI runs succeed by verifying `git lfs ls-files` lists the new archive.

Following this workflow ensures consistent handling of binary data and prevents accidental commits of large files outside Git LFS.

## Artifact Manager CLI

The `artifact_manager.py` utility now includes a small command-line interface:

- `--package` – bundle modified files from `tmp/` into a zip archive.
- `--commit` – after packaging, stage and commit the archive using Git LFS.
- `--sync-gitattributes` – regenerate `.gitattributes` from `.codex_lfs_policy.yaml` before other operations.
- `--recover <archive>` – extract a session archive back into `tmp/`.

Example usage:

```bash
python artifact_manager.py --package
ALLOW_AUTOLFS=1 python artifact_manager.py --package --commit "archive session"
python artifact_manager.py --sync-gitattributes --package
python artifact_manager.py --recover codex-session_<UTC-YYYYmmdd_HHMMSS>.zip
```

Archives are stored in `codex_sessions/` and tracked with Git LFS when configured via `.codex_lfs_policy.yaml`.
## GitHub Actions Workflow

The `.github/workflows/artifact_lfs.yml` workflow packages and commits session artifacts automatically after successful tests:

```yaml
      - name: Package session artifacts
        run: ALLOW_AUTOLFS=1 python artifact_manager.py --package --commit
```

This workflow runs packaging with `--commit` so new session archives are automatically tracked and committed. Nightly runs can also call `--recover` to verify archived files remain valid.

## Troubleshooting

- **Git LFS not found** – run `git lfs install` and verify `git lfs status`.
- **Permission errors** – ensure `codex_sessions/` is writable and you have commit rights.
- **Archive not tracked** – set `ALLOW_AUTOLFS=1` or manually update `.gitattributes`.
