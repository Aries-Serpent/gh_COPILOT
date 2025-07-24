import os
import subprocess


def test_clw_inserts_line_break():
    env = os.environ.copy()
    env["CLW_MAX_LINE_LENGTH"] = "1200"
    proc = subprocess.run(
        ["/usr/local/bin/clw"],
        input=b"A" * 1300,
        capture_output=True,
        env=env,
    )
    assert proc.returncode == 0
    out = proc.stdout
    assert b"\xe2\x8f\x8e\n" in out
    parts = out.split(b"\xe2\x8f\x8e\n")
    assert len(parts) == 2
    assert len(parts[0]) <= 1200
