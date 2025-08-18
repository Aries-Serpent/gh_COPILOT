"""Deploy machine-learning models from a registry and log deployments.

This module fetches models from a registry (e.g., MLflow) using environment
variables to specify the registry URI, model name, version, and optional stage.
Fetched artifacts are stored under ``artifacts/models/<model>/<version>/`` and a
``checksums.json`` file records SHA256 hashes for every artifact. Deployment
results, including success or failure and the artifact hashes, are written to
``analytics.db`` in the ``model_deployments`` table.

Environment variables used:

``MODEL_REGISTRY_URI``: Registry URI or local path.
``MODEL_NAME``:       Name of the model to deploy.
``MODEL_VERSION``:    Version of the model to deploy.
``MODEL_STAGE``:      Optional stage name to fetch instead of version.
``GH_COPILOT_WORKSPACE``: Base workspace path for artifacts and databases.

If MLflow is unavailable, the registry URI is treated as a local filesystem
path. A rollback is performed and logged if the supplied health check fails.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Optional


def _workspace() -> Path:
    """Return the workspace path from ``GH_COPILOT_WORKSPACE`` or cwd."""

    return Path(os.environ.get("GH_COPILOT_WORKSPACE", Path.cwd()))


def _default_db() -> Path:
    """Default location of ``analytics.db`` within the workspace."""

    return _workspace() / "analytics.db"


def _fetch_model(model_name: str, version: str, stage: Optional[str]) -> Path:
    """Fetch a model directory from the registry.

    Attempts to use MLflow if available; otherwise treats the registry URI as a
    local path and returns the model directory.
    """

    registry_uri = os.environ.get("MODEL_REGISTRY_URI")
    if not registry_uri:
        raise RuntimeError("MODEL_REGISTRY_URI not set")

    try:  # pragma: no cover - optional dependency
        import mlflow  # type: ignore

        mlflow.set_tracking_uri(registry_uri)
        spec = stage or version
        model_uri = f"models:/{model_name}/{spec}"
        local_dir = mlflow.artifacts.download_artifacts(model_uri)
        return Path(local_dir)
    except Exception:  # pragma: no cover - fallback path
        source = Path(registry_uri) / model_name / (stage or version)
        if not source.exists():
            raise FileNotFoundError(f"Model not found at {source}")
        return source


def _compute_hashes(directory: Path) -> Dict[str, str]:
    """Compute SHA256 hashes for all files under ``directory``."""

    hashes: Dict[str, str] = {}
    for file in directory.rglob("*"):
        if file.is_file():
            h = hashlib.sha256()
            h.update(file.read_bytes())
            hashes[str(file.relative_to(directory))] = h.hexdigest()
    return hashes


def _log_deployment(
    db_path: Path,
    model_name: str,
    version: str,
    stage: Optional[str],
    status: str,
    artifact_path: Path,
    hashes: Dict[str, str],
) -> None:
    """Persist deployment metadata to ``analytics.db``."""

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS model_deployments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                version TEXT NOT NULL,
                stage TEXT,
                status TEXT NOT NULL,
                artifact_path TEXT NOT NULL,
                artifact_hashes TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            INSERT INTO model_deployments (
                model_name, version, stage, status, artifact_path,
                artifact_hashes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                model_name,
                version,
                stage,
                status,
                str(artifact_path),
                json.dumps(hashes),
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()


def _rollback(artifact_path: Path) -> None:
    """Remove deployed artifacts on failure."""

    if artifact_path.exists():
        shutil.rmtree(artifact_path)


def deploy_model(
    *,
    analytics_db: Optional[Path] = None,
    health_check: Optional[Callable[[Path], bool]] = None,
) -> None:
    """Deploy a model and log the result.

    Parameters
    ----------
    analytics_db:
        Optional path to the analytics database. Defaults to ``analytics.db``
        within the workspace.
    health_check:
        Callable that receives the artifact path and returns ``True`` if the
        deployment is healthy. Defaults to checking that the directory contains
        at least one file.
    """

    model_name = os.environ.get("MODEL_NAME")
    version = os.environ.get("MODEL_VERSION")
    stage = os.environ.get("MODEL_STAGE")

    if not model_name or not version:
        raise RuntimeError("MODEL_NAME and MODEL_VERSION must be set")

    source = _fetch_model(model_name, version, stage)
    dest = _workspace() / "artifacts" / "models" / model_name / version
    if source.is_dir():
        shutil.copytree(source, dest, dirs_exist_ok=True)
    else:
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest / source.name)

    hashes = _compute_hashes(dest)
    (dest / "checksums.json").write_text(json.dumps(hashes, indent=2))

    db_path = analytics_db or _default_db()
    checker = health_check or (lambda p: any(p.iterdir()))

    status = "success"
    if not checker(dest):
        status = "failure"
        _rollback(dest)

    _log_deployment(db_path, model_name, version, stage, status, dest, hashes)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    deploy_model()

