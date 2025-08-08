"""Security related tests for the web GUI modules."""

import pytest


class DummyUserDB:
    def __init__(self, record):
        self._record = record

    def get(self, _username):  # pragma: no cover - simple helper
        return self._record


def test_authenticate_user_success() -> None:
    """Users with valid credentials and roles should authenticate."""
    try:
        from web_gui.security import authentication
    except Exception:
        pytest.skip("authentication module unavailable")

    user_db = DummyUserDB({"password": "pw", "roles": ["admin"]})
    assert authentication.authenticate_user("u", "pw", user_db, required_role="admin")

