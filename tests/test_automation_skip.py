from gh_copilot.automation.core import StepCtx, run_phases


def test_skip_step_when_dry_run_not_ok():
    ran = {"flag": False}

    def dangerous():
        ran["flag"] = True

    phases = [StepCtx(name="Danger", desc="skip in dry-run", fn=dangerous, dry_run_ok=False)]
    result = run_phases(phases, dry_run=True)
    assert result.ok is True
    assert result.phases_completed == 1
    assert ran["flag"] is False
    assert any(log.get("skipped_due_to_dry_run") for log in result.logs)

