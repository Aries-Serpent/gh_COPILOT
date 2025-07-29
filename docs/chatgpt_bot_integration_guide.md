# ChatGPT Bot Integration Guide

This guide explains how to run the optional GitHub bot components used in enterprise deployments.

## Setup
1. Run `bash setup.sh` and activate the virtual environment:
   ```bash
   bash setup.sh
   source .venv/bin/activate
   ```
2. Ensure `/usr/local/bin/clw` is installed. If missing, copy `tools/clw.py` and make it executable:
   ```bash
   cp tools/clw.py /usr/local/bin/clw
   chmod +x /usr/local/bin/clw
   ```

## Environment Variables
Set the following variables before starting the services:
- `GH_COPILOT_WORKSPACE` – absolute path to the repository root.
- `GH_COPILOT_BACKUP_ROOT` – directory outside the workspace for logs and backups.
- `GITHUB_ORG` – name of your GitHub organization used for license management.
- `GITHUB_TOKEN` – token with access to your organization.
- `GITHUB_WEBHOOK_SECRET` – shared secret for validating incoming GitHub webhooks.

Export them manually or place them in a `.env` file and `source` it.

## Example Commands
### Start the Webhook Server
```bash
python scripts/bot/webhook_server.py
```
The server listens for GitHub events and triggers automation workflows.

### Assign Copilot Licenses
```bash
python scripts/bot/assign_copilot_license.py chatgpt-bot
```
Use this script to grant GitHub Copilot licenses to new team members. The target
organization is read from `GITHUB_ORG`.

Both scripts log activity under `$GH_COPILOT_BACKUP_ROOT/logs` and record events in `production.db`.

## Testing & Validation
Run the integration checks after configuration to ensure both components work:
```bash
python scripts/bot/test_integration.py
```
