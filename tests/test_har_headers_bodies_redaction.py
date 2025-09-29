import json


def test_extract_headers_bodies_no_redaction():
    from scripts.har_ingest import _extract_headers_and_bodies

    entry = {
        "request": {
            "headers": [{"name": "X-A", "value": "1"}],
            "postData": {"text": "payload", "mimeType": "text/plain"},
        },
        "response": {
            "headers": [{"name": "Y-B", "value": "2"}],
            "content": {"text": "body", "mimeType": "application/json", "encoding": "utf8"},
        },
    }
    parts = _extract_headers_and_bodies(entry, redact_headers=False, redact_bodies=False)
    assert parts["req_headers_json"][0]["value"] == "1"
    assert parts["res_headers_json"][0]["value"] == "2"
    assert parts["req_body_text"] == "payload"
    assert parts["res_body_text"] == "body"
    assert parts["res_body_mime"] == "application/json"


def test_extract_headers_bodies_with_redaction():
    from scripts.har_ingest import _extract_headers_and_bodies

    entry = {
        "request": {
            "headers": [{"name": "Auth", "value": "secret"}],
            "postData": {"text": "token=abc", "mimeType": "text/plain"},
        },
        "response": {
            "headers": [{"name": "Set-Cookie", "value": "sid=123"}],
            "content": {"text": "{""msg"": ""ok""}", "mimeType": "application/json"},
        },
    }
    parts = _extract_headers_and_bodies(entry, redact_headers=True, redact_bodies=True)
    assert all(h["value"] == "[REDACTED]" for h in parts["req_headers_json"])
    assert all(h["value"] == "[REDACTED]" for h in parts["res_headers_json"])
    assert parts["req_body_text"] == "[REDACTED]"
    assert parts["res_body_text"] == "[REDACTED]"

