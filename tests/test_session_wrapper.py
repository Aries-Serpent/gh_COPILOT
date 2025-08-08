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
<<<<<<< HEAD
    session_dir = Path.home() / '.gh_copilot_sessions' / session_id
    meta_file = session_dir / 'metadata.json'
=======
    meta_file = tmp_path / '.gh_copilot_sessions' / f'{session_id}.json'
>>>>>>> 18051112 (feat: add session wrapper workflow and safe-run alias)
    assert meta_file.exists()

    recovered = subprocess.run(
        ['bash', str(script), 'recover', session_id],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    first_line = recovered.stdout.strip().splitlines()[0]
    meta = json.loads(first_line)
    assert meta['command'] == 'echo hi'

