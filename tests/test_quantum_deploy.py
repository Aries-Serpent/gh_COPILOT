import importlib.util

from copilot.orchestrators.UNIFIED_DEPLOYMENT_ORCHESTRATOR_CONSOLIDATED import (]
   UnifiedDeploymentConfig, UnifiedEnterpriseDeploymentOrchestrator)


        def test_deploy_quantum_algorithms(tmp_path):
    source_workspace = tmp_path / "src"
    source_workspace.mkdir()
    target = tmp_path / "deploy"

    config = UnifiedDeploymentConfig(]
        source_workspace = str(source_workspace),
        deployment_target = str(target),
        enable_quantum_optimization =True)

    orchestrator = UnifiedEnterpriseDeploymentOrchestrator(config)
    orchestrator._create_directory_structure()
    assert orchestrator._deploy_quantum_algorithms() is True

    script_path = target / "quantum" / "quantum_optimization.py"
    assert script_path.exists()

    spec = importlib.util.spec_from_file_location(]
        "quantum_module", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore

    result = module.QuantumOptimizer().optimize()
    assert "theta" in result
    assert "expectation" in result
