import importlib
import importlib.util
import sys
from pathlib import Path

def _dynamic_import_from_scripts():
    repo_root = Path(__file__).resolve().parents[1]
    candidate = repo_root / "scripts" / "wlc_session_manager.py"
    if candidate.exists():
        spec = importlib.util.spec_from_file_location("wlc_session_manager", candidate)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["wlc_session_manager"] = mod
        spec.loader.exec_module(mod)  # type: ignore
        return mod
    return None

def test_import_wlc_session_manager():
    try:
        import wlc_session_manager  # noqa: F401
        assert True
        return
    except Exception:
        mod = _dynamic_import_from_scripts()
        assert mod is not None, "Unable to import wlc_session_manager from package or scripts/"
