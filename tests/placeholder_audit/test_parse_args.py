import scripts.code_placeholder_audit as audit


def test_parse_args_dry_run_alias():
    args = audit.parse_args(["--dry-run"])
    assert args.simulate is True


def test_parse_args_cleanup_alias():
    args = audit.parse_args(["--cleanup"])
    assert args.apply_fixes is True


def test_parse_args_force():
    args = audit.parse_args(["--force"])
    assert args.force is True
