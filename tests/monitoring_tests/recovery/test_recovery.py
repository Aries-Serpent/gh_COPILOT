import sqlite3

from ghc_monitoring.recovery import recover_system


def test_recovers_db_disconnect(tmp_path):
    models = {"db_disconnects": (0.0, 1.0)}
    metrics = {"db_disconnects": 5.0}

    conn = sqlite3.connect(":memory:")
    conn.close()

    factory_calls: list[int] = []

    def factory() -> sqlite3.Connection:
        factory_calls.append(1)
        return sqlite3.connect(":memory:")

    cache: dict[str, int] = {}

    result = recover_system(
        models,
        metrics,
        [conn],
        factory,
        cache,
        lambda: {"a": 1},
        tmp_path,
    )

    assert result == {"db_reconnects": 1, "cache_refreshes": 0, "log_truncations": 0}
    assert len(factory_calls) == 1


def test_recovers_cache_miss(tmp_path):
    models = {"cache_miss": (0.0, 1.0)}
    metrics = {"cache_miss": 5.0}

    conn = sqlite3.connect(":memory:")

    cache: dict[str, int] = {}

    result = recover_system(
        models,
        metrics,
        [conn],
        lambda: sqlite3.connect(":memory:"),
        cache,
        lambda: {"b": 2},
        tmp_path,
    )

    assert result == {"db_reconnects": 0, "cache_refreshes": 1, "log_truncations": 0}
    assert cache == {"b": 2}


def test_recovers_log_saturation(tmp_path):
    models = {"log_saturation": (0.0, 1.0)}
    metrics = {"log_saturation": 5.0}

    conn = sqlite3.connect(":memory:")

    log_file = tmp_path / "test.log"
    log_file.write_text("x" * 10)

    cache: dict[str, int] = {"c": 3}

    result = recover_system(
        models,
        metrics,
        [conn],
        lambda: sqlite3.connect(":memory:"),
        cache,
        lambda: {},
        tmp_path,
        log_limit=5,
    )

    assert result == {"db_reconnects": 0, "cache_refreshes": 0, "log_truncations": 1}
    assert log_file.stat().st_size == 0
