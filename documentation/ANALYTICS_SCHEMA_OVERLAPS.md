# Analytics Schema Overlaps

This report summarizes tables that appear in more than one analytics-related database.

| Table Name | Databases |
|------------|-----------|
| audit_trails | analytics.db, performance_analysis.db |
| autonomous_file_management | analytics.db, monitoring.db, performance_analysis.db |
| compliance_tracking | analytics.db, performance_analysis.db |
| enterprise_metadata | analytics.db, performance_analysis.db |
| file_regeneration_metadata | analytics.db, monitoring.db, performance_analysis.db |
| optimization_logs | analytics.db, optimization_metrics.db, performance_monitoring.db |
| pattern_analysis | analytics.db, optimization_metrics.db, performance_monitoring.db |
| pattern_matching_engine | analytics.db, monitoring.db, performance_analysis.db |
| performance_baselines | analytics.db, performance_analysis.db |
| performance_metrics | analytics.db, optimization_metrics.db, performance_analysis.db, performance_monitoring.db |
| predictive_models | advanced_analytics.db, analytics.db |
| regeneration_history | analytics.db, monitoring.db, performance_analysis.db |
| regeneration_patterns | analytics.db, monitoring.db, performance_analysis.db |
| regeneration_templates | analytics.db, monitoring.db, performance_analysis.db |
| security_policies | analytics.db, performance_analysis.db |
| template_intelligence | analytics.db, monitoring.db, performance_analysis.db |
| template_patterns | analytics.db, optimization_metrics.db, performance_monitoring.db |
