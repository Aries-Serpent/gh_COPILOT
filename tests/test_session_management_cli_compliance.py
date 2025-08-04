import sys
import types
import unified_session_management_system as usm


def test_main_invokes_compliance_validation(monkeypatch, tmp_path):
    called = []
    monkeypatch.setattr(
        usm,
        "validate_environment",
        lambda: called.append(True) or True,
    )

    class DummySystem:
        workspace_root = tmp_path

        def start_session(self):
            return True

        def end_session(self):
            return True

    dummy_module = types.ModuleType("usms")
    dummy_module.UnifiedSessionManagementSystem = lambda: DummySystem()
    sys.modules[
        "scripts.utilities.unified_session_management_system"
    ] = dummy_module

    monkeypatch.setattr(
        "utils.validation_utils.detect_zero_byte_files",
        lambda root: [],
    )
    assert usm.main() == 0
    assert called
