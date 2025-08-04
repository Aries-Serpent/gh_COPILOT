"""Web GUI integration layer for the enterprise dashboard."""

from __future__ import annotations

import logging
import os
from functools import wraps
from pathlib import Path
from typing import Callable, Iterable

import json
from flask import Flask, Response, jsonify, request

from .database_web_connector import DatabaseWebConnector
from .template_intelligence_engine import TemplateIntelligenceEngine

__all__ = ["WebGUIIntegrator", "requires_role"]


def requires_role(role: str) -> Callable[[Callable], Callable]:
    """Simple role-based access decorator."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if os.getenv("ENTERPRISE_AUTH_DISABLED") == "1":
                return func(*args, **kwargs)
            user_role = request.headers.get("X-Role")
            if user_role != role:
                logging.getLogger(__name__).warning("Access denied for role %s to %s", user_role, request.path)
                return jsonify({"error": "forbidden"}), 403
            return func(*args, **kwargs)

        return wrapper

    return decorator


class WebGUIIntegrator:
    """Integrate Flask dashboard with production database."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        self.db_connector = DatabaseWebConnector(self.db_path)
        self.template_engine = TemplateIntelligenceEngine(Path("web_gui/templates"))

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------
    def register_endpoints(self, app: Flask) -> None:
        """Register enterprise dashboard routes."""

        if str(self.template_engine.template_dir) not in app.jinja_loader.searchpath:
            app.jinja_loader.searchpath.append(str(self.template_engine.template_dir))

        @app.get("/")
        @requires_role("admin")
        def dashboard() -> str:
            metrics = self.db_connector.fetch_enterprise_metrics()
            return self.template_engine.render_intelligent_template(
                "dashboard.html", {"title": "Dashboard", "metrics": metrics}
            )

        @app.get("/database")
        @requires_role("admin")
        def database_view() -> str:
            metrics = self.db_connector.fetch_enterprise_metrics()
            return self.template_engine.render_intelligent_template(
                "database.html", {"title": "Database", "metrics": metrics}
            )

        @app.get("/backup")
        @requires_role("admin")
        def backup_view() -> str:
            metrics = self.db_connector.fetch_enterprise_metrics()
            return self.template_engine.render_intelligent_template(
                "backup_restore.html", {"title": "Backup", "metrics": metrics}
            )

        @app.get("/migration")
        @requires_role("admin")
        def migration_view() -> str:
            metrics = self.db_connector.fetch_enterprise_metrics()
            return self.template_engine.render_intelligent_template(
                "migration.html", {"title": "Migration", "metrics": metrics}
            )

        @app.get("/deployment")
        @requires_role("admin")
        def deployment_view() -> str:
            metrics = self.db_connector.fetch_enterprise_metrics()
            return self.template_engine.render_intelligent_template(
                "deployment.html", {"title": "Deployment", "metrics": metrics}
            )

        @app.get("/api/scripts")
        @requires_role("admin")
        def api_scripts() -> Iterable[dict]:
            data = self.db_connector.fetch_recent_scripts()
            self.logger.info("Scripts API served")
            return jsonify(data)

        @app.get("/api/health")
        def api_health() -> dict:
            self.logger.info("Health check served")
            return jsonify({"status": "ok"})

        @app.get("/api/compliance")
        @requires_role("admin")
        def api_compliance() -> dict:
            data = self.db_connector.fetch_compliance_summary()
            self.logger.info("Compliance summary served")
            return jsonify(data)

        @app.get("/api/rollbacks")
        @requires_role("admin")
        def api_rollbacks() -> Iterable[dict]:
            data = self.db_connector.fetch_rollback_logs()
            self.logger.info("Rollback logs served")
            return jsonify(data)

        @app.get("/api/corrections")
        @requires_role("admin")
        def api_corrections() -> Iterable[dict]:
            data = self.db_connector.fetch_correction_history()
            self.logger.info("Correction history served")
            return jsonify(data)

        @app.get("/api/compliance_stream")
        def api_compliance_stream() -> Response:
            from dashboard.compliance_metrics_updater import ComplianceMetricsUpdater

            once = request.args.get("once") == "1"
            updater = ComplianceMetricsUpdater(Path("dashboard/compliance"), test_mode=True)

            def generate() -> Iterable[str]:
                for metrics in updater.stream_metrics(interval=1, iterations=1 if once else None):
                    yield f"data: {json.dumps(metrics)}\n\n"

            return Response(generate(), mimetype="text/event-stream")

        @app.post("/api/ingest")
        @requires_role("admin")
        def api_ingest() -> dict:
            payload = request.get_json(silent=True) or {}
            self.logger.info("Ingestion requested: %s", payload)
            return jsonify({"status": "accepted"})

        @app.post("/api/rollback")
        @requires_role("admin")
        def api_rollback_action() -> dict:
            payload = request.get_json(silent=True) or {}
            self.logger.info("Rollback requested: %s", payload)
            return jsonify({"status": "accepted"})

        @app.post("/api/backup")
        @requires_role("admin")
        def api_backup_action() -> dict:
            payload = request.get_json(silent=True) or {}
            self.logger.info("Backup requested: %s", payload)
            return jsonify({"status": "accepted"})

        self.logger.info("Registered web GUI endpoints")

    def initialize(self) -> None:
        """Initialize the integration with Flask dashboard."""
        self.logger.info("Initialized Web GUI integrator with %s", self.db_path)
