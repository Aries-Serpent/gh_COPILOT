# Template Intelligence Platform - Database Schema Documentation

**Generated:** 2025-07-03 02:57:07  
**Version:** 1.0.0  
**System:** Enterprise Template Intelligence Platform  
## Overview

This document provides comprehensive documentation for the Template Intelligence Platform database schemas. The platform utilizes 8 specialized databases to manage template intelligence, environment adaptation, and cross-database aggregation.

## Database Architecture

The Template Intelligence Platform employs a multi-database architecture with the following components:

### Analytics Collector Database

- **File:** `e:\gh_COPILOT\databases\analytics_collector.db`
- **Tables:** 4
- **Purpose:** Specialized data management

### Capability Scaler Database

- **File:** `e:\gh_COPILOT\databases\capability_scaler.db`
- **Tables:** 5
- **Purpose:** Specialized data management

### Continuous Innovation Database

- **File:** `e:\gh_COPILOT\databases\continuous_innovation.db`
- **Tables:** 5
- **Purpose:** Specialized data management

### Factory Deployment Database

- **File:** `e:\gh_COPILOT\databases\factory_deployment.db`
- **Tables:** 4
- **Purpose:** Specialized data management

### Learning Monitor Database

- **File:** `e:\gh_COPILOT\databases\learning_monitor.db`
- **Tables:** 25
- **Purpose:** Primary learning and monitoring

### Performance Analysis Database

- **File:** `e:\gh_COPILOT\databases\performance_analysis.db`
- **Tables:** 5
- **Purpose:** Specialized data management

### Production Database

- **File:** `e:\gh_COPILOT\databases\production.db`
- **Tables:** 44
- **Purpose:** Specialized data management

### Scaling Innovation Database

- **File:** `e:\gh_COPILOT\databases\scaling_innovation.db`
- **Tables:** 6
- **Purpose:** Specialized data management

## Table Documentation

### Analytics Collector Database Tables

#### analytics_data_points

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| timestamp | TEXT | NOT NULL | - |
| source | TEXT | NOT NULL | - |
| category | TEXT | NOT NULL | - |
| metric_name | TEXT | NOT NULL | - |
| metric_value | TEXT | NOT NULL | - |
| metadata | TEXT | NOT NULL | - |
| quality_score | REAL | NOT NULL | - |
| validation_status | TEXT | NOT NULL | - |
| session_id | TEXT | NOT NULL | - |

#### sqlite_sequence

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| name |  |  | - |
| seq |  |  | - |

#### analytics_sessions

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| session_id | TEXT | NOT NULL | - |
| start_time | TEXT | NOT NULL | - |
| end_time | TEXT |  | - |
| total_data_points | INTEGER | DEFAULT 0 | - |
| data_sources | TEXT | NOT NULL | - |
| categories_processed | TEXT | NOT NULL | - |
| status | TEXT | DEFAULT 'active' | - |
| quality_metrics | TEXT | NOT NULL | - |

**Indexes:**

- `sqlite_autoindex_analytics_sessions_1`

#### data_aggregations

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| aggregation_timestamp | TEXT | NOT NULL | - |
| source | TEXT | NOT NULL | - |
| category | TEXT | NOT NULL | - |
| metric_name | TEXT | NOT NULL | - |
| aggregation_type | TEXT | NOT NULL | - |
| aggregated_value | REAL | NOT NULL | - |
| data_point_count | INTEGER | NOT NULL | - |
| time_window_hours | REAL | NOT NULL | - |

### Capability Scaler Database Tables

#### scaling_capabilities

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| capability_id | TEXT | NOT NULL | - |
| capability_name | TEXT | NOT NULL | - |
| current_level | INTEGER | NOT NULL | - |
| target_level | INTEGER | NOT NULL | - |
| scaling_factor | REAL | NOT NULL | - |
| resource_requirements | TEXT | NOT NULL | - |
| performance_impact | REAL | NOT NULL | - |
| implementation_status | TEXT | NOT NULL | - |
| timestamp | TEXT | NOT NULL | - |

**Indexes:**

- `sqlite_autoindex_scaling_capabilities_1`

#### sqlite_sequence

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| name |  |  | - |
| seq |  |  | - |

#### scaling_sessions

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| session_id | TEXT | NOT NULL | - |
| start_time | TEXT | NOT NULL | - |
| end_time | TEXT |  | - |
| capabilities_scaled | TEXT | NOT NULL | - |
| total_scaling_operations | INTEGER | DEFAULT 0 | - |
| success_rate | REAL | DEFAULT 0.0 | - |
| performance_improvement | REAL | DEFAULT 0.0 | - |
| resource_utilization | TEXT | NOT NULL | - |
| status | TEXT | DEFAULT 'active' | - |

**Indexes:**

- `sqlite_autoindex_scaling_sessions_1`

#### scaling_operations

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| operation_id | TEXT | NOT NULL | - |
| session_id | TEXT | NOT NULL | - |
| capability_id | TEXT | NOT NULL | - |
| operation_type | TEXT | NOT NULL | - |
| start_time | TEXT | NOT NULL | - |
| end_time | TEXT |  | - |
| success | BOOLEAN | DEFAULT FALSE | - |
| performance_impact | REAL | DEFAULT 0.0 | - |
| resource_usage | TEXT | NOT NULL | - |
| error_message | TEXT |  | - |
| status | TEXT | DEFAULT 'pending' | - |

**Indexes:**

- `sqlite_autoindex_scaling_operations_1`

#### scaling_metrics

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| timestamp | TEXT | NOT NULL | - |
| session_id | TEXT | NOT NULL | - |
| metric_name | TEXT | NOT NULL | - |
| metric_value | REAL | NOT NULL | - |
| metric_type | TEXT | NOT NULL | - |
| capability_id | TEXT | NOT NULL | - |

### Continuous Innovation Database Tables

#### innovations

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| innovation_id | TEXT | NOT NULL | - |
| innovation_type | TEXT | NOT NULL | - |
| description | TEXT | NOT NULL | - |
| performance_impact | REAL | NOT NULL | - |
| implementation_complexity | INTEGER | NOT NULL | - |
| resource_requirements | TEXT | NOT NULL | - |
| success_probability | REAL | NOT NULL | - |
| innovation_score | REAL | NOT NULL | - |
| timestamp | TEXT | NOT NULL | - |
| status | TEXT | NOT NULL | - |
| cycle_id | TEXT |  | - |

**Indexes:**

- `sqlite_autoindex_innovations_1`

#### sqlite_sequence

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| name |  |  | - |
| seq |  |  | - |

#### innovation_cycles

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| cycle_id | TEXT | NOT NULL | - |
| start_time | TEXT | NOT NULL | - |
| end_time | TEXT |  | - |
| innovations_generated | INTEGER | DEFAULT 0 | - |
| innovations_implemented | INTEGER | DEFAULT 0 | - |
| cycle_performance_gain | REAL | DEFAULT 0.0 | - |
| learning_insights | TEXT | NOT NULL | - |
| optimization_patterns | TEXT | NOT NULL | - |
| status | TEXT | DEFAULT 'active' | - |

**Indexes:**

- `sqlite_autoindex_innovation_cycles_1`

#### learning_patterns

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| pattern_id | TEXT | NOT NULL | - |
| pattern_type | TEXT | NOT NULL | - |
| pattern_data | TEXT | NOT NULL | - |
| effectiveness_score | REAL | NOT NULL | - |
| usage_count | INTEGER | DEFAULT 0 | - |
| last_used | TEXT | NOT NULL | - |
| created_timestamp | TEXT | NOT NULL | - |

**Indexes:**

- `sqlite_autoindex_learning_patterns_1`

#### innovation_metrics

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| timestamp | TEXT | NOT NULL | - |
| cycle_id | TEXT | NOT NULL | - |
| metric_name | TEXT | NOT NULL | - |
| metric_value | REAL | NOT NULL | - |
| metric_type | TEXT | NOT NULL | - |

### Factory Deployment Database Tables

