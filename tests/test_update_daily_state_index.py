from pathlib import Path

from scripts.documentation.update_daily_state_index import update_index


def test_update_index_writes_links(tmp_path):
    source = tmp_path / "daily_state_update"
    source.mkdir()
    (source / "report_2025-08-07.pdf").write_text("pdf")
    (source / "report_2025-08-07.md").write_text("md")

    index = tmp_path / "daily_state_index.md"
    update_index(source_dir=source, index_path=index)

    content = index.read_text()
    assert "2025-08-07" in content
    assert "report_2025-08-07.pdf" in content
    assert "report_2025-08-07.md" in content

