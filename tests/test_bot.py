from pathlib import Path
from unittest import mock

from scripts.bot.webhook_server import create_app
from scripts.bot.assign_copilot_license import assign_license


def test_webhook_signature(monkeypatch, tmp_path):
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "test")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path.parent / "backups"))
    app = create_app()
    client = app.test_client()
    payload = b"{}"
    import hmac
    import hashlib

    sig = "sha256=" + hmac.new(b"test", payload, hashlib.sha256).hexdigest()
    res = client.post("/webhook", data=payload, headers={"X-Hub-Signature-256": sig})
    assert res.status_code == 200


def test_webhook_invalid_signature(monkeypatch, tmp_path):
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "test")
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path))
    app = create_app()
    client = app.test_client()
    payload = b"{}"
    import hmac
    import hashlib

    sig = "sha256=" + hmac.new(b"wrong", payload, hashlib.sha256).hexdigest()
    res = client.post("/webhook", data=payload, headers={"X-Hub-Signature-256": sig})
    assert res.status_code == 400


def test_assign_license(monkeypatch):
    workspace = Path("/tmp/gh_workspace")
    workspace.mkdir(exist_ok=True)
    monkeypatch.setenv("GITHUB_TOKEN", "t")
    monkeypatch.setenv("GITHUB_ORG", "o")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", "/tmp/gh_backups")
    with mock.patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = "ok"
        assert assign_license("user")
