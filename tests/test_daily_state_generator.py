"""Tests for daily_state_generator."""

from __future__ import annotations

from scripts.documentation import daily_state_generator as dsg


def test_generate_daily_state_creates_md_and_pdf(tmp_path, monkeypatch):
    called: dict[str, object] = {}

    def fake_run(primary, secondary):
        called["primary"] = primary
        called["secondary"] = secondary
        return primary() and secondary()

    monkeypatch.setattr(dsg, "run_dual_copilot_validation", fake_run)

    md_path, pdf_path = dsg.generate_daily_state(output_dir=tmp_path)

    assert md_path.exists() and pdf_path.exists()
    assert "primary" in called and "secondary" in called
