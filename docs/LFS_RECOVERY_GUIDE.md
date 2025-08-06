# Git LFS Recovery Guide

If Git LFS objects become corrupted or missing, use `tools/lfs_repair.sh`
to rebuild the local cache and verify integrity.

```bash
# from repository root
export GH_COPILOT_BACKUP_ROOT=/path/to/external/backups
tools/lfs_repair.sh
```

The script performs the following steps:

1. Removes the local `.git/lfs/objects` cache.
2. Runs `git lfs fetch --all` to download objects from the remote.
3. Checks out files with `git checkout` and `git lfs checkout`.
4. Validates the result using `git lfs fsck`.

Logs are written to `$GH_COPILOT_BACKUP_ROOT/logs/lfs_repair.log` for audit
and disaster recovery purposes.

