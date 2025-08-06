import datetime
import pytest
from scripts.orchestrators.unified_wrapup_orchestrator import WrapUpResult


def test_wrapup_result_post_init_valid():
    result = WrapUpResult(session_id="id", start_time=datetime.datetime.now())
    assert result.compliance_score == 0.0


def test_wrapup_result_post_init_invalid_end_time():
    start = datetime.datetime.now()
    with pytest.raises(ValueError):
        WrapUpResult(session_id="id", start_time=start, end_time=start - datetime.timedelta(seconds=1))


def test_wrapup_result_post_init_invalid_score():
    start = datetime.datetime.now()
    with pytest.raises(ValueError):
        WrapUpResult(session_id="id", start_time=start, compliance_score=150.0)
