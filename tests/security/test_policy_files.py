from security.validator import CONFIG_DIR, validate_security_configs


def test_policy_files_are_valid():
    results = validate_security_configs(CONFIG_DIR)
    assert all(info["status"] == "pass" for info in results.values())
    assert all(not info["missing"] for info in results.values())
