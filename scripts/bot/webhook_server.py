#!/usr/bin/env python3
"""Minimal GitHub webhook server with HMAC validation."""
# pyright: reportMissingImports=false

from __future__ import annotations

import hmac
import hashlib
import logging
import os
from datetime import datetime
from flask import Flask, request
from tqdm import tqdm

from utils.cross_platform_paths import (
    CrossPlatformPathManager,
    verify_environment_variables,
)

TEXT_INDICATORS = {
    "start": "[START]",
    "progress": "[PROGRESS]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
}


def create_app() -> Flask:
    """Create configured Flask app."""
    verify_environment_variables()
    app = Flask(__name__)
    secret = os.environ.get("GITHUB_WEBHOOK_SECRET", "")

    backup_root = CrossPlatformPathManager.get_backup_root()
    log_dir = backup_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"webhook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    @app.route("/webhook", methods=["POST"])
    def webhook() -> tuple[dict[str, str], int]:
        start_time = datetime.now()
        logger.info("%s Webhook received", TEXT_INDICATORS["start"])
        signature = request.headers.get("X-Hub-Signature-256", "")
        payload = request.get_data()
        expected = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            logger.error("%s Invalid signature", TEXT_INDICATORS["error"])
            return {"status": "invalid signature"}, 400

        event = request.headers.get("X-GitHub-Event", "ping")
        with tqdm(total=1, desc=f"{TEXT_INDICATORS['progress']} {event}", unit="evt") as bar:
            logger.info("Event: %s", event)
            bar.update(1)

        duration = (datetime.now() - start_time).total_seconds()
        logger.info("%s Webhook processed in %.2fs", TEXT_INDICATORS["success"], duration)
        return {"status": "ok"}, 200

    return app


if __name__ == "__main__":
    PORT = int(os.getenv("FLASK_RUN_PORT", "5000"))
    app = create_app()
    app.run(host="0.0.0.0", port=PORT)
