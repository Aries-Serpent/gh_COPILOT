"""Tests for compliance gating utilities."""

from utils.lessons_learned_integrator import fetch_lessons_by_tag
from utils.validation_utils import run_compliance_gates


def test_run_compliance_gates_records_failures(tmp_path):
    db_path = tmp_path / "lessons.db"
    result = run_compliance_gates([("sample_gate", False)], db_path=db_path)
    assert result is False
    lessons = fetch_lessons_by_tag("compliance", db_path=db_path)
    assert lessons

