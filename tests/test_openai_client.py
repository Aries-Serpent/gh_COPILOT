from unittest import mock

from third_party.openai_client import OpenAIClient
import third_party.openai_client as oc


def test_chat_completion_success(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    client = OpenAIClient(base_url="http://api")
    result = {"choices": [{"message": {"content": "hi"}}]}
    with mock.patch("requests.Session.request") as req:
        req.return_value.status_code = 200
        req.return_value.json.return_value = result
        resp = client.chat_completion([{"role": "user", "content": "hi"}])
    assert resp == result
    assert req.called


def test_chat_completion_retry(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    client = OpenAIClient(base_url="http://api", max_retries=2)
    first = mock.Mock(status_code=500)
    second = mock.Mock(status_code=200)
    second.json.return_value = {"ok": True}
    with mock.patch("requests.Session.request", side_effect=[first, second]) as req:
        resp = client.chat_completion([{"role": "user", "content": "hi"}])
    assert req.call_count == 2
    assert resp == {"ok": True}


def test_rate_limiting(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    client = OpenAIClient(base_url="http://api", rate_limit=1.0)

    current = {"t": 0.0}

    def fake_time() -> float:
        return current["t"]

    sleeps: list[float] = []

    def fake_sleep(d: float) -> None:
        sleeps.append(d)
        current["t"] += d

    monkeypatch.setattr(oc.time, "time", fake_time)
    monkeypatch.setattr(oc.time, "sleep", fake_sleep)

    with mock.patch("requests.Session.request") as req:
        req.return_value.status_code = 200
        req.return_value.json.return_value = {}
        client.chat_completion([{"role": "user", "content": "a"}])
        t1 = current["t"]
        client.chat_completion([{"role": "user", "content": "b"}])
        t2 = current["t"]

    assert t2 - t1 >= 1.0
    assert sleeps == [1.0, 1.0]
