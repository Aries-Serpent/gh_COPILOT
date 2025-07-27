import scripts.optimization.optimize_to_100_percent as opt
import scripts.optimization.security_compliance_enhancer as sce


class DummyConn:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass


def test_optimize_calls_db(monkeypatch):
    called = False

    def dummy():
        nonlocal called
        called = True
        return DummyConn()

    monkeypatch.setattr(opt, "get_validated_production_connection", dummy)
    opt.optimize_to_100_percent()
    assert called


def test_security_enhancer_calls_db(monkeypatch, tmp_path):
    called = False

    def dummy():
        nonlocal called
        called = True
        return DummyConn()

    monkeypatch.setattr(sce, "get_validated_production_connection", dummy)
    sce.SecurityComplianceEnhancer(str(tmp_path))
    assert called
