#!/usr/bin/env python3
"""Integration test utilities for the bot scripts."""

from __future__ import annotations

import hmac
import hashlib
import os
from unittest import mock

from flask.testing import FlaskClient

from scripts.bot.webhook_server import create_app
from scripts.bot.assign_copilot_license import assign_license


def simulate_webhook(secret: str, payload: bytes = b"{}") -> int:
    """Send a test webhook request using Flask's test client."""
    app = create_app()
    client: FlaskClient = app.test_client()
    signature = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    headers = {
        "X-Hub-Signature-256": signature,
        "X-GitHub-Event": "push",
    }
    response = client.post("/webhook", data=payload, headers=headers)
    return response.status_code


def simulate_license_assignment(username: str) -> bool:
    """Simulate calling ``assign_license`` with mocked requests."""
    with mock.patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = "ok"
        return assign_license(username, True)


if __name__ == "__main__":
    secret = os.environ.get("GITHUB_WEBHOOK_SECRET", "test")
    code = simulate_webhook(secret)
    print(f"Webhook status: {code}")
    success = simulate_license_assignment("octocat")
    print(f"License assigned: {success}")
