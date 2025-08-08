#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT=${1:-staging}
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"${ROOT_DIR}/deploy/dashboard/deploy.sh" "${ENVIRONMENT}"
