from pathlib import Path
import importlib.util


def test_docs_reference_existing_scripts():
    repo_root = Path(__file__).resolve().parents[2]
    module_path = repo_root / "scripts" / "validate_doc_script_paths.py"
    spec = importlib.util.spec_from_file_location("validate_doc_script_paths", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    assert not module.find_missing_script_refs(repo_root)
