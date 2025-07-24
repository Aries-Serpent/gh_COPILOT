import os
import subprocess


def test_clw_wraps_long_lines(tmp_path):
    test_input = b"x" * 1300 + b"\n"
    env = os.environ.copy()
    env["CLW_MAX_LINE_LENGTH"] = "1200"
    result = subprocess.run(
        [
            "/usr/local/bin/clw",
        ],
        input=test_input,
        capture_output=True,
        env=env,
        check=True,
    )
    assert b"\xe2\x8f\x8e\n" in result.stdout