#### deployment_sessions

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| deployment_id | TEXT | NOT NULL | - |
| start_time | TEXT | NOT NULL | - |
| end_time | TEXT |  | - |
| status | TEXT | DEFAULT 'in_progress' | - |
| workspace_path | TEXT | NOT NULL | - |
| phases_completed | INTEGER | DEFAULT 0 | - |
| total_phases | INTEGER | DEFAULT 5 | - |
| success_rate | REAL | DEFAULT 0.0 | - |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | - |

**Indexes:**

- `sqlite_autoindex_deployment_sessions_1`

#### sqlite_sequence

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| name |  |  | - |
| seq |  |  | - |

#### factory_validation

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| deployment_id | TEXT | NOT NULL | - |
| validation_type | TEXT | NOT NULL | - |
| validation_result | TEXT | NOT NULL | - |
| files_checked | INTEGER | DEFAULT 0 | - |
| violations_found | INTEGER | DEFAULT 0 | - |
| compliance_score | REAL | DEFAULT 0.0 | - |
| timestamp | TEXT | NOT NULL | - |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | - |

#### cleanup_actions

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| deployment_id | TEXT | NOT NULL | - |
| action_type | TEXT | NOT NULL | - |
| target_path | TEXT | NOT NULL | - |
| action_result | TEXT | NOT NULL | - |
| files_affected | INTEGER | DEFAULT 0 | - |
| timestamp | TEXT | NOT NULL | - |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | - |

### Learning Monitor Database Tables

#### learning_metrics

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| timestamp | TEXT | NOT NULL | - |
| pattern_id | TEXT | NOT NULL | - |
| effectiveness_score | REAL | NOT NULL | - |
| learning_rate | REAL | NOT NULL | - |
| adaptation_speed | REAL | NOT NULL | - |
| resource_usage | TEXT | NOT NULL | - |
| performance_indicators | TEXT | NOT NULL | - |
| validation_status | TEXT | NOT NULL | - |

#### sqlite_sequence

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| name |  |  | - |
| seq |  |  | - |

#### monitoring_sessions

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| session_id | TEXT | NOT NULL | - |
| start_time | TEXT | NOT NULL | - |
| end_time | TEXT |  | - |
| total_patterns_monitored | INTEGER | DEFAULT 0 | - |
| average_effectiveness | REAL | DEFAULT 0.0 | - |
| alerts_generated | INTEGER | DEFAULT 0 | - |
| status | TEXT | DEFAULT 'active' | - |

**Indexes:**

- `sqlite_autoindex_monitoring_sessions_1`

#### monitoring_alerts

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| timestamp | TEXT | NOT NULL | - |
| session_id | TEXT | NOT NULL | - |
| alert_type | TEXT | NOT NULL | - |
| pattern_id | TEXT | NOT NULL | - |
| severity | TEXT | NOT NULL | - |
| message | TEXT | NOT NULL | - |
| resolved | BOOLEAN | DEFAULT FALSE | - |

#### enhanced_scripts

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| name | TEXT | NOT NULL | - |
| content | TEXT | NOT NULL | - |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| environment | TEXT | DEFAULT 'development' | - |
| version | TEXT | DEFAULT '1.0.0' | - |
| tags | TEXT | DEFAULT '[]' | - |
| category | TEXT | DEFAULT 'general' | - |
| author | TEXT | DEFAULT 'system' | - |
| description | TEXT | DEFAULT '' | - |
| dependencies | TEXT | DEFAULT '[]' | - |
| file_hash | TEXT |  | - |
| status | TEXT | DEFAULT 'active' | - |
| usage_count | INTEGER | DEFAULT 0 | - |
| last_used | TIMESTAMP |  | - |
| performance_metrics | TEXT | DEFAULT '{}' | - |

**Indexes:**

- `sqlite_autoindex_enhanced_scripts_2`
- `sqlite_autoindex_enhanced_scripts_1`

#### enhanced_templates

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| name | TEXT | NOT NULL | - |
| content | TEXT | NOT NULL | - |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| environment | TEXT | DEFAULT 'all' | - |
| version | TEXT | DEFAULT '1.0.0' | - |
| tags | TEXT | DEFAULT '[]' | - |
| category | TEXT | DEFAULT 'general' | - |
| template_type | TEXT | DEFAULT 'script' | - |
| author | TEXT | DEFAULT 'system' | - |
| description | TEXT | DEFAULT '' | - |
| variables | TEXT | DEFAULT '[]' | - |
| adaptation_rules | TEXT | DEFAULT '[]' | - |
| success_rate | REAL | DEFAULT 1.0 | - |
| usage_count | INTEGER | DEFAULT 0 | - |
| last_used | TIMESTAMP |  | - |
| parent_template_id | INTEGER |  | - |
| status | TEXT | DEFAULT 'active' | - |

**Foreign Keys:**

- `parent_template_id` → `enhanced_templates.id`

**Indexes:**

- `sqlite_autoindex_enhanced_templates_1`

#### enhanced_logs

**Type:** Logging  
**Description:** Enhanced system logging and monitoring

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| action | TEXT | NOT NULL | - |
| details | TEXT | DEFAULT '' | - |
| timestamp | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| environment | TEXT | DEFAULT 'development' | - |
| session_id | TEXT |  | - |
| user_id | TEXT | DEFAULT 'system' | - |
| log_level | TEXT | DEFAULT 'INFO' | - |
| component | TEXT | DEFAULT 'platform' | - |
| context_data | TEXT | DEFAULT '{}' | - |
| correlation_id | TEXT |  | - |
| duration_ms | INTEGER |  | - |
| success | BOOLEAN | DEFAULT 1 | - |
| error_message | TEXT |  | - |
| stack_trace | TEXT |  | - |

#### enhanced_lessons_learned

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| description | TEXT | NOT NULL | - |
| source | TEXT | NOT NULL | - |
| timestamp | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| environment | TEXT | DEFAULT 'all' | - |
| lesson_type | TEXT | DEFAULT 'improvement' | - |
| category | TEXT | DEFAULT 'general' | - |
| impact_level | TEXT | DEFAULT 'medium' | - |
| confidence_score | REAL | DEFAULT 0.8 | - |
| validation_status | TEXT | DEFAULT 'pending' | - |
| applied_count | INTEGER | DEFAULT 0 | - |
| success_rate | REAL | DEFAULT 0.0 | - |
| tags | TEXT | DEFAULT '[]' | - |
| context_data | TEXT | DEFAULT '{}' | - |
| related_scripts | TEXT | DEFAULT '[]' | - |
| related_templates | TEXT | DEFAULT '[]' | - |
| created_by | TEXT | DEFAULT 'system' | - |
| validated_by | TEXT |  | - |
| validation_timestamp | TIMESTAMP |  | - |

#### template_versions

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| template_id | INTEGER | NOT NULL | - |
| version | TEXT | NOT NULL | - |
| content | TEXT | NOT NULL | - |
| changelog | TEXT | DEFAULT '' | - |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| created_by | TEXT | DEFAULT 'system' | - |
| is_current | BOOLEAN | DEFAULT 0 | - |
| migration_notes | TEXT | DEFAULT '' | - |

**Foreign Keys:**

- `template_id` → `enhanced_templates.id`

**Indexes:**

- `sqlite_autoindex_template_versions_1`

#### environment_adaptations

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| source_template_id | INTEGER | NOT NULL | - |
| target_environment | TEXT | NOT NULL | - |
| adaptation_rules | TEXT | DEFAULT '[]' | - |
| success_rate | REAL | DEFAULT 1.0 | - |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| last_applied | TIMESTAMP |  | - |
| application_count | INTEGER | DEFAULT 0 | - |
| performance_impact | TEXT | DEFAULT '{}' | - |

**Foreign Keys:**

- `source_template_id` → `enhanced_templates.id`

**Indexes:**

- `sqlite_autoindex_environment_adaptations_1`

#### cross_database_references

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| source_database | TEXT | NOT NULL | - |
| source_table | TEXT | NOT NULL | - |
| source_id | TEXT | NOT NULL | - |
| target_database | TEXT | NOT NULL | - |
| target_table | TEXT | NOT NULL | - |
| target_id | TEXT | NOT NULL | - |
| relationship_type | TEXT | DEFAULT 'reference' | - |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| metadata | TEXT | DEFAULT '{}' | - |

