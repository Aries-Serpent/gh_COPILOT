# ChatGPT Codex Environment Configuration

This guide explains how to configure environment variables for the gh_COPILOT toolkit.

## Required Variables

- `GH_COPILOT_WORKSPACE`: Absolute path to the repository workspace. Used by tests and scripts to locate databases and configuration files. If unset, tools default to the current working directory.
- `GH_COPILOT_BACKUP_ROOT`: External directory for backups. Must not reside inside the workspace. Defaults to `E:/temp/gh_COPILOT_Backups` on Windows or `/tmp/<user>/gh_COPILOT_Backups` on Linux.

Set these variables by editing the provided `.env` file:

```bash
# Example .env
GH_COPILOT_WORKSPACE=/path/to/workspace
GH_COPILOT_BACKUP_ROOT=/external/backup/location
```

Load the variables in your shell before running tasks:

```bash
source .env
```

All unit tests (`make test`) and scripts rely on these variables for path validation and anti-recursion compliance.

## Line-Wrapping Utility

Install the `clw` line wrapper to prevent terminal overflow during long command output. Copy the script and verify it exists:

```bash
cp tools/clw.py /usr/local/bin/clw
chmod +x /usr/local/bin/clw
ls -l /usr/local/bin/clw
```

## Archival Databases
`archive.db` and `staging.db` are no longer included by default. They have been moved to `archived_databases/` and are also available in the project's GitHub releases. Download them if legacy analysis is required and place them under the `archived_databases/` directory.
