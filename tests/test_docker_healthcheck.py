import os
import subprocess
import sys
from pathlib import Path

import scripts.docker_healthcheck as dhc


def test_healthcheck_success(monkeypatch, tmp_path):
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