#### template_placeholders

**Type:** Core  
**Description:** Template placeholder definitions and configurations

Entries in this table define allowed placeholders for all templates. Each
placeholder type includes an optional validation pattern and default value.
Usage statistics are aggregated in `template_usage_analytics`.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| placeholder_type | TEXT | NOT NULL | - |
| default_value | TEXT |  | - |
| description | TEXT | NOT NULL | - |
| validation_pattern | TEXT |  | - |
| environments | TEXT |  | - |
| usage_count | INTEGER | DEFAULT 0 | - |
| effectiveness_score | REAL | DEFAULT 0.0 | - |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |

**Indexes:**

- `idx_placeholders_type`
- `sqlite_autoindex_template_placeholders_1`

#### code_pattern_analysis

**Type:** Analysis  
**Description:** Code pattern analysis results and insights

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| analysis_id | TEXT | NOT NULL | - |
| source_file | TEXT | NOT NULL | - |
| pattern_type | TEXT | NOT NULL | - |
| pattern_content | TEXT | NOT NULL | - |
| confidence_score | REAL | DEFAULT 0.0 | - |
| frequency_count | INTEGER | DEFAULT 1 | - |
| analysis_timestamp | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| environment_context | TEXT |  | - |

**Foreign Keys:**

- `analysis_id` → `enhanced_logs.id`

**Indexes:**

- `idx_patterns_type`
- `idx_pattern_type`
- `sqlite_autoindex_code_pattern_analysis_1`

#### template_intelligence

**Type:** Core  
**Description:** Template intelligence insights and recommendations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| intelligence_id | TEXT | NOT NULL | - |
| template_id | TEXT | NOT NULL | - |
| suggestion_type | TEXT | NOT NULL | - |
| suggestion_content | TEXT | NOT NULL | - |
| confidence_score | REAL | DEFAULT 0.0 | - |
| usage_context | TEXT |  | - |
| success_rate | REAL | DEFAULT 0.0 | - |
| user_feedback_score | REAL | DEFAULT 0.0 | - |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| last_used | TIMESTAMP |  | - |
| intelligence_type | TEXT | DEFAULT 'code_analysis' | - |
| intelligence_data | TEXT |  | - |
| source_analysis | TEXT |  | - |

**Foreign Keys:**

- `template_id` → `enhanced_templates.id`

**Indexes:**

- `idx_intelligence_template`
- `sqlite_autoindex_template_intelligence_1`

#### cross_database_template_mapping

**Type:** Integration  
**Description:** Cross-database template mapping relationships

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| mapping_id | TEXT | NOT NULL | - |
| source_database | TEXT | NOT NULL | - |
| source_table | TEXT | NOT NULL | - |
| source_template_id | TEXT |  | - |
| target_database | TEXT | NOT NULL | - |
| target_table | TEXT | NOT NULL | - |
| target_template_id | TEXT |  | - |
| mapping_type | TEXT | NOT NULL | - |
| mapping_rules | TEXT |  | - |
| sync_status | TEXT | DEFAULT 'active' | - |
| last_sync | TIMESTAMP |  | - |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |

**Indexes:**

- `idx_mapping_source`
- `sqlite_autoindex_cross_database_template_mapping_1`

#### template_usage_analytics

**Type:** Analytics
**Description:** Records template usage metrics

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| usage_id | TEXT | NOT NULL | - |
| template_id | TEXT |  | - |
| environment | TEXT |  | - |
| usage_context | TEXT |  | - |
| substitution_value | TEXT |  | - |
| success | BOOLEAN | DEFAULT 1 | - |
| performance_ms | INTEGER |  | - |
| user_satisfaction | INTEGER |  | - |
| usage_timestamp | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |

**Foreign Keys:**

- `template_id` → `enhanced_templates.id`

**Indexes:**

- `idx_usage_template`
- `sqlite_autoindex_template_usage_analytics_1`

#### environment_adaptation_intelligence

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| adaptation_id | TEXT | NOT NULL | - |
| source_environment | TEXT | NOT NULL | - |
| target_environment | TEXT | NOT NULL | - |
| adaptation_type | TEXT | NOT NULL | - |
| adaptation_pattern | TEXT | NOT NULL | - |
| success_rate | REAL | DEFAULT 0.0 | - |
| performance_impact | REAL | DEFAULT 0.0 | - |
| learning_data | TEXT |  | - |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| last_applied | TIMESTAMP |  | - |

**Indexes:**

- `idx_adaptation_environments`
- `sqlite_autoindex_environment_adaptation_intelligence_1`

#### environment_variables

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| variable_id | INTEGER | PRIMARY KEY | - |
| profile_id | INTEGER |  | - |
| variable_name | TEXT | NOT NULL | - |
| variable_value | TEXT |  | - |
| variable_type | TEXT | DEFAULT 'string' | - |
| description | TEXT |  | - |
| is_secure | BOOLEAN | DEFAULT FALSE | - |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |

**Foreign Keys:**

- `profile_id` → `environment_profiles.profile_id`

#### integration_points

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| integration_id | INTEGER | PRIMARY KEY | - |
| profile_id | INTEGER |  | - |
| integration_type | TEXT | NOT NULL | - |
| target_system | TEXT | NOT NULL | - |
| configuration | TEXT |  | - |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |

**Foreign Keys:**

- `profile_id` → `environment_profiles.profile_id`

#### environment_specific_templates

**Type:** Environment  
**Description:** Environment-specific template adaptations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| base_template_id | TEXT | NOT NULL | - |
| environment_name | TEXT | NOT NULL | - |
| template_content | TEXT | NOT NULL | - |
| adaptation_rules | TEXT |  | - |
| performance_metrics | TEXT |  | - |
| success_rate | REAL |  | - |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | - |
| updated_at | TEXT | DEFAULT CURRENT_TIMESTAMP | - |

**Indexes:**

- `idx_env_templates_env`
- `sqlite_autoindex_environment_specific_templates_1`

#### cross_database_aggregation_results

**Type:** Integration  
**Description:** Cross-database aggregation results

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| aggregation_id | TEXT | NOT NULL | - |
| aggregation_timestamp | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| databases_involved | TEXT | NOT NULL | - |
| aggregation_type | TEXT | NOT NULL | - |
| results_data | TEXT | NOT NULL | - |
| confidence_score | REAL | DEFAULT 0.0 | - |
| insights_generated | INTEGER | DEFAULT 0 | - |

**Indexes:**

- `sqlite_autoindex_cross_database_aggregation_results_1`

#### environment_profiles

**Type:** Environment  
**Description:** Environment profile configurations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| profile_id | TEXT | NOT NULL | - |
| profile_name | TEXT | NOT NULL | - |
| environment_type | TEXT | NOT NULL | - |
| characteristics | TEXT | NOT NULL | - |
| adaptation_rules | TEXT | NOT NULL | - |
| template_preferences | TEXT | NOT NULL | - |
| priority | INTEGER | DEFAULT 0 | - |
| active | BOOLEAN | DEFAULT 1 | - |
| created_timestamp | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| modified_timestamp | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |

**Indexes:**

- `sqlite_autoindex_environment_profiles_1`

#### adaptation_rules

**Type:** Environment  
**Description:** Dynamic template adaptation rules

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| rule_id | TEXT | NOT NULL | - |
| rule_name | TEXT | NOT NULL | - |
| environment_context | TEXT | NOT NULL | - |
| condition_pattern | TEXT | NOT NULL | - |
| adaptation_action | TEXT | NOT NULL | - |
| template_modifications | TEXT | NOT NULL | - |
| confidence_threshold | REAL | DEFAULT 0.8 | - |
| execution_priority | INTEGER | DEFAULT 0 | - |
| active | BOOLEAN | DEFAULT 1 | - |
| created_timestamp | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |

**Indexes:**

- `sqlite_autoindex_adaptation_rules_1`

#### environment_context_history

**Type:** Environment  
**Description:** Historical environment context data

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| context_id | TEXT | NOT NULL | - |
| timestamp | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| environment_type | TEXT | NOT NULL | - |
| system_info | TEXT | NOT NULL | - |
| workspace_context | TEXT | NOT NULL | - |
| active_profiles | TEXT | NOT NULL | - |
| applicable_rules | TEXT | NOT NULL | - |
| adaptation_results | TEXT |  | - |

