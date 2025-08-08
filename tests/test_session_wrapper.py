import json
import subprocess
from pathlib import Path


def test_wrap_and_recover(tmp_path):
    script = Path('.github/scripts/session_wrapper.sh').resolve()
    result = subprocess.run(
        ['bash', str(script), 'wrap_command', 'echo', 'hi'],
        capture_output=True,
        text=True,
        check=True,
    )
    session_id = result.stdout.strip().splitlines()[-1]
    meta_file = Path('.session_meta') / f'{session_id}.json'
    assert meta_file.exists()

    recovered = subprocess.run(
        ['bash', str(script), 'recover_session', session_id],
        capture_output=True,
        text=True,
        check=True,
    )
    meta = json.loads(recovered.stdout)
    assert meta['command'] == 'echo hi'

