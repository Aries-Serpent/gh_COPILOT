import os
import subprocess


def test_clw_wraps_long_lines(tmp_path):
    line = b"a" * 1300 + b"\n"
    env = dict(os.environ, CLW_MAX_LINE_LENGTH="1200")
    result = subprocess.run(["/usr/local/bin/clw"], input=line, stdout=subprocess.PIPE, env=env, check=True)
    assert b"\xe2\x8f\x8e\n" in result.stdout
    wrapped_line = result.stdout.split(b"\xe2\x8f\x8e\n")[0]
    assert len(wrapped_line) <= 1200
