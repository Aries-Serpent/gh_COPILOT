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
