# Updated Codex Environment Custom Instructions (gh_COPILOT)

These guidelines reflect the current repository state and supersede previous custom instructions.

---

## 1. Scope & Setup

| Step | Instruction |
|------|-------------|
| **Environment** | 1. Run `./setup.sh` to create the Python (3.8+) virtualenv and install project dependencies.<br>2. Set environment variables:<br>  • `GH_COPILOT_WORKSPACE` = repository root<br>  • `ALLOW_AUTOLFS=1`<br>  • `GH_COPILOT_BACKUP_ROOT` pointing **outside** the repo (for logs/backups)<br>  • `CLW_MAX_LINE_LENGTH=1550` (for safe output) |
| **clw Utility** | Ensure `/usr/local/bin/clw` exists and is executable. If missing, copy `tools/clw.py` there and `chmod +x`. Use `clw` for any command that may produce long lines. |
| **Safe Searching** | Use `./tools/safe_rg.sh "<pattern>"` for repository searches; avoid `grep -R`/`ls -R`. |
| **Workspace Scope** | Only modify files within the designated directories for the task. |
| **Backup** | Store all backups/logs under `$GH_COPILOT_BACKUP_ROOT`, never inside the repo tree. |

---

## 2. Tooling & Git LFS

| Step | Instruction |
|------|-------------|
| **Commands** | Non‑interactive shell tools only (`git`, `rg`, `sed`, `jq`, etc.); no network calls or daemons. |
| **Pre‑commit LFS Hook** | Install and run `tools/pre-commit-lfs.sh` as `.git/hooks/pre-commit-lfs` before committing (`chmod +x` after copying). |
| **Binary Handling** | For files ≥50 MB or with extensions defined in `.codex_lfs_policy.yaml`, ensure Git LFS tracking:<br>  1. `git lfs install`<br>  2. `git lfs track "*.<ext>"`<br>  3. `python artifact_manager.py --sync-gitattributes`<br>  4. `git add .gitattributes` and re‑stage files |
| **Verification** | Validate with `git lfs status` or `git lfs ls-files`. Abort and report if `ALLOW_AUTOLFS` is unset. |
| **Output Handling** | For potentially large output, pipe through `clw` or redirect to a log file and inspect in chunks (`head`, `tail`). |
| **LFS Hygiene** | 1. Run `git lfs fetch --all && git lfs checkout || true && git lfs fsck` in a clean clone.<br>2. Ensure `git status --short` is empty.<br>3. Append LFS ignore rules for `.gitkeep`, `.keep`, `.placeholder`.<br>4. If missing objects: run `git lfs push --all origin` from a clone with payloads, then re‑hydrate. |

---

## 3. Code & PR Standards

| Area | Instruction |
|------|-------------|
| **Commits/PRs** | Use Conventional Commit prefixes (e.g., `feat:`, `fix:`). Each commit must be focused and descriptive. |
| **Documentation** | Update relevant docs (`README.md`, `AGENTS.md`, etc.) and in‑code comments when changing behavior or adding features. |
| **Testing** | Run `ruff` and `pytest` for all affected areas. Add/adjust tests for new features or bugfixes. Ensure all tests and linters pass. |
| **Session Wrap‑Up** | After completing work, run `scripts/wlc_session_manager.py` to log the session and perform integrity checks. |

---

## 4. Core Protocols

| Protocol | Application |
|----------|-------------|
| **Dual Copilot** | For critical operations, perform a secondary validation step using `secondary_copilot_validator.py` or equivalent review process. |
| **Database‑First** | Consult `production.db` (or relevant database) before editing files; databases must remain < 99.9 MB. |
| **Anti‑recursion & Backup** | Validate paths to ensure backups/logs reside outside the workspace. Never copy the repo recursively. |
| **Session Integrity** | Begin and end sessions with checks for zero‑byte files and overall process completion. |
| **Visual Indicators** | Long‑running scripts should provide progress bars or timestamps for transparency. |

---

## 5. Policy & Configuration

- `.codex_lfs_policy.yaml` defines LFS thresholds, binary extensions, and the `.gitattributes` template.  
- Keep `.gitattributes` synchronized with policy changes (`python artifact_manager.py --sync-gitattributes`).  
- All edits must comply with this policy and stay within the designated scope.

---

## 6. LFS Recovery & Ref‑Scoped Migration

- Only rewrite `main` and necessary `release/*` branches when migrating LFS for archives.  
- Preconditions: clean working tree, `git lfs fsck` passes after fetch/checkout.  
- Preview impact: `git lfs migrate info --include="<patterns>" <branch>`.  
- Rewrite and verify, then force‑push updated branches with team coordination.

---

## 7. CI/CD Invariants

- Hydrate LFS in CI with `actions/checkout@v4` and `lfs: true`.  
- Use a diff‑aware guard job to enforce LFS tracking for new/changed binary files in PRs.

---

**Adherence to these instructions is mandatory for contributions to the gh_COPILOT repository.**
