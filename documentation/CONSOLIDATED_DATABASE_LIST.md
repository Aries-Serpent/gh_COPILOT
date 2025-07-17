# Consolidated Database Inventory

The following SQLite databases remain after consolidating analytics data:

- analytics.db
- enterprise_assets.db
- archive.db
- autonomous_decisions.db
- capability_scaler.db
- consolidation_tracking.db
- continuous_innovation.db
- deployment_preparation.db
- development.db
- documentation_sync.db
- enhanced_deployment_tracking.db
- enhanced_intelligence.db
- enterprise_ml_engine.db
- executive_alerts.db
- factory_deployment.db
- instruction_orchestrator.db
- learning_monitor.db
- ml_deployment_engine.db
- production.db
- project_grading_database.db
- scaling_innovation.db
- script_generation.db
- staging.db
- strategic_implementation.db
- template_completion.db
- testing.db
- v3_self_learning_engine.db

The `database_sync_scheduler.py` utility now reads this file to determine which
replicas should be kept in sync with `production.db`.
