from enterprise_modules import compliance
from scripts import code_placeholder_audit as audit


def test_placeholder_counts_consistent(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    sample = tmp_path / "example.py"
    sample.write_text(
        "\n".join(
            [
                "TODO",
                "FIXME",
                "pass",
                "NotImplementedError",
                "placeholder",
                "HACK",
                "BUG",
                "XXX",
            ]
        ),
        encoding="utf-8",
    )

    audit_count = len(audit.scan_file_for_placeholders(sample))
    compliance_count = compliance._count_placeholders()  # noqa: SLF001
    assert audit_count == compliance_count
