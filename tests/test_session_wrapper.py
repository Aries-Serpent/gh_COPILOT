import json
import os
import subprocess
from pathlib import Path


def test_wrap_and_recover(tmp_path):
    script = Path('.github/scripts/session_wrapper.sh').resolve()
    env = os.environ.copy()
    env['HOME'] = str(tmp_path)
    result = subprocess.run(
        ['bash', str(script), 'wrap', 'echo', 'hi'],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    session_id = result.stdout.strip().splitlines()[-1]
    meta_file = tmp_path / '.gh_copilot_sessions' / f'{session_id}.json'
    assert meta_file.exists()

    recovered = subprocess.run(
        ['bash', str(script), 'recover_session', session_id],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    meta = json.loads(recovered.stdout)
    assert meta['command'] == 'echo hi'

