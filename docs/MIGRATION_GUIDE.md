# Migration Guide

The following thin wrapper modules were relocated to improve project organization. Update any imports or CLI calls accordingly.

| Old Path | New Path |
| --- | --- |
| `advanced_qubo_optimization.py` | `scripts/entrypoints/advanced_qubo_optimization.py` |
| `simplified_quantum_integration_orchestrator.py` | `scripts/session/simplified_quantum_integration_orchestrator.py` |
| `unified_database_management_system.py` | `scripts/entrypoints/unified_database_management_system.py` |
| `unified_disaster_recovery_system.py` | `scripts/unified_disaster_recovery_system.py` |
| `unified_legacy_cleanup_system.py` | `scripts/unified_legacy_cleanup_wrapper.py` |
| `unified_monitoring_optimization_system.py` | `scripts/unified_monitoring_optimization_system.py` |
| `unified_script_generation_system.py` | `scripts/unified_script_generation_system.py` |
| `unified_session_management_system.py` | removed; use `scripts/session/unified_session_management_system.py` |

For any renamed modules, adjust imports to the new locations. CLI examples in the README and documentation have been updated accordingly.
