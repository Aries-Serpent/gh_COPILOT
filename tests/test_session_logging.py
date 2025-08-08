"""Verify codex logging includes timestamps and session IDs."""

from datetime import datetime

import unified_session_management_system as usm


def test_log_action_includes_timestamp(monkeypatch):
    calls: dict[str, str] = {}

    def fake_log(session_id, action, statement, metadata=""):
        calls.update(
            session_id=session_id,
            action=action,
            statement=statement,
            metadata=metadata,
        )

    monkeypatch.setattr(usm, "log_codex_action", fake_log)

    usm.log_action("sess-1", "start", "message")

    assert calls["session_id"] == "sess-1"
    assert calls["action"] == "start"
    assert calls["statement"] == "message"
    # Ensure metadata contains a parseable timestamp
    assert calls["metadata"]
    datetime.fromisoformat(calls["metadata"])
