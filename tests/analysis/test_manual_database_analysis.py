import logging
import pytest

from scripts.analysis import manual_database_analysis as mda


def test_main_logs_and_raises(monkeypatch, caplog):
    def boom():
        raise ValueError("boom")

    monkeypatch.setattr(mda, "generate_action_statement", boom)
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError):
            mda.main()
    assert "analysis script error" in caplog.text
