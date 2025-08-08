import scripts.DEDICATED_CODEX_LOG_DATABASE_TASKS as tasks

def test_initialize_session(monkeypatch):
    calls = []
    monkeypatch.setattr(tasks, "init_codex_log_db", lambda: calls.append("init"))
    monkeypatch.setattr(tasks, "log_codex_start", lambda s: calls.append(("start", s)))
    tasks.initialize_session("s1")
    assert calls == ["init", ("start", "s1")]

def test_log_action(monkeypatch):
    recorded = []
    monkeypatch.setattr(
        tasks,
        "record_codex_action",
        lambda session_id, action, statement, metadata: recorded.append(
            (session_id, action, statement, metadata)
        ),
    )
    tasks.log_action("s1", "act", "stmt", "meta")
    assert recorded == [("s1", "act", "stmt", "meta")]

def test_finalize_session(monkeypatch):
    calls = []
    monkeypatch.setattr(tasks, "log_codex_end", lambda s, summary: calls.append(("end", s, summary)))
    monkeypatch.setattr(tasks, "finalize_codex_log_db", lambda: calls.append("final"))
    tasks.finalize_session("s1", "ok")
    assert calls == [("end", "s1", "ok"), "final"]