**Indexes:**

- `sqlite_autoindex_environment_context_history_1`

#### template_adaptation_logs

**Type:** Logging  
**Description:** Template adaptation execution logs

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| adaptation_id | TEXT | NOT NULL | - |
| timestamp | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| source_template | TEXT | NOT NULL | - |
| target_environment | TEXT | NOT NULL | - |
| applied_rules | TEXT | NOT NULL | - |
| adaptation_changes | TEXT | NOT NULL | - |
| success_rate | REAL | DEFAULT 0.0 | - |
| performance_impact | TEXT |  | - |

**Indexes:**

- `sqlite_autoindex_template_adaptation_logs_1`

### Performance Analysis Database Tables

#### performance_metrics

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| timestamp | TEXT | NOT NULL | - |
| metric_name | TEXT | NOT NULL | - |
| current_value | REAL | NOT NULL | - |
| baseline_value | REAL | NOT NULL | - |
| performance_score | REAL | NOT NULL | - |
| trend_direction | TEXT | NOT NULL | - |
| confidence_level | REAL | NOT NULL | - |
| analysis_metadata | TEXT | NOT NULL | - |
| session_id | TEXT | NOT NULL | - |

#### sqlite_sequence

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| name |  |  | - |
| seq |  |  | - |

#### analysis_sessions

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| session_id | TEXT | NOT NULL | - |
| start_time | TEXT | NOT NULL | - |
| end_time | TEXT |  | - |
| metrics_analyzed | INTEGER | DEFAULT 0 | - |
| optimization_opportunities | TEXT | NOT NULL | - |
| performance_grade | TEXT | DEFAULT 'unknown' | - |
| recommendations | TEXT | NOT NULL | - |
| status | TEXT | DEFAULT 'active' | - |

**Indexes:**

- `sqlite_autoindex_analysis_sessions_1`

#### baseline_metrics

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| metric_name | TEXT | NOT NULL | - |
| baseline_value | REAL | NOT NULL | - |
| calculation_method | TEXT | NOT NULL | - |
| data_points_used | INTEGER | NOT NULL | - |
| confidence_score | REAL | NOT NULL | - |
| last_updated | TEXT | NOT NULL | - |

**Indexes:**

- `sqlite_autoindex_baseline_metrics_1`

#### optimization_recommendations

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| timestamp | TEXT | NOT NULL | - |
| session_id | TEXT | NOT NULL | - |
| metric_name | TEXT | NOT NULL | - |
| recommendation_type | TEXT | NOT NULL | - |
| description | TEXT | NOT NULL | - |
| expected_improvement | REAL | NOT NULL | - |
| implementation_priority | TEXT | NOT NULL | - |
| status | TEXT | DEFAULT 'pending' | - |

### Production Database Tables

#### file_system_mapping

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| file_path | TEXT | NOT NULL | - |
| file_hash | TEXT |  | - |
| file_size | INTEGER |  | - |
| last_modified | TIMESTAMP |  | - |
| status | TEXT | DEFAULT 'active' | - |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| file_content | TEXT |  | - |
| file_type | TEXT |  | - |
| backup_location | TEXT |  | - |
| compression_type | TEXT |  | - |
| encoding | TEXT | DEFAULT "utf-8" | - |

**Indexes:**

- `idx_file_system_status`
- `idx_file_mapping_status`
- `idx_file_mapping_path`
- `sqlite_autoindex_file_system_mapping_1`

#### sqlite_sequence

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| name |  |  | - |
| seq |  |  | - |

#### validation_sessions

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| session_id | TEXT | NOT NULL | - |
| start_time | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| end_time | TIMESTAMP |  | - |
| status | TEXT | DEFAULT 'active' | - |
| results | TEXT |  | - |

**Indexes:**

- `idx_validation_session`
- `sqlite_autoindex_validation_sessions_1`

#### github_sessions

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| session_id | TEXT | NOT NULL | - |
| start_time | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| end_time | TIMESTAMP |  | - |
| objective | TEXT |  | - |
| status | TEXT | DEFAULT 'active' | - |
| chunks_completed | INTEGER | DEFAULT 0 | - |

**Indexes:**

- `idx_github_session`
- `sqlite_autoindex_github_sessions_1`

#### system_info

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| key | TEXT | NOT NULL | - |
| value | TEXT |  | - |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |

**Indexes:**

- `idx_system_info_key`
- `sqlite_autoindex_system_info_1`

#### log_correlation_results

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| analysis_timestamp | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| total_files_analyzed | INTEGER |  | - |
| total_events_found | INTEGER |  | - |
| events_by_type | TEXT |  | - |
| error_patterns | TEXT |  | - |
| success_patterns | TEXT |  | - |
| compliance_events | TEXT |  | - |
| performance_metrics | TEXT |  | - |
| anomalies | TEXT |  | - |
| execution_time | REAL |  | - |

#### compliance_events

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| event_type | TEXT | NOT NULL | - |
| event_category | TEXT | NOT NULL | - |
| description | TEXT | NOT NULL | - |
| severity | TEXT | DEFAULT 'INFO' | - |
| timestamp | TEXT | NOT NULL | - |
| source_file | TEXT |  | - |
| compliance_score | REAL | DEFAULT 100.0 | - |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | - |

#### enhanced_compliance_tracking

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| check_timestamp | TEXT | NOT NULL | - |
| check_type | TEXT | NOT NULL | - |
| status | TEXT | NOT NULL | - |
| details | TEXT |  | - |
| compliance_score | REAL |  | - |
| dual_copilot_validation | BOOLEAN | DEFAULT TRUE | - |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | - |

#### copilot_learning_events

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| event_id | TEXT | PRIMARY KEY | - |
| session_id | TEXT | NOT NULL | - |
| event_type | TEXT | NOT NULL | - |
| event_category | TEXT | NOT NULL | - |
| timestamp | DATETIME | DEFAULT CURRENT_TIMESTAMP | - |
| component | TEXT |  | - |
| file_path | TEXT |  | - |
| function_name | TEXT |  | - |
| line_number | INTEGER |  | - |
| action_taken | TEXT | NOT NULL | - |
| reasoning | TEXT |  | - |
| confidence_score | REAL | DEFAULT 0.0 | - |
| outcome | TEXT |  | - |
| effectiveness_score | REAL |  | - |
| user_feedback | TEXT |  | - |
| pattern_ids | TEXT |  | - |
| similar_events | TEXT |  | - |
| learning_weight | REAL | DEFAULT 1.0 | - |
| response_time_ms | INTEGER |  | - |
| tokens_processed | INTEGER |  | - |
| memory_usage_mb | REAL |  | - |
| context_data | TEXT |  | - |
| tags | TEXT |  | - |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | - |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | - |

**Foreign Keys:**

- `session_id` → `copilot_sessions.session_id`

**Indexes:**

- `idx_learning_events_outcome`
- `idx_learning_events_component`
- `idx_learning_events_timestamp`
- `idx_learning_events_type`
- `idx_learning_events_session`
- `sqlite_autoindex_copilot_learning_events_1`

#### error_patterns

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| pattern_id | TEXT | PRIMARY KEY | - |
| error_type | TEXT | NOT NULL | - |
| error_category | TEXT | NOT NULL | - |
| error_signature | TEXT | NOT NULL | - |
| error_message_pattern | TEXT |  | - |
| error_context_pattern | TEXT |  | - |
| first_seen | DATETIME | NOT NULL | - |
| last_seen | DATETIME | DEFAULT CURRENT_TIMESTAMP | - |
| occurrence_count | INTEGER | DEFAULT 1 | - |
| typical_solutions | TEXT | NOT NULL | - |
| resolution_success_rate | REAL | DEFAULT 0.0 | - |
| average_resolution_time_minutes | REAL |  | - |
| common_triggers | TEXT |  | - |
| prevention_strategies | TEXT |  | - |
| related_components | TEXT |  | - |
| learning_priority | INTEGER | DEFAULT 1 | - |
| pattern_confidence | REAL | DEFAULT 0.0 | - |
| severity_level | TEXT | DEFAULT 'medium' | - |
| performance_impact | TEXT |  | - |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | - |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | - |

