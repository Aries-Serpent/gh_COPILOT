from session_management_consolidation_executor import EnterpriseUtility
from utils.lessons_learned_integrator import load_lessons


def test_lessons_persist_across_sessions(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    (workspace / "databases").mkdir(parents=True)
    backup_root = tmp_path / "backups"
    backup_root.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    util = EnterpriseUtility(workspace_path=workspace)
    assert util.loaded_lessons == []
    assert util.execute_utility() is True

    lessons = load_lessons(util.learning_db)
    assert any("Session utility" in lesson["description"] for lesson in lessons)

    util2 = EnterpriseUtility(workspace_path=workspace)
    assert util2.loaded_lessons
