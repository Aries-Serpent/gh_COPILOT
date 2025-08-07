"""Tests for database integration helpers in the web GUI."""

from web_gui.database_driven_web_gui_generator import EnterpriseDatabaseProcessor


def test_database_processor_executes(tmp_path) -> None:
    """The processor should run against an empty database without errors."""
    db_file = tmp_path / "web_gui.db"
    processor = EnterpriseDatabaseProcessor(database_path=str(db_file))
    assert processor.execute_processing() is True

