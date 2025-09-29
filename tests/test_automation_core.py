from gh_copilot.automation.core import StepCtx, run_phases


def test_run_phases_basic_dry_run():
    acc = []

    def a():
        acc.append("a")

    def b():
        acc.append("b")

    phases = [
        StepCtx(name="A", desc="alpha", fn=a),
        StepCtx(name="B", desc="beta", fn=b),
    ]

    result = run_phases(phases, dry_run=True)
    assert result.phases_completed == 2
    assert result.ok is True
    assert len(result.logs) >= 2
    assert acc == ["a", "b"]

