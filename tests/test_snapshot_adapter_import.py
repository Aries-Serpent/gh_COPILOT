def test_snapshot_adapter_import_disabled_returns_empty():
    from gh_copilot.compat.codex_snapshot_adapter import initialize_adapter

    loaded = initialize_adapter(log_path=None)
    assert isinstance(loaded, dict)
    assert not loaded  # default: GH_COPILOT_USE_CODEX_SNAPSHOT is unset

