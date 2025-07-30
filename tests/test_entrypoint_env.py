import os
import subprocess
from pathlib import Path


def test_entrypoint_has_validation_call():
    text = Path('entrypoint.sh').read_text()
    assert 'validate_enterprise_environment' in text


def test_entrypoint_requires_env(tmp_path):
    env = os.environ.copy()
    env['GH_COPILOT_WORKSPACE'] = str(tmp_path)
    env.pop('GH_COPILOT_BACKUP_ROOT', None)
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(['bash', 'entrypoint.sh'], cwd=repo_root, env=env, capture_output=True, text=True)
    assert result.returncode != 0
    assert 'GH_COPILOT_BACKUP_ROOT is not set' in result.stderr
