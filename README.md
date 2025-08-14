# gh_COPILOT

This repository uses Git LFS for large files. In cases where LFS pointers or objects become corrupt, run the full repair script:

```bash
scripts/lfs_full_repair.sh
```

> **Warning**
> The repair script rewrites Git history and force pushes all branches and tags. Coordinate with the team before running it and ensure that a backup is created. After the migration finishes you **must** force push the updated refs to the remote.
