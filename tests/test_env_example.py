from pathlib import Path


def test_env_example_exists():
    repo_root = Path(__file__).resolve().parents[1]
    env_example = repo_root / ".env.example"
    assert env_example.exists(), ".env.example should be present at repository root"
