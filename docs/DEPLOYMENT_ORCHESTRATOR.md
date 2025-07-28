# Deployment Orchestrator

The `UnifiedDeploymentOrchestrator` coordinates multiple enterprise systems
such as the file manager, backup manager and monitoring engine. It wraps
execution with the dual-copilot pattern to ensure independent validation.

Run the orchestrator via the CLI module:
```bash
python scripts/orchestration/UNIFIED_DEPLOYMENT_ORCHESTRATOR_CONSOLIDATED.py --start
```
This command starts a managed session with `ComprehensiveWorkspaceManager` and
executes the deployment workflow.
