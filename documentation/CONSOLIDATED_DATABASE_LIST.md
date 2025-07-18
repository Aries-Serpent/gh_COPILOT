# Consolidated Database Inventory

The following SQLite databases remain after consolidating analytics data:

- enterprise_assets.db
- archive.db
- autonomous_decisions.db
- capability_scaler.db
- consolidation_tracking.db
- continuous_innovation.db
- deployment_preparation.db
- development.db
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
- testing.db
- v3_self_learning_engine.db

The `database_sync_scheduler.py` utility now reads this file to determine which
replicas should be kept in sync with `production.db`.

The unified `enterprise_assets.db` replaces `analytics.db`, `documentation.db`, and `template_completion.db`.

**Note:** Initial attempt on 2025-07-18 exceeded the 99.9 MB limit. Cleanup involved removing redundant data and compressing tables to reduce the database size. 
The migration succeeded, but the resulting database remains untracked due to size constraints and the lack of an immediate need for tracking. 
Future migrations should evaluate whether tracking this database is necessary and consider additional cleanup or optimization steps if required.
