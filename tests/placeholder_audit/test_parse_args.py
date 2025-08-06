import scripts.code_placeholder_audit as audit


import pytest


def test_removed_dry_run_option():
    with pytest.raises(SystemExit):
        audit.parse_args(["--dry-run"])


def test_removed_cleanup_option():
    with pytest.raises(SystemExit):
        audit.parse_args(["--cleanup"])


def test_removed_force_option():
    with pytest.raises(SystemExit):
        audit.parse_args(["--force"])


def test_apply_suggestions_flag():
    args = audit.parse_args(["--apply-suggestions"])
    assert args.apply_suggestions is True
