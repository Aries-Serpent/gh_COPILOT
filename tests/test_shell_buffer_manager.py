import shutil
from pathlib import Path

from utils.general_utils import safe_shell_execute


def test_safe_shell_execute_overflow(capsys):
    target = Path("/tmp/gh_copilot_sessions")
    if target.exists():
        shutil.rmtree(target)
    cmd = "python - <<'PY'\nprint('A' * 5000)\nPY"
    out = safe_shell_execute(cmd)
    assert len(out.strip()) == 4096
    summary = capsys.readouterr().out
    assert "overflow logged to:" in summary
    files = list(target.glob("overflow_*"))
    assert len(files) == 1
    assert files[0].read_text() == "A" * (5000 - 4096)