**Indexes:**

- `idx_error_patterns_severity`
- `idx_error_patterns_occurrence`
- `idx_error_patterns_signature`
- `idx_error_patterns_type`
- `sqlite_autoindex_error_patterns_1`

#### change_tracking

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| change_id | TEXT | PRIMARY KEY | - |
| session_id | TEXT |  | - |
| event_id | TEXT |  | - |
| change_type | TEXT | NOT NULL | - |
| change_scope | TEXT | NOT NULL | - |
| change_category | TEXT |  | - |
| file_path | TEXT | NOT NULL | - |
| file_type | TEXT |  | - |
| lines_added | INTEGER | DEFAULT 0 | - |
| lines_removed | INTEGER | DEFAULT 0 | - |
| lines_modified | INTEGER | DEFAULT 0 | - |
| complexity_delta | REAL |  | - |
| before_content | TEXT |  | - |
| after_content | TEXT |  | - |
| diff_content | TEXT |  | - |
| affected_functions | TEXT |  | - |
| affected_components | TEXT |  | - |
| breaking_change | BOOLEAN | DEFAULT FALSE | - |
| code_quality_score_before | REAL |  | - |
| code_quality_score_after | REAL |  | - |
| test_coverage_before | REAL |  | - |
| test_coverage_after | REAL |  | - |
| change_effectiveness | REAL |  | - |
| side_effects | TEXT |  | - |
| rollback_required | BOOLEAN | DEFAULT FALSE | - |
| triggered_by | TEXT |  | - |
| learning_value | REAL | DEFAULT 1.0 | - |
| timestamp | DATETIME | DEFAULT CURRENT_TIMESTAMP | - |

**Foreign Keys:**

- `event_id` → `copilot_learning_events.event_id`
- `session_id` → `copilot_sessions.session_id`

**Indexes:**

- `idx_change_tracking_timestamp`
- `idx_change_tracking_type`
- `idx_change_tracking_file`
- `idx_change_tracking_session`
- `sqlite_autoindex_change_tracking_1`

#### todo_fixme_tracking

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| item_id | TEXT | PRIMARY KEY | - |
| session_id | TEXT |  | - |
| item_type | TEXT | NOT NULL | - |
| priority_level | TEXT | DEFAULT 'medium' | - |
| category | TEXT |  | - |
| file_path | TEXT | NOT NULL | - |
| line_number | INTEGER | NOT NULL | - |
| function_context | TEXT |  | - |
| class_context | TEXT |  | - |
| original_text | TEXT | NOT NULL | - |
| description | TEXT |  | - |
| estimated_effort | TEXT |  | - |
| status | TEXT | DEFAULT 'open' | - |
| assigned_to | TEXT |  | - |
| created_date | DATETIME | DEFAULT CURRENT_TIMESTAMP | - |
| resolved_date | DATETIME |  | - |
| resolution_method | TEXT |  | - |
| resolution_code_changes | TEXT |  | - |
| resolution_effectiveness | REAL |  | - |
| similar_items | TEXT |  | - |
| common_patterns | TEXT |  | - |
| root_cause | TEXT |  | - |
| business_impact | TEXT |  | - |
| technical_debt_score | REAL |  | - |
| urgency_score | REAL |  | - |
| learning_insights | TEXT |  | - |
| prevention_strategies | TEXT |  | - |
| last_updated | DATETIME | DEFAULT CURRENT_TIMESTAMP | - |

**Foreign Keys:**

- `session_id` → `copilot_sessions.session_id`

**Indexes:**

- `idx_todo_fixme_type`
- `idx_todo_fixme_file`
- `idx_todo_fixme_priority`
- `idx_todo_fixme_status`
- `sqlite_autoindex_todo_fixme_tracking_1`

#### feedback_loops

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| feedback_id | TEXT | PRIMARY KEY | - |
| loop_type | TEXT | NOT NULL | - |
| source_event_id | TEXT |  | - |
| source_component | TEXT |  | - |
| source_session_id | TEXT |  | - |
| feedback_type | TEXT | NOT NULL | - |
| feedback_content | TEXT | NOT NULL | - |
| feedback_score | REAL |  | - |
| context_data | TEXT |  | - |
| environment_info | TEXT |  | - |
| user_persona | TEXT |  | - |
| processed | BOOLEAN | DEFAULT FALSE | - |
| processing_result | TEXT |  | - |
| processing_effectiveness | REAL |  | - |
| learning_applied | BOOLEAN | DEFAULT FALSE | - |
| learning_changes | TEXT |  | - |
| improvement_metrics | TEXT |  | - |
| feedback_timestamp | DATETIME | DEFAULT CURRENT_TIMESTAMP | - |
| processed_timestamp | DATETIME |  | - |
| applied_timestamp | DATETIME |  | - |
| feedback_validity | REAL | DEFAULT 1.0 | - |
| confidence_level | REAL | DEFAULT 0.5 | - |

**Foreign Keys:**

- `source_session_id` → `copilot_sessions.session_id`
- `source_event_id` → `copilot_learning_events.event_id`

**Indexes:**

- `idx_feedback_timestamp`
- `idx_feedback_processed`
- `idx_feedback_type`
- `sqlite_autoindex_feedback_loops_1`

#### pattern_effectiveness

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| effectiveness_id | TEXT | PRIMARY KEY | - |
| pattern_id | TEXT | NOT NULL | - |
| pattern_type | TEXT | NOT NULL | - |
| total_applications | INTEGER | DEFAULT 0 | - |
| successful_applications | INTEGER | DEFAULT 0 | - |
| failed_applications | INTEGER | DEFAULT 0 | - |
| average_success_rate | REAL | DEFAULT 0.0 | - |
| average_response_time_ms | REAL |  | - |
| average_user_satisfaction | REAL |  | - |
| most_effective_contexts | TEXT |  | - |
| least_effective_contexts | TEXT |  | - |
| optimal_conditions | TEXT |  | - |
| performance_trend | TEXT |  | - |
| trend_data | TEXT |  | - |
| better_alternatives | TEXT |  | - |
| complementary_patterns | TEXT |  | - |
| key_success_factors | TEXT |  | - |
| common_failure_modes | TEXT |  | - |
| improvement_opportunities | TEXT |  | - |
| recommendation_score | REAL | DEFAULT 0.5 | - |
| recommendation_contexts | TEXT |  | - |
| first_measurement | DATETIME | DEFAULT CURRENT_TIMESTAMP | - |
| last_updated | DATETIME | DEFAULT CURRENT_TIMESTAMP | - |
| measurement_count | INTEGER | DEFAULT 0 | - |
| data_quality_score | REAL | DEFAULT 1.0 | - |
| statistical_confidence | REAL | DEFAULT 0.0 | - |

**Foreign Keys:**

- `pattern_id` → `pattern_database.pattern_id`

**Indexes:**

- `idx_pattern_effectiveness_updated`
- `idx_pattern_effectiveness_success`
- `idx_pattern_effectiveness_pattern`
- `sqlite_autoindex_pattern_effectiveness_1`

#### copilot_decision_tree

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| decision_id | TEXT | PRIMARY KEY | - |
| parent_decision_id | TEXT |  | - |
| event_id | TEXT | NOT NULL | - |
| decision_point | TEXT | NOT NULL | - |
| available_options | TEXT | NOT NULL | - |
| chosen_option | TEXT | NOT NULL | - |
| evaluation_criteria | TEXT |  | - |
| option_scores | TEXT |  | - |
| decision_algorithm | TEXT |  | - |
| decision_confidence | REAL | NOT NULL | - |
| uncertainty_factors | TEXT |  | - |
| risk_assessment | TEXT |  | - |
| expected_outcome | TEXT |  | - |
| actual_outcome | TEXT |  | - |
| outcome_match_score | REAL |  | - |
| decision_quality | REAL |  | - |
| learning_insights | TEXT |  | - |
| would_decide_differently | TEXT |  | - |
| decision_timestamp | DATETIME | DEFAULT CURRENT_TIMESTAMP | - |
| outcome_timestamp | DATETIME |  | - |

