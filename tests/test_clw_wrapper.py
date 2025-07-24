import subprocess


def test_clw_inserts_line_breaks() -> None:
    long_line = "x" * 1300
    proc = subprocess.run(
        ["/usr/local/bin/clw"],
        input=(long_line + "\n").encode(),
        env={"CLW_MAX_LINE_LENGTH": "1200"},
        capture_output=True,
    )
    output = proc.stdout.decode()
    assert "⏎" in output
    assert len(output.splitlines()) == 2
