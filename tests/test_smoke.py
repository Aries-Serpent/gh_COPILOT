from pathlib import Path


def test_smoke_layout():
    assert Path("src/gh_copilot/models.py").exists()
    assert Path("src/gh_copilot/dao.py").exists()
    assert Path("src/gh_copilot/api.py").exists()
    assert Path("src/gh_copilot/cli.py").exists()
