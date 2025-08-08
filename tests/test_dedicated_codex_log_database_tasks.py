import scripts.DEDICATED_CODEX_LOG_DATABASE_TASKS as tasks

def test_initialize_session_calls_init_and_start(monkeypatch):
    calls = []
    monkeypatch.setattr(tasks, "init_codex_log_db", lambda: calls.append("init"))
    monkeypatch.setattr(tasks, "log_codex_start", lambda sid: calls.append(("start", sid)))
    tasks.initialize_session("s1")
    assert calls == ["init", ("start", "s1")]

def test_log_action_records(monkeypatch):
    recorded = []
    monkeypatch.setattr(
        tasks,
        "record_codex_action",
        lambda sid, act, stmt, meta: recorded.append((sid, act, stmt, meta)),
    )
    tasks.log_action("s1", "act", "stmt", "meta")
    assert recorded == [("s1", "act", "stmt", "meta")]

def test_finalize_session_calls_end_and_finalize(monkeypatch):
    calls = []
    monkeypatch.setattr(
        tasks,
        "log_codex_end",
        lambda sid, summ: calls.append(("end", sid, summ)),
    )
    monkeypatch.setattr(tasks, "finalize_codex_log_db", lambda: calls.append("finalize"))
    tasks.finalize_session("s1", "summary")
    assert calls == [("end", "s1", "summary"), "finalize"]


def test_codex_session_logger_context(monkeypatch):
    import utils.codex_log_db as cldb

    calls = []
    monkeypatch.setattr(cldb, "init_codex_log_db", lambda: calls.append("init"))
    monkeypatch.setattr(cldb, "log_codex_start", lambda sid: calls.append(("start", sid)))
    monkeypatch.setattr(
        cldb,
        "record_codex_action",
        lambda sid, act, stmt, meta: calls.append((sid, act, stmt, meta)),
    )
    monkeypatch.setattr(
        cldb, "log_codex_end", lambda sid, summ: calls.append(("end", sid, summ))
    )
    monkeypatch.setattr(cldb, "finalize_codex_log_db", lambda: calls.append("finalize"))

    with cldb.CodexSessionLogger("s1") as logger:
        logger.log("act", "stmt")

    assert calls == [
        "init",
        ("start", "s1"),
        ("s1", "act", "stmt", ""),
        ("end", "s1", "session complete"),
        "finalize",
    ]