**Foreign Keys:**

- `event_id` → `copilot_learning_events.event_id`
- `parent_decision_id` → `copilot_decision_tree.decision_id`

**Indexes:**

- `idx_decision_tree_confidence`
- `idx_decision_tree_parent`
- `idx_decision_tree_event`
- `sqlite_autoindex_copilot_decision_tree_1`

#### sqlite_stat1

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| tbl |  |  | - |
| idx |  |  | - |
| stat |  |  | - |

#### environment_configs

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| config_id | TEXT | PRIMARY KEY | - |
| environment_name | TEXT | NOT NULL | - |
| environment_type | TEXT | NOT NULL | - |
| configuration_data | TEXT | NOT NULL | - |
| deployment_patterns | TEXT |  | - |
| validation_rules | TEXT |  | - |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |

**Indexes:**

- `sqlite_autoindex_environment_configs_1`

#### template_effectiveness

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| effectiveness_id | TEXT | PRIMARY KEY | - |
| template_id | TEXT |  | - |
| usage_context | TEXT |  | - |
| success_rate | REAL | DEFAULT 0.0 | - |
| performance_metrics | TEXT |  | - |
| user_feedback | TEXT |  | - |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |

**Foreign Keys:**

- `template_id` → `script_templates.template_id`

**Indexes:**

- `sqlite_autoindex_template_effectiveness_1`

#### generation_history

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| generation_id | TEXT | PRIMARY KEY | - |
| template_id | TEXT |  | - |
| environment_id | TEXT |  | - |
| generated_content | TEXT |  | - |
| generation_parameters | TEXT |  | - |
| success_status | TEXT |  | - |
| execution_results | TEXT |  | - |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |

**Foreign Keys:**

- `template_id` → `script_templates.template_id`

**Indexes:**

- `sqlite_autoindex_generation_history_1`

#### codebase_analysis

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| analysis_id | TEXT | PRIMARY KEY | - |
| analysis_timestamp | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| total_scripts_analyzed | INTEGER |  | - |
| patterns_extracted | TEXT |  | - |
| dependency_graph | TEXT |  | - |
| complexity_metrics | TEXT |  | - |
| enterprise_compliance_score | REAL |  | - |
| analysis_metadata | TEXT |  | - |

**Indexes:**

- `sqlite_autoindex_codebase_analysis_1`

#### script_metadata

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| filepath | TEXT |  | - |
| filename | TEXT |  | - |
| size_bytes | INTEGER |  | - |
| lines_of_code | INTEGER |  | - |
| functions | TEXT |  | - |
| classes | TEXT |  | - |
| imports | TEXT |  | - |
| dependencies | TEXT |  | - |
| patterns | TEXT |  | - |
| database_connections | TEXT |  | - |
| complexity_score | INTEGER |  | - |
| last_modified | TEXT |  | - |
| category | TEXT |  | - |
| analysis_timestamp | TEXT |  | - |

**Indexes:**

- `sqlite_autoindex_script_metadata_1`

#### template_patterns

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| pattern_id | TEXT |  | - |
| pattern_type | TEXT |  | - |
| occurrence_count | INTEGER |  | - |
| files | TEXT |  | - |
| code_snippet | TEXT |  | - |
| variables | TEXT |  | - |
| description | TEXT |  | - |
| analysis_timestamp | TEXT |  | - |

**Indexes:**

- `sqlite_autoindex_template_patterns_1`

#### template_variables

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| template_id | INTEGER | NOT NULL | - |
| variable_name | TEXT | NOT NULL | - |
| variable_type | TEXT | NOT NULL | - |
| default_value | TEXT |  | - |
| description | TEXT |  | - |
| required | BOOLEAN | DEFAULT 0 | - |
| validation_pattern | TEXT |  | - |
| example_value | TEXT |  | - |

**Foreign Keys:**

- `template_id` → `script_templates.id`

#### template_dependencies

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| template_id | INTEGER | NOT NULL | - |
| dependency_type | TEXT | NOT NULL | - |
| dependency_name | TEXT | NOT NULL | - |
| version_requirement | TEXT |  | - |
| optional | BOOLEAN | DEFAULT 0 | - |
| description | TEXT |  | - |

**Foreign Keys:**

- `template_id` → `script_templates.id`

#### environment_profiles

**Type:** Environment  
**Description:** Environment profile configurations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| profile_name | TEXT | NOT NULL | - |
| description | TEXT |  | - |
| target_platform | TEXT |  | - |
| python_version | TEXT |  | - |
| enterprise_level | TEXT |  | - |
| compliance_requirements | TEXT |  | - |
| default_packages | TEXT |  | - |
| security_level | INTEGER | DEFAULT 1 | - |
| created_timestamp | TEXT | NOT NULL | - |
| active | BOOLEAN | DEFAULT 1 | - |

**Indexes:**

- `sqlite_autoindex_environment_profiles_1`

#### environment_variables

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| profile_id | INTEGER | NOT NULL | - |
| variable_name | TEXT | NOT NULL | - |
| variable_value | TEXT |  | - |
| variable_type | TEXT | DEFAULT 'string' | - |
| sensitive | BOOLEAN | DEFAULT 0 | - |
| description | TEXT |  | - |

**Foreign Keys:**

- `profile_id` → `environment_profiles.id`

#### environment_adaptations

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| source_template_id | INTEGER | NOT NULL | - |
| target_environment_id | INTEGER | NOT NULL | - |
| adaptation_rules | TEXT |  | - |
| success_rate | REAL | DEFAULT 0.0 | - |
| last_adaptation_timestamp | TEXT |  | - |

**Foreign Keys:**

- `target_environment_id` → `environment_profiles.id`
- `source_template_id` → `script_templates.id`

#### generation_sessions

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| session_id | TEXT | NOT NULL | - |
| user_prompt | TEXT | NOT NULL | - |
| template_used_id | INTEGER |  | - |
| environment_profile_id | INTEGER |  | - |
| generation_mode | TEXT |  | - |
| success | BOOLEAN | DEFAULT 0 | - |
| output_file_path | TEXT |  | - |
| generation_timestamp | TEXT | NOT NULL | - |
| completion_timestamp | TEXT |  | - |
| duration_seconds | REAL |  | - |

**Foreign Keys:**

- `environment_profile_id` → `environment_profiles.id`
- `template_used_id` → `script_templates.id`

**Indexes:**

- `sqlite_autoindex_generation_sessions_1`

#### generated_scripts

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| session_id | TEXT | NOT NULL | - |
| script_name | TEXT | NOT NULL | - |
| script_path | TEXT | NOT NULL | - |
| content_hash | TEXT |  | - |
| lines_of_code | INTEGER |  | - |
| functions_count | INTEGER |  | - |
| classes_count | INTEGER |  | - |
| complexity_score | INTEGER |  | - |
| validation_status | TEXT | DEFAULT 'pending' | - |
| execution_status | TEXT | DEFAULT 'not_tested' | - |
| file_size_bytes | INTEGER |  | - |

**Foreign Keys:**

- `session_id` → `generation_sessions.session_id`

**Indexes:**

- `sqlite_autoindex_generated_scripts_1`

#### generation_logs

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| session_id | TEXT | NOT NULL | - |
| log_level | TEXT | NOT NULL | - |
| message | TEXT | NOT NULL | - |
| timestamp | TEXT | NOT NULL | - |
| component | TEXT |  | - |
| details | TEXT |  | - |

**Foreign Keys:**

- `session_id` → `generation_sessions.session_id`

#### user_feedback

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| session_id | TEXT | NOT NULL | - |
| script_id | INTEGER |  | - |
| template_id | INTEGER |  | - |
| satisfaction_rating | INTEGER |  | - |
| quality_rating | INTEGER |  | - |
| usefulness_rating | INTEGER |  | - |
| feedback_text | TEXT |  | - |
| suggestions | TEXT |  | - |
| timestamp | TEXT | NOT NULL | - |

**Foreign Keys:**

- `template_id` → `script_templates.id`
- `script_id` → `generated_scripts.id`
- `session_id` → `generation_sessions.session_id`

