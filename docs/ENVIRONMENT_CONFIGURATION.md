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
