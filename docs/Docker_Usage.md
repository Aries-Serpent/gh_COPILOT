# Docker Usage

This guide explains how to build and run the gh_COPILOT Docker image and describes the environment variables and port mappings used by the container.

## Building the Image

From the repository root run:

```bash
docker build -t gh_copilot .
```

## Running the Container

When starting the container you must supply several environment variables and map the backup volume to the host. Example:

```bash
docker run -p 5000:5000 \
  -e GH_COPILOT_WORKSPACE=/app \
  -e GH_COPILOT_BACKUP_ROOT=/path/to/backups \
  -e FLASK_SECRET_KEY=<generated_secret> \
  gh_copilot
```

The `docker-compose.yml` file exposes additional services and ports. By default the dashboard listens on `FLASK_RUN_PORT` (5000). The compose file maps ports `5000`-`5006` and `8080` from the container to the host.

## Environment Variables

| Variable | Purpose |
| --- | --- |
| `GH_COPILOT_WORKSPACE` | Path to the workspace inside the container (usually `/app`). |
| `GH_COPILOT_BACKUP_ROOT` | Host directory mounted at `/backup` where logs and databases persist. |
| `FLASK_SECRET_KEY` | Secret key required by the Flask dashboard. |
| `FLASK_RUN_PORT` | Port exposed by the dashboard (default `5000`). |
| `API_SECRET_KEY` | Token used by automation scripts. Optional but recommended. |

Set these variables in `.env` or pass them via `docker run -e`.

## Entrypoint Details

The container uses `entrypoint.sh` to initialise the `enterprise_assets.db` database if it does not exist. The script then launches two background services: `dashboard/compliance_metrics_updater.py` and `scripts/code_placeholder_audit.py`. Finally it `exec`s the command provided as `CMD` so the main service (typically the dashboard) starts with the workers running.

`docker_wrapper.sh` performs similar validation but invokes `scripts/docker_entrypoint.py` before starting the same background workers. It waits for those processes so that containerised CI jobs can run initialization logic and exit cleanly.

