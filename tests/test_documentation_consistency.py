from pathlib import Path

DOC_REFERENCES = {
    "README.md": [
        "simplified_quantum_integration_orchestrator.py",
        "quantum_integration_orchestrator.py",
        "scripts/wlc_session_manager.py",
    ],
    "docs/QUANTUM_HARDWARE_SETUP.md": [
        "quantum_integration_orchestrator.py",
    ],
}


def test_documentation_paths_exist():
    repo_root = Path(__file__).resolve().parents[1]
    for doc, refs in DOC_REFERENCES.items():
        content = (repo_root / doc).read_text()
        for ref in refs:
            assert ref in content, f"{ref} not referenced in {doc}"
            assert (repo_root / ref).exists(), f"{ref} missing in repository"


def test_quantum_docs_refer_to_simulation():
    repo_root = Path(__file__).resolve().parents[1]
    readme_text = (repo_root / "README.md").read_text().lower()
    hardware_doc_text = (repo_root / "docs/QUANTUM_HARDWARE_SETUP.md").read_text().lower()
    assert "simulation" in readme_text
    assert "simulation" in hardware_doc_text
