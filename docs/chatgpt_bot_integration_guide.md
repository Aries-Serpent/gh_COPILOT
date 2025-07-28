# ChatGPT Bot Integration Guide

This document explains how to enable the lightweight webhook server and license
management utilities included under `scripts/bot`.

## Environment Variables

- `GITHUB_WEBHOOK_SECRET` – secret token used to verify webhook payloads.
- `GITHUB_TOKEN` – personal access token with the `manage_billing:copilot` scope.
- `GITHUB_ORG` – organization name that owns the Copilot subscription.
- `GH_COPILOT_BACKUP_ROOT` – external path for logs (must be outside the repo).

Set these variables in your shell or `.env` file before starting the tools.

## Webhook Server

Run the Flask server to receive GitHub events:

```bash
python scripts/bot/webhook_server.py
```

The `/webhook` endpoint validates the `X-Hub-Signature-256` header using
`GITHUB_WEBHOOK_SECRET`. Events are logged to
`$GH_COPILOT_BACKUP_ROOT/logs/webhook_*.log` with visual processing indicators.

## Assigning Copilot Seats

Manage seats via the GitHub REST API:

```bash
python scripts/bot/assign_copilot_license.py <username>
```

Pass `--revoke` to remove a seat. The script logs progress and uses the Dual
Copilot validator for compliance.

## Testing the Integration

Use the helper script to simulate events and API calls without touching the
real GitHub endpoints:

```bash
python scripts/bot/test_integration.py
```

This runs an in-memory webhook request and mocks the GitHub API so you can
verify end-to-end behavior.
