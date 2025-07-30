# Deployment Orchestrator

The `UnifiedDeploymentOrchestrator` coordinates multiple enterprise systems
such as the file manager, backup manager and monitoring engine. It wraps
execution with the dual-copilot pattern to ensure independent validation.

Run the orchestrator via the CLI module:
```bash
python scripts/orchestration/UNIFIED_DEPLOYMENT_ORCHESTRATOR_CONSOLIDATED.py --start
```
This command starts a managed session with `ComprehensiveWorkspaceManager` and
executes the deployment workflow.

## Docker Deployment

The orchestrator can run inside the provided Docker image. Build and tag the
image from the repository root:

```bash
docker build -t gh_copilot:latest .
```

Run the container while mapping the backup directory on the host. Two
environment variables are required at startup:

* **`GH_COPILOT_WORKSPACE`** – workspace path inside the container. Defaults to
  `/app`.
* **`GH_COPILOT_BACKUP_ROOT`** – external path for logs and backups. Must map to
  a host directory.

Example run command:

```bash
docker run \
  -e GH_COPILOT_BACKUP_ROOT=/path/to/backups \
  -e GH_COPILOT_WORKSPACE=/app \
  gh_copilot:latest
```

The CI workflow `.github/workflows/ci.yml` builds this image as part of the
automated tests.
