import os
from pathlib import Path

from session_protocol_validator import SessionProtocolValidator
from unified_session_management_system import UnifiedSessionManagementSystem


def test_startup_detects_zero_byte(tmp_path):
    zero_file = tmp_path / "a.py"
    zero_file.write_text("")

    validator = SessionProtocolValidator(workspace_root=str(tmp_path))
    assert validator.validate_startup() is False


def test_unified_session_start_fails_with_zero_byte(tmp_path):
    zero_file = tmp_path / "b.py"
    zero_file.write_text("")

    mgr = UnifiedSessionManagementSystem(workspace_root=str(tmp_path))
    assert mgr.start_session() is False
