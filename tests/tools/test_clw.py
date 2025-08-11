import subprocess


def test_clw_silently_handles_broken_pipe():
    cmd = "set -o pipefail; printf 'data\n' | /usr/local/bin/clw | head -n 0"
    result = subprocess.run(
        ["bash", "-c", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    assert b"Traceback" not in result.stderr