#### performance_metrics

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| metric_type | TEXT | NOT NULL | - |
| metric_value | REAL | NOT NULL | - |
| session_id | TEXT |  | - |
| template_id | INTEGER |  | - |
| timestamp | TEXT | NOT NULL | - |
| context | TEXT |  | - |

**Foreign Keys:**

- `template_id` → `script_templates.id`
- `session_id` → `generation_sessions.session_id`

#### copilot_contexts

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| context_name | TEXT | NOT NULL | - |
| context_type | TEXT | NOT NULL | - |
| context_content | TEXT | NOT NULL | - |
| usage_instructions | TEXT |  | - |
| effectiveness_score | REAL | DEFAULT 0.0 | - |
| usage_count | INTEGER | DEFAULT 0 | - |
| created_timestamp | TEXT | NOT NULL | - |
| updated_timestamp | TEXT | NOT NULL | - |
| active | BOOLEAN | DEFAULT 1 | - |

**Indexes:**

- `sqlite_autoindex_copilot_contexts_1`

#### copilot_suggestions

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| session_id | TEXT | NOT NULL | - |
| suggestion_type | TEXT | NOT NULL | - |
| suggestion_content | TEXT | NOT NULL | - |
| confidence_score | REAL | DEFAULT 0.0 | - |
| accepted | BOOLEAN | DEFAULT 0 | - |
| timestamp | TEXT | NOT NULL | - |
| context_used | TEXT |  | - |

**Foreign Keys:**

- `session_id` → `generation_sessions.session_id`

#### copilot_analytics

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| metric_name | TEXT | NOT NULL | - |
| metric_value | REAL | NOT NULL | - |
| session_id | TEXT |  | - |
| template_id | INTEGER |  | - |
| timestamp | TEXT | NOT NULL | - |
| details | TEXT |  | - |

**Foreign Keys:**

- `template_id` → `script_templates.id`
- `session_id` → `generation_sessions.session_id`

#### compliance_checks

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| check_name | TEXT | NOT NULL | - |
| check_type | TEXT | NOT NULL | - |
| target_type | TEXT | NOT NULL | - |
| target_id | TEXT | NOT NULL | - |
| check_result | TEXT | NOT NULL | - |
| details | TEXT |  | - |
| timestamp | TEXT | NOT NULL | - |
| auto_fix_attempted | BOOLEAN | DEFAULT 0 | - |
| auto_fix_success | BOOLEAN | DEFAULT 0 | - |

#### anti_recursion_tracking

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| operation_type | TEXT | NOT NULL | - |
| resource_path | TEXT | NOT NULL | - |
| access_count | INTEGER | DEFAULT 1 | - |
| last_access_timestamp | TEXT | NOT NULL | - |
| blocked | BOOLEAN | DEFAULT 0 | - |
| session_id | TEXT |  | - |
| details | TEXT |  | - |

#### compliance_patterns

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| pattern_name | TEXT | NOT NULL | - |
| pattern_type | TEXT | NOT NULL | - |
| pattern_regex | TEXT |  | - |
| description | TEXT |  | - |
| severity | TEXT | DEFAULT 'medium' | - |
| auto_fix_available | BOOLEAN | DEFAULT 0 | - |
| auto_fix_pattern | TEXT |  | - |
| active | BOOLEAN | DEFAULT 1 | - |

**Indexes:**

- `sqlite_autoindex_compliance_patterns_1`

#### script_templates

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| template_name | TEXT | NOT NULL | - |
| template_type | TEXT | NOT NULL, DEFAULT 'script' | - |
| category | TEXT | NOT NULL | - |
| description | TEXT |  | - |
| base_template | TEXT | NOT NULL | - |
| variables | TEXT | DEFAULT '[]' | - |
| dependencies | TEXT | DEFAULT '[]' | - |
| compliance_patterns | TEXT | DEFAULT '[]' | - |
| complexity_level | INTEGER | DEFAULT 1 | - |
| author | TEXT | DEFAULT 'Enterprise Framework' | - |
| version | TEXT | DEFAULT '1.0.0' | - |
| tags | TEXT | DEFAULT '[]' | - |
| created_timestamp | TEXT | NOT NULL | - |
| updated_timestamp | TEXT | NOT NULL | - |
| active | BOOLEAN | DEFAULT 1 | - |

**Indexes:**

- `sqlite_autoindex_script_templates_1`

#### advanced_script_analysis

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| script_path | TEXT | NOT NULL | - |
| ast_complexity_score | REAL |  | - |
| pattern_fingerprint | TEXT |  | - |
| dependency_graph | TEXT |  | - |
| template_similarity_score | REAL |  | - |
| environment_compatibility | TEXT |  | - |
| generation_potential | REAL |  | - |
| last_analyzed | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |

**Indexes:**

- `idx_script_analysis_path`
- `sqlite_autoindex_advanced_script_analysis_1`

#### environment_adaptation_rules

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| rule_name | TEXT | NOT NULL | - |
| source_pattern | TEXT | NOT NULL | - |
| target_pattern | TEXT | NOT NULL | - |
| environment_filter | TEXT |  | - |
| transformation_logic | TEXT |  | - |
| priority | INTEGER | DEFAULT 0 | - |
| active | BOOLEAN | DEFAULT TRUE | - |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |

**Indexes:**

- `idx_adaptation_rules_env`
- `sqlite_autoindex_environment_adaptation_rules_1`

#### copilot_integration_sessions

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| session_id | TEXT | NOT NULL | - |
| request_type | TEXT | NOT NULL | - |
| context_data | TEXT |  | - |
| template_used | TEXT |  | - |
| generated_content | TEXT |  | - |
| user_feedback | TEXT |  | - |
| effectiveness_score | REAL |  | - |
| environment | TEXT |  | - |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |

**Indexes:**

- `idx_copilot_sessions_type`
- `sqlite_autoindex_copilot_integration_sessions_1`

#### template_usage_analytics

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| template_id | TEXT | NOT NULL | - |
| usage_timestamp | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |
| environment | TEXT |  | - |
| success_rate | REAL |  | - |
| generation_time_ms | INTEGER |  | - |
| user_satisfaction | INTEGER |  | - |
| customizations_applied | TEXT |  | - |

**Foreign Keys:**

- `template_id` → `script_templates.template_name`

**Indexes:**

- `idx_template_analytics_id`

#### filesystem_sync_log

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| sync_session_id | TEXT | NOT NULL | - |
| action_type | TEXT | NOT NULL | - |
| file_path | TEXT | NOT NULL | - |
| status | TEXT | NOT NULL | - |
| error_message | TEXT |  | - |
| sync_timestamp | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - |

**Indexes:**

- `idx_sync_log_session`

### Scaling Innovation Database Tables

#### scaling_metrics

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| scaling_id | TEXT | NOT NULL | - |
| timestamp | TEXT | NOT NULL | - |
| current_capacity | REAL | NOT NULL | - |
| target_capacity | REAL | NOT NULL | - |
| scaling_efficiency | REAL |  | - |
| resource_utilization | REAL |  | - |
| performance_impact | REAL |  | - |
| cost_effectiveness | REAL |  | - |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | - |

**Indexes:**

- `sqlite_autoindex_scaling_metrics_1`

#### sqlite_sequence

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| name |  |  | - |
| seq |  |  | - |

#### innovation_opportunities

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| opportunity_id | TEXT | NOT NULL | - |
| timestamp | TEXT | NOT NULL | - |
| innovation_type | TEXT | NOT NULL | - |
| description | TEXT | NOT NULL | - |
| potential_impact | REAL | NOT NULL | - |
| implementation_complexity | REAL | NOT NULL | - |
| estimated_value | REAL | NOT NULL | - |
| priority_score | REAL | NOT NULL | - |
| status | TEXT | DEFAULT 'identified' | - |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | - |

**Indexes:**

- `sqlite_autoindex_innovation_opportunities_1`

#### capability_expansions

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| expansion_id | TEXT | NOT NULL | - |
| capability_name | TEXT | NOT NULL | - |
| current_level | REAL | NOT NULL | - |
| target_level | REAL | NOT NULL | - |
| expansion_progress | REAL | DEFAULT 0.0 | - |
| estimated_completion | TEXT |  | - |
| resource_requirements | TEXT |  | - |
| status | TEXT | DEFAULT 'planned' | - |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | - |

