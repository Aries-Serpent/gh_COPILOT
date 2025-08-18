# Interface Contracts

This document defines the input and output contracts for code generation,
monitoring, and deployment modules. Each contract includes its idempotency
rules to ensure repeatable operations.

## Code Generation

**Module:** `template_engine.db_first_code_generator`

- **Input:** `CodegenRequest`
  - `objective` (`str`): description of the desired script.
- **Output:** `CodegenResult`
  - `code` (`str`): generated template text.
- **Idempotency:** generating with the same objective yields the same code
  without producing additional side effects.

## Monitoring

**Module:** `scripts.monitoring.performance_monitor`

- **Input:** `MonitoringRequest`
  - `interval` (`int`): seconds between samples.
  - `prometheus` (`bool`): emit Prometheus format when `True`.
- **Output:** `MonitoringOutput`
  - `metrics` (`dict[str, float]`): collected metric values.
- **Idempotency:** running with identical parameters repeatedly reports
  metrics independently and does not accumulate duplicate state.

## Deployment

**Module:** `deployment.scripts.deploy_to_production`

- **Input:** `DeploymentRequest`
  - `environment` (`str`): target environment; must be `"production"`.
  - `include_quantum` (`bool`): deploy quantum modules when `True`.
- **Output:** `DeploymentResult`
  - `message` (`str`): human readable deployment summary.
  - `success` (`bool`): `True` when deployment completed.
- **Idempotency:** deploying the same version to the same environment is
  safe to repeat; subsequent runs produce the same outcome without side
  effects.

