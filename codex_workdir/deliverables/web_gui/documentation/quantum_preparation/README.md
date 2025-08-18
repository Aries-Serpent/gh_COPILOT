# Quantum Preparation - gh_COPILOT Web GUI

Steps to prime the web interface for quantum-enabled features. All quantum operations run in simulation, but databases and routes still require preparation.

## Key Resources

- [migration_scripts/quantum_preparation.sql](../../../migration_scripts/quantum_preparation.sql) – primes databases for quantum metrics
- [web_gui/scripts/flask_apps/quantum_enhanced_framework.py](../../scripts/flask_apps/quantum_enhanced_framework.py) – exposes simulated quantum endpoints

## Workflow

1. Apply the SQL migration to initialize quantum-related tables.
2. Launch the `quantum_enhanced_framework` Flask app to enable optional quantum routes.

