import scripts.docker_healthcheck as dhc


def test_healthcheck_success(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "utils.cross_platform_paths.CrossPlatformPathManager.get_workspace_path",
        lambda: tmp_path,
    )
    monkeypatch.setattr(
        "utils.cross_platform_paths.CrossPlatformPathManager.get_backup_root",
        lambda: tmp_path / "backup",
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backup"))

    class FakeResp:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

    monkeypatch.setattr(dhc, "urlopen", lambda *a, **k: FakeResp())
    assert dhc.main() == 0
