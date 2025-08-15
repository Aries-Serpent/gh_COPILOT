import importlib

import pytest


@pytest.mark.parametrize(
    "module_name",
    [
        "scripts.compliance.sox_compliance",
        "scripts.compliance.hipaa_compliance",
        "scripts.compliance.pci_compliance",
        "scripts.compliance.gdpr_compliance",
    ],
)
def test_stub_delegates_to_update(monkeypatch, module_name):
    mod = importlib.import_module(module_name)
    called = {}

    def fake_update():
        called["yes"] = True
        return 1.23

    monkeypatch.setattr(mod, "update_compliance_metrics", fake_update)
    result = mod.main()
    assert called["yes"] is True
    assert result == 1.23
