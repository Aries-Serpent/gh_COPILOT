#!/usr/bin/env bash
set -e
python scripts/docker_entrypoint.py &
python dashboard/compliance_metrics_updater.py &
wait -n
