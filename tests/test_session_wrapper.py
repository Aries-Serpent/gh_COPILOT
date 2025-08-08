import json
import subprocess
from pathlib import Path


def test_wrap_and_recover(tmp_path):
    script = Path('.github/scripts/session_wrapper.sh').resolve()
    result = subprocess.run(
        ['bash', str(script), 'wrap', 'echo', 'hi'],
        capture_output=True,
        text=True,
        check=True,
    )
    session_id = result.stdout.strip().splitlines()[-1]
    session_dir = Path.home() / '.gh_copilot_sessions' / session_id
    meta_file = session_dir / 'metadata.json'
    assert meta_file.exists()

    recovered = subprocess.run(
        ['bash', str(script), 'recover', session_id],
        capture_output=True,
        text=True,
        check=True,
    )
    first_line = recovered.stdout.strip().splitlines()[0]
    meta = json.loads(first_line)
    assert meta['command'] == 'echo hi'

