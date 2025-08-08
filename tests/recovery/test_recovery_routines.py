from __future__ import annotations

from src.monitoring.alerts import dispatch_alert


def test_db_disconnect_recovery():
    attempts = {"count": 0}

    def reconnect() -> bool:
        attempts["count"] += 1
        if attempts["count"] == 2:
            return True
        raise ConnectionError

    assert dispatch_alert("db_disconnect", reconnect=reconnect)


def test_failed_sync_recovery():
    attempts = {"count": 0}

    def resync() -> bool:
        attempts["count"] += 1
        if attempts["count"] > 1:
            return True
        raise RuntimeError

    assert dispatch_alert("sync_failed", resync=resync)


def test_auth_error_recovery():
    attempts = {"count": 0}

    def refresh_token() -> bool:
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise PermissionError
        return True

    assert dispatch_alert("auth_error", refresh_token=refresh_token)


def test_unknown_alert_returns_false():
    assert dispatch_alert("unknown") is False
