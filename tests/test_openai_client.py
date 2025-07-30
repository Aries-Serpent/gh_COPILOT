from unittest import mock

from third_party.openai_client import OpenAIClient


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
