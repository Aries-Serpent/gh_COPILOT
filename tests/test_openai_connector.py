import importlib
from unittest import mock

import third_party.openai_client


def test_send_prompt(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "key")
    module = importlib.reload(importlib.import_module("github_integration.openai_connector"))
    result = {"choices": [{"message": {"content": "ok"}}]}
    with mock.patch.object(third_party.openai_client.OpenAIClient, "request") as req:
        req.return_value.status_code = 200
        req.return_value.json.return_value = result
        resp = module.send_prompt("hello", model="gpt-test")
    assert resp == result
    assert req.called
    method, endpoint, payload = req.call_args[0]
    assert method == "POST"
    assert endpoint == "chat/completions"
    assert payload["messages"][0]["content"] == "hello"
