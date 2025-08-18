# Staging Deployment Guide

This directory contains configuration and helper scripts for launching a staging
environment.

## Container and Orchestration Configurations

The `deployment` directory now includes baseline configuration for running the
application with Nginx, Gunicorn, Docker Compose, and Kubernetes:

- `nginx_config.conf` – reverse proxy configuration for Nginx.
- `gunicorn_config.py` – basic Gunicorn settings.
- `docker_compose.yml` – Compose file wiring the application and Nginx.
- `k8s/deployment.yaml` – Kubernetes Deployment definition.
- `k8s/service.yaml` – Kubernetes Service exposing the pod.
- `k8s/ingress.yaml` – Kubernetes Ingress routing external traffic.

### Key Configuration Parameters

| File | Parameter | Description |
| ---- | --------- | ----------- |
| `nginx_config.conf` | `listen` | Port Nginx listens on for HTTP traffic |
|  | `proxy_pass` | Upstream URL for forwarding requests |
| `gunicorn_config.py` | `bind` | Socket and port Gunicorn exposes |
|  | `workers` | Number of worker processes |
|  | `timeout` | Seconds before a worker is restarted |
| `docker_compose.yml` | `volumes` | Host paths mounted inside containers |
|  | `ports` | Host:container port mappings |
|  | `environment` | Container environment variables |
| `k8s/deployment.yaml` | `replicas` | Number of pod instances |
|  | `image` | Container image to deploy |
|  | `env` | Environment variables for the pod |
| `k8s/service.yaml` | `port/targetPort` | Map service port to container port |
|  | `type` | Service exposure strategy |
| `k8s/ingress.yaml` | `path` | URL prefix routed to the service |

## Prerequisites

1. Activate the project virtual environment:
   ```bash
   source .venv/bin/activate
   ```
2. Export the workspace path so helper utilities can locate `production.db`:
   ```bash
   export GH_COPILOT_WORKSPACE=/workspace/gh_COPILOT
   ```

## Staging Deployment

Run the staging deployment utility:

```bash
python -m scripts.deployment.ENHANCED_ML_STAGING_DEPLOYMENT_MISSION_COMPLETE \
  >/tmp/gh_copilot_backups/staging.log 2>&1
```

The script attempts to copy a random template from `databases/production.db`
into `generated_scripts/`. On non-Windows systems, update the script's
`workspace_path` to your local path; otherwise it logs:
`[ERROR] Generation failed: unable to open database file`.

For an additional validation step, run the deployment validator:

```bash
python -m scripts.deployment.comprehensive_deployment_validator \
  >/tmp/gh_copilot_backups/deploy.log 2>&1
```

## Post-Deployment Testing

After deployment, run the full test suite:

```bash
pytest
```

Logs from deployment attempts are stored under `/tmp/gh_copilot_backups/`.

## Production Deployment

Use `deployment/scripts/deploy_to_production.py` to deploy the web GUI to the
production environment. The script supports a `--dry-run` flag which prints the
deployment plan without applying any changes. Concurrent executions are guarded
by a lockfile to prevent conflicting deployments, and each run logs events to
`analytics.db`'s `deployment_events` table.

Example dry run:

```bash
python -m deployment.scripts.deploy_to_production --dry-run
```

