from gh_copilot.automation.core import StepCtx, run_phases


def test_error_path_logs_and_continues():
    ran = {"a": False, "c": False}

    def step_a():
        ran["a"] = True

    def step_b():
        raise ValueError("boom")

    def step_c():
        ran["c"] = True

    phases = [
        StepCtx(name="A", desc="ok", fn=step_a),
        StepCtx(name="B", desc="err", fn=step_b),
        StepCtx(name="C", desc="ok", fn=step_c),
    ]
    result = run_phases(phases, dry_run=True)

    assert result.phases_completed == 3
    assert result.ok is False
    assert ran["a"] is True and ran["c"] is True
    # Ensure error captured for B
    b_logs = [l for l in result.logs if l.get("name") == "B"]
    assert b_logs and b_logs[0].get("error")

