import json
import pytest
from dashboard.enterprise_dashboard import app, corrections_ws, request


@pytest.fixture
def client():
    return app.test_client()


def test_corrections_sse(client, monkeypatch):
    monkeypatch.setattr(
        "dashboard.enterprise_dashboard._load_corrections",
        lambda limit=10: [{"timestamp": "t", "path": "p", "status": "ok"}],
    )
    resp = client.get("/corrections_stream?once=1")
    data = resp.get_data(as_text=True)
    assert "data:" in data
    assert "p" in data


def test_corrections_websocket(monkeypatch):
    messages = []

    class DummyWS:
        def send(self, payload):
            messages.append(payload)
            raise RuntimeError("stop")

    monkeypatch.setattr(
        "dashboard.enterprise_dashboard._load_corrections",
        lambda limit=10: [{"foo": "bar"}],
    )
    with app.test_request_context("/ws/corrections"):
        request.environ["wsgi.websocket"] = DummyWS()
        corrections_ws()
    assert json.loads(messages[0])[0]["foo"] == "bar"
