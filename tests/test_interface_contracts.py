from scripts.monitoring.performance_monitor import (
    MonitoringRequest,
    validate_monitoring_request,
)
from deployment.scripts.deploy_to_production import (
    DeploymentRequest,
    validate_deployment_request,
)
import pytest


def test_codegen_contract_validation():
    qiskit = pytest.importorskip("qiskit")
    if not hasattr(qiskit, "QuantumCircuit"):
        pytest.skip("qiskit missing QuantumCircuit")
    from template_engine.db_first_code_generator import (
        CodegenRequest,
        TemplateAutoGenerator,
        validate_codegen_request,
    )

    with pytest.raises(ValueError):
        validate_codegen_request(CodegenRequest(objective=""))
    gen = TemplateAutoGenerator()
    result = gen.generate_from_contract(CodegenRequest(objective="demo"))
    assert result.code


def test_monitoring_contract_validation():
    with pytest.raises(ValueError):
        validate_monitoring_request(MonitoringRequest(interval=0))
    validate_monitoring_request(MonitoringRequest(interval=1))


def test_deployment_contract_validation():
    with pytest.raises(ValueError):
        validate_deployment_request(DeploymentRequest(environment="staging"))
    validate_deployment_request(DeploymentRequest(environment="production"))
