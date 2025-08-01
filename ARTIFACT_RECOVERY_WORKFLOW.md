# Artifact Recovery Workflow

This guide explains how the repository packages, commits, and restores
session artifacts while keeping large binary files under Git LFS. It is
intended for contributors and CI jobs running in the Codex environment.

## 1. Continuous Integration Overview

All automation uses `.github/workflows/artifact_lfs.yml` to manage
artifacts. Centralising on a single workflow avoids per-branch
divergence and ensures every run applies the same rules. The workflow
packages, syncs, and commits artifacts in a single atomic sequence:

1. **Checkout and setup** – the job fetches the repository with LFS
   pointers, installs Git LFS, and runs `setup.sh`.
2. **Package and commit** – `python artifact_manager.py --package --commit
   --sync-gitattributes [--tmp-dir <path>]` bundles files from the
   temporary directory, stages the archive, regenerates `.gitattributes`,
   and records the commit. `artifact_lfs.yml` runs this command so that
   packaging, pointer conversion, and committing happen as one atomic
   action. A custom `--tmp-dir` overrides the policy’s
   `session_artifact_dir`, allowing CI jobs to isolate artifacts without
   changing repository defaults.
3. **Pointer verification** – the subsequent *Verify LFS pointers* step
   enumerates `binary_extensions` from `.codex_lfs_policy.yaml` and fails
   the job if any files skip Git LFS.
4. **Push** – changes are pushed only after verification succeeds,
   guaranteeing that packaging, pointer conversion, and commit occur
   together.

## 2. Key CI Workflow Step: Artifact Packaging, Commit, and Sync

Every job that produces artifacts should include:

```yaml
- name: Package, Commit, and Sync Artifacts
  run: python artifact_manager.py --package --commit --sync-gitattributes [--tmp-dir <path>]
```

This single step bundles new files from the temporary directory (or the
directory provided via `--tmp-dir`), commits the resulting archive, and
updates `.gitattributes` so newly introduced binary types are tracked
automatically in accordance with `.codex_lfs_policy.yaml`.

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
- If the *Verify LFS pointers* step fails in CI, review
  `.codex_lfs_policy.yaml` and rerun `artifact_manager.py --sync-gitattributes`
  before recommitting.
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

## CI Integration and Best Practices

The following guidelines ensure artifact packaging and Git LFS automation run
reliably in continuous integration environments.

### 1. Continuous Integration Overview

Standardize on a single workflow, `.github/workflows/artifact_lfs.yml`, to
manage large files and session artifacts. Consistent automation prevents manual
mistakes and keeps every contributor working with the same expectations.

### 2. Key CI Step: Package, Commit, and Sync

Include a job step that runs `python artifact_manager.py --package --commit
--sync-gitattributes`. The workflow defined in `artifact_lfs.yml` executes this
command so that packaging, pointer conversion, and committing occur in a single
transaction. A minimal workflow showing these steps alongside pointer validation looks like:

```yaml
# .github/workflows/artifact_lfs.yml
jobs:
  manage-artifacts:
    steps:
      - uses: actions/checkout@v4
        with:
          lfs: true
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Package, Commit, and Sync Artifacts
        run: python artifact_manager.py --package --commit --sync-gitattributes [--tmp-dir <path>]
      - name: Verify LFS pointers
        run: |
          set -e
          exts='.db .7z .zip .bak .dot .sqlite .exe'
          missing=''
          for ext in $exts; do
            for f in $(git ls-files "*$ext"); do
              if ! git lfs ls-files "$f" >/dev/null 2>&1; then
                missing="$missing $f"
              fi
            done
          done
          if [ -n "$missing" ]; then
            echo "These files are not tracked by Git LFS:$missing" >&2
            exit 1
          fi
          git lfs ls-files | tee lfs_files.log
      - name: Validate session archives
        run: |
          set -e
          # Ensure session archives exist and have LFS pointers (see ARTIFACT_RECOVERY_WORKFLOW.md)
          while read -r oid marker path; do
            if [ "$marker" != "*" ]; then
              echo "Pointer missing for $path" >&2
              exit 1
            fi
            if [ ! -f "$path" ]; then
              echo "Missing session archive: $path" >&2
              exit 1
            fi
          done < lfs_files.log
      - name: Push changes
        run: git push
```

Running `artifact_manager.py` with `--package --commit --sync-gitattributes` ensures the archive is created, LFS pointers are generated, and the commit is recorded before the validation step runs. The subsequent *Validate session archives* step parses the `git lfs ls-files` output to confirm every session archive exists and carries a proper pointer. This atomic sequence prevents raw binary blobs from ever entering history and catches mis-tracked files before they can break subsequent pushes or pulls.

### 3. Pointer Validation Step

After committing, the workflow runs `git lfs ls-files --strict` to verify that
all tracked extensions resolve to LFS pointers. A failing run might emit:

```
Error: these files should be pointers but are not:
  artifacts/report.csv
```

To fix this, add the file type to `.codex_lfs_policy.yaml`, run
`artifact_manager.py --sync-gitattributes`, and recommit.

### 4. Why This Approach Works

Bundling packaging, pointer updates, and committing in one step eliminates
missed artifacts, ensures `.gitattributes` stays current, and reduces LFS
misconfiguration errors that commonly break CI/CD pipelines.

### 5. Troubleshooting & Verification

When failures occur, review `git lfs ls-files` output and artifact manager logs
in CI to identify mis-tracked binaries or permission problems. Pointer
validation errors often mean the file's extension is missing from
`.codex_lfs_policy.yaml` or that a custom `--tmp-dir` bypassed the policy's
`session_artifact_dir`. Update the policy or rerun `artifact_manager.py --sync-gitattributes [--tmp-dir <path>]` before recommitting.
Test workflow changes in branches before merging to catch platform-specific
issues.

### 6. Configuration Files & CLI Options

Keep `.codex_lfs_policy.yaml` up to date. Its `session_artifact_dir` defines the
default temporary path; passing `--tmp-dir` overrides it for a job run and can
isolate artifacts to ephemeral storage. The policy’s `binary_extensions`
control which files the pointer validation step checks, so CI runs should
update the policy before changing `--tmp-dir` locations.

### 7. Limitations and Future Improvements

Some LFS or commit errors appear only at `git push`, and all contributors must
have Git LFS installed. Future work could add notifications for pointer
validation failures, scheduled cleanup of old temp files, and additional
documentation on artifact recovery during session iterations.


Example usage:

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

