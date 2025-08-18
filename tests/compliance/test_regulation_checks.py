"""Boundary tests for regulation-specific compliance helpers."""

from scripts.compliance.gdpr_compliance import check_data_retention
from scripts.compliance.hipaa_compliance import check_phi_access
from scripts.compliance.pci_compliance import check_card_storage
from scripts.compliance.sox_compliance import check_financial_controls


def test_sox_financial_controls_boundary():
    assert check_financial_controls([1_000_000])
    assert not check_financial_controls([1_000_001])


def test_hipaa_phi_access_boundary():
    allowed = {"alice"}
    assert check_phi_access(["alice"], allowed)
    assert not check_phi_access(["bob"], allowed)


def test_gdpr_retention_boundary():
    assert check_data_retention([365])
    assert not check_data_retention([366])


def test_pci_card_storage_boundary():
    assert check_card_storage(["************1111"])
    assert not check_card_storage(["4111111111111111"])

