# ChatGPT Codex Environment Configuration

This guide explains how to configure environment variables for the gh_COPILOT toolkit.

## Required Variables

- `GH_COPILOT_WORKSPACE`: Absolute path to the repository workspace. Used by tests and scripts to locate databases and configuration files. If unset, tools default to the current working directory.
- `GH_COPILOT_BACKUP_ROOT`: External directory for backups. **This variable is required.** Set it to a folder outside the workspace before running `setup.sh`.

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

### Docker and CI Variables

The container entrypoint reads several additional variables:

- `FLASK_SECRET_KEY` – secret key for the Flask dashboard. Required when running the Docker image or deploying in CI.
- `FLASK_RUN_PORT` – port for the dashboard service (default `5000`).
- `API_SECRET_KEY` – token used by automated scripts and CI jobs.
- `CI` – set to `true` in CI environments to disable progress bars and interactive prompts.

Define these in `.env` or pass them via your CI configuration so Docker containers and automated tests use consistent settings.

## Security Configuration

Security policies are stored in the repository under the `security/` directory:

- `security/enterprise_security_policy.json` – high-level enterprise requirements.
- `security/access_control_matrix.json` – role-based access definitions.
- `security/encryption_standards.json` – approved cryptographic algorithms and key management practices.
- `security/security_audit_framework.json` – audit categories, compliance checks, and incident response procedures.

Refer to these files when updating or validating security protocols.

## Line-Wrapping Utility

Install the `clw` line wrapper to prevent terminal overflow during long command output. Use the helper installer and verify it exists:

```bash
tools/install_clw.sh
ls -l /usr/local/bin/clw
```

PyYAML>=6.0 is required for `artifact_manager.py` to read `.codex_lfs_policy.yaml`; ensure the package is installed in your environment.

## Archival Databases
`archive.db` and `staging.db` are no longer included by default. They have been moved to `archived_databases/` and are also available in the project's GitHub releases. Download them if legacy analysis is required and place them under the `archived_databases/` directory.

## Enterprise Configuration

Workspace policies are defined in `config/enterprise.json`. The file currently specifies path patterns that compliance checks remove or block:

```json
{
  "forbidden_paths": ["*temp*"]
}
```

Set `CONFIG_PATH` to load a custom configuration file.
