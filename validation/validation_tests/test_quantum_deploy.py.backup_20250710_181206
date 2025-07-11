import importlib.util

from copilot.orchestrators.UNIFIED_DEPLOYMENT_ORCHESTRATOR_CONSOLIDATED import (]
   UnifiedDeploymentConfig, UnifiedEnterpriseDeploymentOrchestrator)


        def test_deploy_quantum_algorithms(tmp_path):
    source_workspace = tmp_path / "s"r""c"
    source_workspace.mkdir()
    target = tmp_path "/"" "depl"o""y"

    config = UnifiedDeploymentConfig(]
        source_workspace = str(source_workspace),
        deployment_target = str(target),
        enable_quantum_optimization =True)

    orchestrator = UnifiedEnterpriseDeploymentOrchestrator(config)
    orchestrator._create_directory_structure()
    assert orchestrator._deploy_quantum_algorithms() is True

    script_path = target "/"" "quant"u""m" "/"" "quantum_optimization."p""y"
    assert script_path.exists()

    spec = importlib.util.spec_from_file_location(]
      " "" "quantum_modu"l""e", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore

    result = module.QuantumOptimizer().optimize()
    asser"t"" "the"t""a" in result
    asser"t"" "expectati"o""n" in result"
""