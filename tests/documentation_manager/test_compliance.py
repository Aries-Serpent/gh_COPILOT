from documentation.enterprise_documentation_manager import EnterpriseDocumentationManager


def test_calculate_compliance_capped(tmp_path, monkeypatch):
    monkeypatch.setenv('GH_COPILOT_WORKSPACE', str(tmp_path))
    manager = EnterpriseDocumentationManager(db_path=':memory:')
    score = manager.calculate_compliance('x' * 250)
    assert score == 1.0


def test_calculate_compliance_basic(tmp_path, monkeypatch):
    monkeypatch.setenv('GH_COPILOT_WORKSPACE', str(tmp_path))
    manager = EnterpriseDocumentationManager(db_path=':memory:')
    score = manager.calculate_compliance('x' * 50)
    assert 0 < score < 1.0