**Indexes:**

- `sqlite_autoindex_capability_expansions_1`

#### scaling_history

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| scaling_event_id | TEXT | NOT NULL | - |
| event_type | TEXT | NOT NULL | - |
| trigger_metric | TEXT | NOT NULL | - |
| trigger_value | REAL | NOT NULL | - |
| scaling_action | TEXT | NOT NULL | - |
| start_time | TEXT | NOT NULL | - |
| end_time | TEXT |  | - |
| success | BOOLEAN |  | - |
| performance_change | REAL |  | - |
| notes | TEXT |  | - |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | - |

**Indexes:**

- `sqlite_autoindex_scaling_history_1`

#### innovation_pipeline

**Type:** Unknown  
**Description:** Table description not available

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | - |
| innovation_id | TEXT | NOT NULL | - |
| stage | TEXT | NOT NULL | - |
| innovation_name | TEXT | NOT NULL | - |
| description | TEXT | NOT NULL | - |
| expected_impact | REAL | NOT NULL | - |
| development_progress | REAL | DEFAULT 0.0 | - |
| estimated_deployment | TEXT |  | - |
| resource_allocation | TEXT |  | - |
| status | TEXT | DEFAULT 'research' | - |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | - |

**Indexes:**

- `sqlite_autoindex_innovation_pipeline_1`

## Entity Relationships

- **enhanced_templates** many-to-one **enhanced_templates**
  - `parent_template_id` → `id`
  - enhanced_templates.parent_template_id references enhanced_templates.id

- **template_versions** many-to-one **enhanced_templates**
  - `template_id` → `id`
  - template_versions.template_id references enhanced_templates.id

- **environment_adaptations** many-to-one **enhanced_templates**
  - `source_template_id` → `id`
  - environment_adaptations.source_template_id references enhanced_templates.id

- **code_pattern_analysis** many-to-one **enhanced_logs**
  - `analysis_id` → `id`
  - code_pattern_analysis.analysis_id references enhanced_logs.id

- **template_intelligence** many-to-one **enhanced_templates**
  - `template_id` → `id`
  - template_intelligence.template_id references enhanced_templates.id

- **template_usage_analytics** many-to-one **enhanced_templates**
  - `template_id` → `id`
  - template_usage_analytics.template_id references enhanced_templates.id

- **template_usage_analytics** many-to-one **template_placeholders**
  - tracks how often each placeholder is used during generation

- **environment_variables** many-to-one **environment_profiles**
  - `profile_id` → `profile_id`
  - environment_variables.profile_id references environment_profiles.profile_id

- **integration_points** many-to-one **environment_profiles**
  - `profile_id` → `profile_id`
  - integration_points.profile_id references environment_profiles.profile_id

- **copilot_learning_events** many-to-one **copilot_sessions**
  - `session_id` → `session_id`
  - copilot_learning_events.session_id references copilot_sessions.session_id

- **change_tracking** many-to-one **copilot_learning_events**
  - `event_id` → `event_id`
  - change_tracking.event_id references copilot_learning_events.event_id

- **change_tracking** many-to-one **copilot_sessions**
  - `session_id` → `session_id`
  - change_tracking.session_id references copilot_sessions.session_id

- **todo_fixme_tracking** many-to-one **copilot_sessions**
  - `session_id` → `session_id`
  - todo_fixme_tracking.session_id references copilot_sessions.session_id

- **feedback_loops** many-to-one **copilot_sessions**
  - `source_session_id` → `session_id`
  - feedback_loops.source_session_id references copilot_sessions.session_id

- **feedback_loops** many-to-one **copilot_learning_events**
  - `source_event_id` → `event_id`
  - feedback_loops.source_event_id references copilot_learning_events.event_id

- **pattern_effectiveness** many-to-one **pattern_database**
  - `pattern_id` → `pattern_id`
  - pattern_effectiveness.pattern_id references pattern_database.pattern_id

- **copilot_decision_tree** many-to-one **copilot_learning_events**
  - `event_id` → `event_id`
  - copilot_decision_tree.event_id references copilot_learning_events.event_id

- **copilot_decision_tree** many-to-one **copilot_decision_tree**
  - `parent_decision_id` → `decision_id`
  - copilot_decision_tree.parent_decision_id references copilot_decision_tree.decision_id

- **template_effectiveness** many-to-one **script_templates**
  - `template_id` → `template_id`
  - template_effectiveness.template_id references script_templates.template_id

- **generation_history** many-to-one **script_templates**
  - `template_id` → `template_id`
  - generation_history.template_id references script_templates.template_id

- **template_variables** many-to-one **script_templates**
  - `template_id` → `id`
  - template_variables.template_id references script_templates.id

- **template_dependencies** many-to-one **script_templates**
  - `template_id` → `id`
  - template_dependencies.template_id references script_templates.id

- **environment_variables** many-to-one **environment_profiles**
  - `profile_id` → `id`
  - environment_variables.profile_id references environment_profiles.id

- **environment_adaptations** many-to-one **environment_profiles**
  - `target_environment_id` → `id`
  - environment_adaptations.target_environment_id references environment_profiles.id

- **environment_adaptations** many-to-one **script_templates**
  - `source_template_id` → `id`
  - environment_adaptations.source_template_id references script_templates.id

- **generation_sessions** many-to-one **environment_profiles**
  - `environment_profile_id` → `id`
  - generation_sessions.environment_profile_id references environment_profiles.id

- **generation_sessions** many-to-one **script_templates**
  - `template_used_id` → `id`
  - generation_sessions.template_used_id references script_templates.id

- **generated_scripts** many-to-one **generation_sessions**
  - `session_id` → `session_id`
  - generated_scripts.session_id references generation_sessions.session_id

- **generation_logs** many-to-one **generation_sessions**
  - `session_id` → `session_id`
  - generation_logs.session_id references generation_sessions.session_id

- **user_feedback** many-to-one **script_templates**
  - `template_id` → `id`
  - user_feedback.template_id references script_templates.id

- **user_feedback** many-to-one **generated_scripts**
  - `script_id` → `id`
  - user_feedback.script_id references generated_scripts.id

- **user_feedback** many-to-one **generation_sessions**
  - `session_id` → `session_id`
  - user_feedback.session_id references generation_sessions.session_id

- **performance_metrics** many-to-one **script_templates**
  - `template_id` → `id`
  - performance_metrics.template_id references script_templates.id

- **performance_metrics** many-to-one **generation_sessions**
  - `session_id` → `session_id`
  - performance_metrics.session_id references generation_sessions.session_id

- **copilot_suggestions** many-to-one **generation_sessions**
  - `session_id` → `session_id`
  - copilot_suggestions.session_id references generation_sessions.session_id

- **copilot_analytics** many-to-one **script_templates**
  - `template_id` → `id`
  - copilot_analytics.template_id references script_templates.id

- **copilot_analytics** many-to-one **generation_sessions**
  - `session_id` → `session_id`
  - copilot_analytics.session_id references generation_sessions.session_id

- **template_usage_analytics** many-to-one **script_templates**
  - `template_id` → `template_name`
  - template_usage_analytics.template_id references script_templates.template_name

- **template_intelligence** one-to-many **template_placeholders**
  - `template_id` → `template_id`
  - Template intelligence provides insights for placeholder usage

- **environment_profiles** one-to-many **adaptation_rules**
  - `environment_type` → `environment_context`
  - Environment profiles define applicable adaptation rules

- **code_pattern_analysis** many-to-one **template_intelligence**
  - `analysis_id` → `intelligence_id`
  - Code analysis feeds into template intelligence

\n
## 🤖🤖 DUAL COPILOT PATTERN COMPLIANT
**Enterprise Standards:** This documentation follows DUAL COPILOT patterns with visual processing indicators and anti-recursion protocols.
\n
## 🤖🤖 DUAL COPILOT PATTERN COMPLIANT
**Enterprise Standards:** This documentation follows DUAL COPILOT patterns with visual processing indicators and anti-recursion protocols.
