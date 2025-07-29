import logging
from scripts.optimization.enterprise_template_compliance_enhancer import EnterpriseFlake8Corrector


def test_correct_file_logs_and_fixes(tmp_path, caplog):
    bad = tmp_path / "bad.py"
    bad.write_text("import os, sys\nprint('hi')  \n", encoding="utf-8")

    fixer = EnterpriseFlake8Corrector(workspace_path=str(tmp_path))
    caplog.set_level(logging.INFO)
    changed = fixer.correct_file(str(bad))

    assert changed
    assert bad.read_text(encoding="utf-8") == "import os\nimport sys\n\nprint('hi')\n"
    assert any("SUCCESS" in record.message for record in caplog.records)
