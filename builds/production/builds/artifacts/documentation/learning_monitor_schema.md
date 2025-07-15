
# Learning Monitor Database Documentation

## Overview
**Database**: learning_monitor  
**Type**: SQLite  
**Tables**: 40  
**Generated**: 2025-07-03 06:23:03

## Purpose
Central intelligence hub for template learning, pattern recognition, and cross-database coordination. Manages placeholder intelligence and adaptation rules.

## Tables Overview


### learning_metrics

**Rows**: 0  
**Columns**: 9

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| timestamp | TEXT | No | None | No |
| pattern_id | TEXT | No | None | No |
| effectiveness_score | REAL | No | None | No |
| learning_rate | REAL | No | None | No |
| adaptation_speed | REAL | No | None | No |
| resource_usage | TEXT | No | None | No |
| performance_indicators | TEXT | No | None | No |
| validation_status | TEXT | No | None | No |

#### SQL Definition
```sql
CREATE TABLE learning_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    pattern_id TEXT NOT NULL,
                    effectiveness_score REAL NOT NULL,
                    learning_rate REAL NOT NULL,
                    adaptation_speed REAL NOT NULL,
                    resource_usage TEXT NOT NULL,
                    performance_indicators TEXT NOT NULL,
                    validation_status TEXT NOT NULL
                )
```


### sqlite_sequence

**Rows**: 25  
**Columns**: 2

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| name |  | Yes | None | No |
| seq |  | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE sqlite_sequence(name,seq)
```


### monitoring_sessions

**Rows**: 4  
**Columns**: 8

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| session_id | TEXT | No | None | No |
| start_time | TEXT | No | None | No |
| end_time | TEXT | Yes | None | No |
| total_patterns_monitored | INTEGER | Yes | 0 | No |
| average_effectiveness | REAL | Yes | 0.0 | No |
| alerts_generated | INTEGER | Yes | 0 | No |
| status | TEXT | Yes | 'active' | No |

#### SQL Definition
```sql
CREATE TABLE monitoring_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    total_patterns_monitored INTEGER DEFAULT 0,
                    average_effectiveness REAL DEFAULT 0.0,
                    alerts_generated INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active'
                )
```


### monitoring_alerts

**Rows**: 0  
**Columns**: 8

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| timestamp | TEXT | No | None | No |
| session_id | TEXT | No | None | No |
| alert_type | TEXT | No | None | No |
| pattern_id | TEXT | No | None | No |
| severity | TEXT | No | None | No |
| message | TEXT | No | None | No |
| resolved | BOOLEAN | Yes | FALSE | No |

#### SQL Definition
```sql
CREATE TABLE monitoring_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    pattern_id TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE
                )
```


### enhanced_scripts

**Rows**: 1  
**Columns**: 17

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| name | TEXT | No | None | No |
| content | TEXT | No | None | No |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| updated_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| environment | TEXT | Yes | 'development' | No |
| version | TEXT | Yes | '1.0.0' | No |
| tags | TEXT | Yes | '[]' | No |
| category | TEXT | Yes | 'general' | No |
| author | TEXT | Yes | 'system' | No |
| description | TEXT | Yes | '' | No |
| dependencies | TEXT | Yes | '[]' | No |
| file_hash | TEXT | Yes | None | No |
| status | TEXT | Yes | 'active' | No |
| usage_count | INTEGER | Yes | 0 | No |
| last_used | TIMESTAMP | Yes | None | No |
| performance_metrics | TEXT | Yes | '{}' | No |

#### SQL Definition
```sql
CREATE TABLE enhanced_scripts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        environment TEXT DEFAULT 'development',
                        version TEXT DEFAULT '1.0.0',
                        tags TEXT DEFAULT '[]',
                        category TEXT DEFAULT 'general',
                        author TEXT DEFAULT 'system',
                        description TEXT DEFAULT '',
                        dependencies TEXT DEFAULT '[]',
                        file_hash TEXT UNIQUE,
                        status TEXT DEFAULT 'active',
                        usage_count INTEGER DEFAULT 0,
                        last_used TIMESTAMP,
                        performance_metrics TEXT DEFAULT '{}',
                        UNIQUE(name, version, environment)
                    )
```


### enhanced_templates

**Rows**: 0  
**Columns**: 19

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| name | TEXT | No | None | No |
| content | TEXT | No | None | No |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| updated_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| environment | TEXT | Yes | 'all' | No |
| version | TEXT | Yes | '1.0.0' | No |
| tags | TEXT | Yes | '[]' | No |
| category | TEXT | Yes | 'general' | No |
| template_type | TEXT | Yes | 'script' | No |
| author | TEXT | Yes | 'system' | No |
| description | TEXT | Yes | '' | No |
| variables | TEXT | Yes | '[]' | No |
| adaptation_rules | TEXT | Yes | '[]' | No |
| success_rate | REAL | Yes | 1.0 | No |
| usage_count | INTEGER | Yes | 0 | No |
| last_used | TIMESTAMP | Yes | None | No |
| parent_template_id | INTEGER | Yes | None | No |
| status | TEXT | Yes | 'active' | No |

#### SQL Definition
```sql
CREATE TABLE enhanced_templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        environment TEXT DEFAULT 'all',
                        version TEXT DEFAULT '1.0.0',
                        tags TEXT DEFAULT '[]',
                        category TEXT DEFAULT 'general',
                        template_type TEXT DEFAULT 'script',
                        author TEXT DEFAULT 'system',
                        description TEXT DEFAULT '',
                        variables TEXT DEFAULT '[]',
                        adaptation_rules TEXT DEFAULT '[]',
                        success_rate REAL DEFAULT 1.0,
                        usage_count INTEGER DEFAULT 0,
                        last_used TIMESTAMP,
                        parent_template_id INTEGER,
                        status TEXT DEFAULT 'active',
                        FOREIGN KEY (parent_template_id) REFERENCES enhanced_templates(id),
                        UNIQUE(name, version, environment)
                    )
```


### enhanced_logs

**Rows**: 2  
**Columns**: 15

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| action | TEXT | No | None | No |
| details | TEXT | Yes | '' | No |
| timestamp | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| environment | TEXT | Yes | 'development' | No |
| session_id | TEXT | Yes | None | No |
| user_id | TEXT | Yes | 'system' | No |
| log_level | TEXT | Yes | 'INFO' | No |
| component | TEXT | Yes | 'platform' | No |
| context_data | TEXT | Yes | '{}' | No |
| correlation_id | TEXT | Yes | None | No |
| duration_ms | INTEGER | Yes | None | No |
| success | BOOLEAN | Yes | 1 | No |
| error_message | TEXT | Yes | None | No |
| stack_trace | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE enhanced_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        action TEXT NOT NULL,
                        details TEXT DEFAULT '',
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        environment TEXT DEFAULT 'development',
                        session_id TEXT,
                        user_id TEXT DEFAULT 'system',
                        log_level TEXT DEFAULT 'INFO',
                        component TEXT DEFAULT 'platform',
                        context_data TEXT DEFAULT '{}',
                        correlation_id TEXT,
                        duration_ms INTEGER,
                        success BOOLEAN DEFAULT 1,
                        error_message TEXT,
                        stack_trace TEXT
                    )
```


### enhanced_lessons_learned

**Rows**: 1  
**Columns**: 19

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| description | TEXT | No | None | No |
| source | TEXT | No | None | No |
| timestamp | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| environment | TEXT | Yes | 'all' | No |
| lesson_type | TEXT | Yes | 'improvement' | No |
| category | TEXT | Yes | 'general' | No |
| impact_level | TEXT | Yes | 'medium' | No |
| confidence_score | REAL | Yes | 0.8 | No |
| validation_status | TEXT | Yes | 'pending' | No |
| applied_count | INTEGER | Yes | 0 | No |
| success_rate | REAL | Yes | 0.0 | No |
| tags | TEXT | Yes | '[]' | No |
| context_data | TEXT | Yes | '{}' | No |
| related_scripts | TEXT | Yes | '[]' | No |
| related_templates | TEXT | Yes | '[]' | No |
| created_by | TEXT | Yes | 'system' | No |
| validated_by | TEXT | Yes | None | No |
| validation_timestamp | TIMESTAMP | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE enhanced_lessons_learned (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        description TEXT NOT NULL,
                        source TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        environment TEXT DEFAULT 'all',
                        lesson_type TEXT DEFAULT 'improvement',
                        category TEXT DEFAULT 'general',
                        impact_level TEXT DEFAULT 'medium',
                        confidence_score REAL DEFAULT 0.8,
                        validation_status TEXT DEFAULT 'pending',
                        applied_count INTEGER DEFAULT 0,
                        success_rate REAL DEFAULT 0.0,
                        tags TEXT DEFAULT '[]',
                        context_data TEXT DEFAULT '{}',
                        related_scripts TEXT DEFAULT '[]',
                        related_templates TEXT DEFAULT '[]',
                        created_by TEXT DEFAULT 'system',
                        validated_by TEXT,
                        validation_timestamp TIMESTAMP
                    )
```


### template_versions

**Rows**: 0  
**Columns**: 9

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| template_id | INTEGER | No | None | No |
| version | TEXT | No | None | No |
| content | TEXT | No | None | No |
| changelog | TEXT | Yes | '' | No |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| created_by | TEXT | Yes | 'system' | No |
| is_current | BOOLEAN | Yes | 0 | No |
| migration_notes | TEXT | Yes | '' | No |

#### SQL Definition
```sql
CREATE TABLE template_versions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        template_id INTEGER NOT NULL,
                        version TEXT NOT NULL,
                        content TEXT NOT NULL,
                        changelog TEXT DEFAULT '',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by TEXT DEFAULT 'system',
                        is_current BOOLEAN DEFAULT 0,
                        migration_notes TEXT DEFAULT '',
                        FOREIGN KEY (template_id) REFERENCES enhanced_templates(id),
                        UNIQUE(template_id, version)
                    )
```


### environment_adaptations

**Rows**: 0  
**Columns**: 9

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| source_template_id | INTEGER | No | None | No |
| target_environment | TEXT | No | None | No |
| adaptation_rules | TEXT | Yes | '[]' | No |
| success_rate | REAL | Yes | 1.0 | No |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| last_applied | TIMESTAMP | Yes | None | No |
| application_count | INTEGER | Yes | 0 | No |
| performance_impact | TEXT | Yes | '{}' | No |

#### SQL Definition
```sql
CREATE TABLE environment_adaptations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_template_id INTEGER NOT NULL,
                        target_environment TEXT NOT NULL,
                        adaptation_rules TEXT DEFAULT '[]',
                        success_rate REAL DEFAULT 1.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_applied TIMESTAMP,
                        application_count INTEGER DEFAULT 0,
                        performance_impact TEXT DEFAULT '{}',
                        FOREIGN KEY (source_template_id) REFERENCES enhanced_templates(id),
                        UNIQUE(source_template_id, target_environment)
                    )
```


### cross_database_references

**Rows**: 12  
**Columns**: 10

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| source_database | TEXT | No | None | No |
| source_table | TEXT | No | None | No |
| source_id | TEXT | No | None | No |
| target_database | TEXT | No | None | No |
| target_table | TEXT | No | None | No |
| target_id | TEXT | No | None | No |
| relationship_type | TEXT | Yes | 'reference' | No |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| metadata | TEXT | Yes | '{}' | No |

#### SQL Definition
```sql
CREATE TABLE cross_database_references (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_database TEXT NOT NULL,
                        source_table TEXT NOT NULL,
                        source_id TEXT NOT NULL,
                        target_database TEXT NOT NULL,
                        target_table TEXT NOT NULL,
                        target_id TEXT NOT NULL,
                        relationship_type TEXT DEFAULT 'reference',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT DEFAULT '{}'
                    )
```


### template_placeholders

**Rows**: 21  
**Columns**: 11

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| placeholder_name | TEXT | No | None | No |
| placeholder_type | TEXT | No | None | No |
| default_value | TEXT | Yes | None | No |
| description | TEXT | No | None | No |
| validation_pattern | TEXT | Yes | None | No |
| environments | TEXT | Yes | None | No |
| usage_count | INTEGER | Yes | 0 | No |
| effectiveness_score | REAL | Yes | 0.0 | No |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| updated_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE template_placeholders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    placeholder_name TEXT UNIQUE NOT NULL,
                    placeholder_type TEXT NOT NULL,
                    default_value TEXT,
                    description TEXT NOT NULL,
                    validation_pattern TEXT,
                    environments TEXT, -- JSON array
                    usage_count INTEGER DEFAULT 0,
                    effectiveness_score REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
```


### code_pattern_analysis

**Rows**: 8080  
**Columns**: 10

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| analysis_id | TEXT | No | None | No |
| source_file | TEXT | No | None | No |
| pattern_type | TEXT | No | None | No |
| pattern_content | TEXT | No | None | No |
| confidence_score | REAL | Yes | 0.0 | No |
| placeholder_suggestions | TEXT | Yes | None | No |
| frequency_count | INTEGER | Yes | 1 | No |
| analysis_timestamp | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| environment_context | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE code_pattern_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT UNIQUE NOT NULL,
                    source_file TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    pattern_content TEXT NOT NULL,
                    confidence_score REAL DEFAULT 0.0,
                    placeholder_suggestions TEXT, -- JSON array
                    frequency_count INTEGER DEFAULT 1,
                    analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    environment_context TEXT,
                    FOREIGN KEY (analysis_id) REFERENCES enhanced_logs(id)
                )
```


### template_intelligence

**Rows**: 61  
**Columns**: 14

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| intelligence_id | TEXT | No | None | No |
| template_id | TEXT | No | None | No |
| suggestion_type | TEXT | No | None | No |
| suggestion_content | TEXT | No | None | No |
| confidence_score | REAL | Yes | 0.0 | No |
| usage_context | TEXT | Yes | None | No |
| success_rate | REAL | Yes | 0.0 | No |
| user_feedback_score | REAL | Yes | 0.0 | No |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| last_used | TIMESTAMP | Yes | None | No |
| intelligence_type | TEXT | Yes | 'code_analysis' | No |
| intelligence_data | TEXT | Yes | None | No |
| source_analysis | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE template_intelligence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    intelligence_id TEXT UNIQUE NOT NULL,
                    template_id TEXT NOT NULL,
                    suggestion_type TEXT NOT NULL, -- 'placeholder', 'pattern', 'optimization'
                    suggestion_content TEXT NOT NULL,
                    confidence_score REAL DEFAULT 0.0,
                    usage_context TEXT, -- JSON object
                    success_rate REAL DEFAULT 0.0,
                    user_feedback_score REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP, intelligence_type TEXT DEFAULT 'code_analysis', intelligence_data TEXT, source_analysis TEXT,
                    FOREIGN KEY (template_id) REFERENCES enhanced_templates(id)
                )
```


### cross_database_template_mapping

**Rows**: 72  
**Columns**: 13

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| mapping_id | TEXT | No | None | No |
| source_database | TEXT | No | None | No |
| source_table | TEXT | No | None | No |
| source_template_id | TEXT | Yes | None | No |
| target_database | TEXT | No | None | No |
| target_table | TEXT | No | None | No |
| target_template_id | TEXT | Yes | None | No |
| mapping_type | TEXT | No | None | No |
| mapping_rules | TEXT | Yes | None | No |
| sync_status | TEXT | Yes | 'active' | No |
| last_sync | TIMESTAMP | Yes | None | No |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE cross_database_template_mapping (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mapping_id TEXT UNIQUE NOT NULL,
                    source_database TEXT NOT NULL,
                    source_table TEXT NOT NULL,
                    source_template_id TEXT,
                    target_database TEXT NOT NULL,
                    target_table TEXT NOT NULL,
                    target_template_id TEXT,
                    mapping_type TEXT NOT NULL, -- 'template_sharing', 'pattern_reuse', 'placeholder_sync'
                    mapping_rules TEXT, -- JSON object
                    sync_status TEXT DEFAULT 'active',
                    last_sync TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
```


### placeholder_usage_analytics

**Rows**: 0  
**Columns**: 11

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| usage_id | TEXT | No | None | No |
| placeholder_name | TEXT | No | None | No |
| template_id | TEXT | Yes | None | No |
| environment | TEXT | Yes | None | No |
| usage_context | TEXT | Yes | None | No |
| substitution_value | TEXT | Yes | None | No |
| success | BOOLEAN | Yes | 1 | No |
| performance_ms | INTEGER | Yes | None | No |
| user_satisfaction | INTEGER | Yes | None | No |
| usage_timestamp | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE placeholder_usage_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usage_id TEXT UNIQUE NOT NULL,
                    placeholder_name TEXT NOT NULL,
                    template_id TEXT,
                    environment TEXT,
                    usage_context TEXT, -- JSON object
                    substitution_value TEXT,
                    success BOOLEAN DEFAULT 1,
                    performance_ms INTEGER,
                    user_satisfaction INTEGER, -- 1-5 scale
                    usage_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (placeholder_name) REFERENCES template_placeholders(placeholder_name),
                    FOREIGN KEY (template_id) REFERENCES enhanced_templates(id)
                )
```


### environment_adaptation_intelligence

**Rows**: 0  
**Columns**: 11

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| adaptation_id | TEXT | No | None | No |
| source_environment | TEXT | No | None | No |
| target_environment | TEXT | No | None | No |
| adaptation_type | TEXT | No | None | No |
| adaptation_pattern | TEXT | No | None | No |
| success_rate | REAL | Yes | 0.0 | No |
| performance_impact | REAL | Yes | 0.0 | No |
| learning_data | TEXT | Yes | None | No |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| last_applied | TIMESTAMP | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE environment_adaptation_intelligence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    adaptation_id TEXT UNIQUE NOT NULL,
                    source_environment TEXT NOT NULL,
                    target_environment TEXT NOT NULL,
                    adaptation_type TEXT NOT NULL, -- 'placeholder', 'configuration', 'dependency'
                    adaptation_pattern TEXT NOT NULL,
                    success_rate REAL DEFAULT 0.0,
                    performance_impact REAL DEFAULT 0.0,
                    learning_data TEXT, -- JSON object
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_applied TIMESTAMP
                )
```


### environment_variables

**Rows**: 0  
**Columns**: 9

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| variable_id | INTEGER | Yes | None | Yes |
| profile_id | INTEGER | Yes | None | No |
| variable_name | TEXT | No | None | No |
| variable_value | TEXT | Yes | None | No |
| variable_type | TEXT | Yes | 'string' | No |
| description | TEXT | Yes | None | No |
| is_secure | BOOLEAN | Yes | FALSE | No |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| updated_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE environment_variables (
    variable_id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER,
    variable_name TEXT NOT NULL,
    variable_value TEXT,
    variable_type TEXT DEFAULT 'string',
    description TEXT,
    is_secure BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES environment_profiles(profile_id)
)
```


### integration_points

**Rows**: 0  
**Columns**: 7

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| integration_id | INTEGER | Yes | None | Yes |
| profile_id | INTEGER | Yes | None | No |
| integration_type | TEXT | No | None | No |
| target_system | TEXT | No | None | No |
| configuration | TEXT | Yes | None | No |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| updated_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE integration_points (
    integration_id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER,
    integration_type TEXT NOT NULL,
    target_system TEXT NOT NULL,
    configuration TEXT, -- JSON object
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES environment_profiles(profile_id)
)
```


### environment_specific_templates

**Rows**: 0  
**Columns**: 9

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| base_template_id | TEXT | No | None | No |
| environment_name | TEXT | No | None | No |
| template_content | TEXT | No | None | No |
| adaptation_rules | TEXT | Yes | None | No |
| performance_metrics | TEXT | Yes | None | No |
| success_rate | REAL | Yes | None | No |
| created_at | TEXT | Yes | CURRENT_TIMESTAMP | No |
| updated_at | TEXT | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE environment_specific_templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        base_template_id TEXT NOT NULL,
                        environment_name TEXT NOT NULL,
                        template_content TEXT NOT NULL,
                        adaptation_rules TEXT, -- JSON object
                        performance_metrics TEXT, -- JSON object
                        success_rate REAL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(base_template_id, environment_name)
                    )
```


### cross_database_aggregation_results

**Rows**: 1  
**Columns**: 8

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| aggregation_id | TEXT | No | None | No |
| aggregation_timestamp | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| databases_involved | TEXT | No | None | No |
| aggregation_type | TEXT | No | None | No |
| results_data | TEXT | No | None | No |
| confidence_score | REAL | Yes | 0.0 | No |
| insights_generated | INTEGER | Yes | 0 | No |

#### SQL Definition
```sql
CREATE TABLE cross_database_aggregation_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    aggregation_id TEXT UNIQUE NOT NULL,
                    aggregation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    databases_involved TEXT NOT NULL,
                    aggregation_type TEXT NOT NULL,
                    results_data TEXT NOT NULL,
                    confidence_score REAL DEFAULT 0.0,
                    insights_generated INTEGER DEFAULT 0
                )
```


### environment_profiles

**Rows**: 13  
**Columns**: 11

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| profile_id | TEXT | No | None | No |
| profile_name | TEXT | No | None | No |
| environment_type | TEXT | No | None | No |
| characteristics | TEXT | No | None | No |
| adaptation_rules | TEXT | No | None | No |
| template_preferences | TEXT | No | None | No |
| priority | INTEGER | Yes | 0 | No |
| active | BOOLEAN | Yes | 1 | No |
| created_timestamp | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| modified_timestamp | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE environment_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id TEXT UNIQUE NOT NULL,
                profile_name TEXT NOT NULL,
                environment_type TEXT NOT NULL,
                characteristics TEXT NOT NULL,
                adaptation_rules TEXT NOT NULL,
                template_preferences TEXT NOT NULL,
                priority INTEGER DEFAULT 0,
                active BOOLEAN DEFAULT 1,
                created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
```


### adaptation_rules

**Rows**: 11  
**Columns**: 11

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| rule_id | TEXT | No | None | No |
| rule_name | TEXT | No | None | No |
| environment_context | TEXT | No | None | No |
| condition_pattern | TEXT | No | None | No |
| adaptation_action | TEXT | No | None | No |
| template_modifications | TEXT | No | None | No |
| confidence_threshold | REAL | Yes | 0.8 | No |
| execution_priority | INTEGER | Yes | 0 | No |
| active | BOOLEAN | Yes | 1 | No |
| created_timestamp | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE adaptation_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id TEXT UNIQUE NOT NULL,
                rule_name TEXT NOT NULL,
                environment_context TEXT NOT NULL,
                condition_pattern TEXT NOT NULL,
                adaptation_action TEXT NOT NULL,
                template_modifications TEXT NOT NULL,
                confidence_threshold REAL DEFAULT 0.8,
                execution_priority INTEGER DEFAULT 0,
                active BOOLEAN DEFAULT 1,
                created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
```


### environment_context_history

**Rows**: 1  
**Columns**: 9

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| context_id | TEXT | No | None | No |
| timestamp | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| environment_type | TEXT | No | None | No |
| system_info | TEXT | No | None | No |
| workspace_context | TEXT | No | None | No |
| active_profiles | TEXT | No | None | No |
| applicable_rules | TEXT | No | None | No |
| adaptation_results | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE environment_context_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                context_id TEXT UNIQUE NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                environment_type TEXT NOT NULL,
                system_info TEXT NOT NULL,
                workspace_context TEXT NOT NULL,
                active_profiles TEXT NOT NULL,
                applicable_rules TEXT NOT NULL,
                adaptation_results TEXT
            )
```


### template_adaptation_logs

**Rows**: 1  
**Columns**: 9

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| adaptation_id | TEXT | No | None | No |
| timestamp | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| source_template | TEXT | No | None | No |
| target_environment | TEXT | No | None | No |
| applied_rules | TEXT | No | None | No |
| adaptation_changes | TEXT | No | None | No |
| success_rate | REAL | Yes | 0.0 | No |
| performance_impact | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE template_adaptation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                adaptation_id TEXT UNIQUE NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_template TEXT NOT NULL,
                target_environment TEXT NOT NULL,
                applied_rules TEXT NOT NULL,
                adaptation_changes TEXT NOT NULL,
                success_rate REAL DEFAULT 0.0,
                performance_impact TEXT
            )
```


### placeholder_metadata

**Rows**: 60  
**Columns**: 12

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| placeholder_name | TEXT | No | None | No |
| placeholder_type | TEXT | No | None | No |
| category | TEXT | No | None | No |
| description | TEXT | Yes | None | No |
| default_value | TEXT | Yes | None | No |
| validation_pattern | TEXT | Yes | None | No |
| is_required | BOOLEAN | Yes | 1 | No |
| usage_count | INTEGER | Yes | 0 | No |
| last_used | DATETIME | Yes | None | No |
| created_timestamp | DATETIME | Yes | CURRENT_TIMESTAMP | No |
| updated_timestamp | DATETIME | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE placeholder_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    placeholder_name TEXT UNIQUE NOT NULL,
                    placeholder_type TEXT NOT NULL, -- 'database', 'api', 'environment', etc.
                    category TEXT NOT NULL,
                    description TEXT,
                    default_value TEXT,
                    validation_pattern TEXT,
                    is_required BOOLEAN DEFAULT 1,
                    usage_count INTEGER DEFAULT 0,
                    last_used DATETIME,
                    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
```


### cross_database_templates

**Rows**: 7  
**Columns**: 10

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| source_database | TEXT | No | None | No |
| target_database | TEXT | No | None | No |
| template_id | TEXT | No | None | No |
| mapping_type | TEXT | No | None | No |
| sync_status | TEXT | Yes | 'pending' | No |
| last_sync | DATETIME | Yes | None | No |
| conflict_resolution | TEXT | Yes | None | No |
| created_timestamp | DATETIME | Yes | CURRENT_TIMESTAMP | No |
| metadata | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE cross_database_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_database TEXT NOT NULL,
                    target_database TEXT NOT NULL,
                    template_id TEXT NOT NULL,
                    mapping_type TEXT NOT NULL, -- 'reference', 'clone', 'adaptation'
                    sync_status TEXT DEFAULT 'pending',
                    last_sync DATETIME,
                    conflict_resolution TEXT,
                    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT -- JSON
                )
```


### advanced_code_patterns

**Rows**: 9  
**Columns**: 11

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| pattern_name | TEXT | No | None | No |
| pattern_type | TEXT | No | None | No |
| pattern_regex | TEXT | Yes | None | No |
| confidence_score | REAL | Yes | 0.0 | No |
| detection_count | INTEGER | Yes | 0 | No |
| false_positive_rate | REAL | Yes | 0.0 | No |
| last_detection | DATETIME | Yes | None | No |
| created_timestamp | DATETIME | Yes | CURRENT_TIMESTAMP | No |
| is_active | BOOLEAN | Yes | 1 | No |
| improvement_suggestions | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE advanced_code_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_name TEXT NOT NULL,
                    pattern_type TEXT NOT NULL, -- 'placeholder_candidate', 'template_structure', 'anti_pattern'
                    pattern_regex TEXT,
                    confidence_score REAL DEFAULT 0.0,
                    detection_count INTEGER DEFAULT 0,
                    false_positive_rate REAL DEFAULT 0.0,
                    last_detection DATETIME,
                    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    improvement_suggestions TEXT
                )
```


### template_intelligence_analytics

**Rows**: 2  
**Columns**: 11

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| analysis_id | TEXT | No | None | No |
| analysis_type | TEXT | No | None | No |
| scope | TEXT | No | None | No |
| input_data | TEXT | Yes | None | No |
| results | TEXT | Yes | None | No |
| quality_metrics | TEXT | Yes | None | No |
| recommendations | TEXT | Yes | None | No |
| execution_time_ms | INTEGER | Yes | None | No |
| created_timestamp | DATETIME | Yes | CURRENT_TIMESTAMP | No |
| status | TEXT | Yes | 'completed' | No |

#### SQL Definition
```sql
CREATE TABLE template_intelligence_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT UNIQUE NOT NULL,
                    analysis_type TEXT NOT NULL, -- 'quality_assessment', 'usage_analysis', 'optimization'
                    scope TEXT NOT NULL, -- 'single_template', 'database', 'cross_database'
                    input_data TEXT, -- JSON
                    results TEXT, -- JSON
                    quality_metrics TEXT, -- JSON
                    recommendations TEXT, -- JSON
                    execution_time_ms INTEGER,
                    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'completed'
                )
```


### environment_template_adaptations

**Rows**: 7  
**Columns**: 11

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| template_id | TEXT | No | None | No |
| environment_name | TEXT | No | None | No |
| adaptation_rules | TEXT | Yes | None | No |
| placeholder_overrides | TEXT | Yes | None | No |
| performance_profile | TEXT | Yes | None | No |
| security_requirements | TEXT | Yes | None | No |
| compliance_rules | TEXT | Yes | None | No |
| last_updated | DATETIME | Yes | CURRENT_TIMESTAMP | No |
| is_active | BOOLEAN | Yes | 1 | No |
| validation_status | TEXT | Yes | 'pending' | No |

#### SQL Definition
```sql
CREATE TABLE environment_template_adaptations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_id TEXT NOT NULL,
                    environment_name TEXT NOT NULL,
                    adaptation_rules TEXT, -- JSON
                    placeholder_overrides TEXT, -- JSON
                    performance_profile TEXT, -- JSON
                    security_requirements TEXT, -- JSON
                    compliance_rules TEXT, -- JSON
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    validation_status TEXT DEFAULT 'pending'
                )
```


### template_versioning

**Rows**: 0  
**Columns**: 10

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| template_id | TEXT | No | None | No |
| version_number | TEXT | No | None | No |
| change_type | TEXT | No | None | No |
| placeholder_changes | TEXT | Yes | None | No |
| compatibility_level | TEXT | Yes | None | No |
| created_date | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| created_by | TEXT | Yes | None | No |
| approval_status | TEXT | Yes | 'PENDING' | No |
| rollback_data | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE template_versioning (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_id TEXT NOT NULL,
                    version_number TEXT NOT NULL,
                    change_type TEXT NOT NULL, -- MAJOR, MINOR, PATCH, HOTFIX
                    placeholder_changes TEXT, -- JSON of changed placeholders
                    compatibility_level TEXT, -- BACKWARD, FORWARD, BREAKING
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT,
                    approval_status TEXT DEFAULT 'PENDING',
                    rollback_data TEXT, -- JSON for rollback capability
                    UNIQUE(template_id, version_number)
                )
```


### placeholder_intelligence

**Rows**: 64  
**Columns**: 14

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| placeholder_name | TEXT | No | None | No |
| placeholder_category | TEXT | No | None | No |
| usage_frequency | INTEGER | Yes | 0 | No |
| context_patterns | TEXT | Yes | None | No |
| value_patterns | TEXT | Yes | None | No |
| validation_regex | TEXT | Yes | None | No |
| default_value | TEXT | Yes | None | No |
| environment_specific | BOOLEAN | Yes | 0 | No |
| security_level | TEXT | Yes | None | No |
| transformation_rules | TEXT | Yes | None | No |
| related_placeholders | TEXT | Yes | None | No |
| quality_score | REAL | Yes | 0.0 | No |
| last_updated | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE placeholder_intelligence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    placeholder_name TEXT NOT NULL UNIQUE,
                    placeholder_category TEXT NOT NULL,
                    usage_frequency INTEGER DEFAULT 0,
                    context_patterns TEXT, -- JSON of common contexts
                    value_patterns TEXT, -- JSON of common values/formats
                    validation_regex TEXT,
                    default_value TEXT,
                    environment_specific BOOLEAN DEFAULT 0,
                    security_level TEXT, -- PUBLIC, INTERNAL, CONFIDENTIAL, SECRET
                    transformation_rules TEXT, -- JSON transformation rules
                    related_placeholders TEXT, -- JSON array of related placeholders
                    quality_score REAL DEFAULT 0.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
```


### template_dependency_graph

**Rows**: 0  
**Columns**: 10

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| parent_template | TEXT | No | None | No |
| child_template | TEXT | No | None | No |
| dependency_type | TEXT | No | None | No |
| dependency_strength | TEXT | Yes | None | No |
| version_compatibility | TEXT | Yes | None | No |
| circular_dependency_check | TEXT | Yes | None | No |
| created_date | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| validated_date | TIMESTAMP | Yes | None | No |
| status | TEXT | Yes | 'ACTIVE' | No |

#### SQL Definition
```sql
CREATE TABLE template_dependency_graph (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parent_template TEXT NOT NULL,
                    child_template TEXT NOT NULL,
                    dependency_type TEXT NOT NULL, -- INHERIT, INCLUDE, REFERENCE
                    dependency_strength TEXT, -- STRONG, WEAK, OPTIONAL
                    version_compatibility TEXT, -- JSON version constraints
                    circular_dependency_check TEXT, -- Path validation
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    validated_date TIMESTAMP,
                    status TEXT DEFAULT 'ACTIVE'
                )
```


### enterprise_compliance_audit

**Rows**: 1  
**Columns**: 14

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| audit_id | TEXT | No | None | No |
| audit_type | TEXT | No | None | No |
| target_scope | TEXT | No | None | No |
| target_identifier | TEXT | No | None | No |
| compliance_rules | TEXT | Yes | None | No |
| audit_results | TEXT | Yes | None | No |
| compliance_score | REAL | Yes | None | No |
| violations_found | INTEGER | Yes | 0 | No |
| remediation_actions | TEXT | Yes | None | No |
| auditor | TEXT | Yes | None | No |
| audit_date | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| next_audit_due | TIMESTAMP | Yes | None | No |
| status | TEXT | Yes | 'COMPLETED' | No |

#### SQL Definition
```sql
CREATE TABLE enterprise_compliance_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    audit_id TEXT NOT NULL UNIQUE,
                    audit_type TEXT NOT NULL, -- SECURITY, PERFORMANCE, DATA_QUALITY
                    target_scope TEXT NOT NULL, -- DATABASE, TABLE, TEMPLATE, PLACEHOLDER
                    target_identifier TEXT NOT NULL,
                    compliance_rules TEXT, -- JSON compliance rules
                    audit_results TEXT, -- JSON detailed results
                    compliance_score REAL,
                    violations_found INTEGER DEFAULT 0,
                    remediation_actions TEXT, -- JSON action items
                    auditor TEXT,
                    audit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    next_audit_due TIMESTAMP,
                    status TEXT DEFAULT 'COMPLETED'
                )
```


### intelligent_migration_log

**Rows**: 0  
**Columns**: 16

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| migration_id | TEXT | No | None | No |
| migration_type | TEXT | No | None | No |
| source_version | TEXT | Yes | None | No |
| target_version | TEXT | Yes | None | No |
| affected_components | TEXT | Yes | None | No |
| migration_script | TEXT | Yes | None | No |
| execution_plan | TEXT | Yes | None | No |
| rollback_plan | TEXT | Yes | None | No |
| execution_start | TIMESTAMP | Yes | None | No |
| execution_end | TIMESTAMP | Yes | None | No |
| execution_status | TEXT | Yes | None | No |
| error_details | TEXT | Yes | None | No |
| performance_metrics | TEXT | Yes | None | No |
| validated_by | TEXT | Yes | None | No |
| validation_date | TIMESTAMP | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE intelligent_migration_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    migration_id TEXT NOT NULL UNIQUE,
                    migration_type TEXT NOT NULL, -- SCHEMA, DATA, TEMPLATE, PLACEHOLDER
                    source_version TEXT,
                    target_version TEXT,
                    affected_components TEXT, -- JSON list of affected items
                    migration_script TEXT, -- The actual migration commands
                    execution_plan TEXT, -- JSON execution plan
                    rollback_plan TEXT, -- JSON rollback plan
                    execution_start TIMESTAMP,
                    execution_end TIMESTAMP,
                    execution_status TEXT, -- PENDING, RUNNING, SUCCESS, FAILED, ROLLED_BACK
                    error_details TEXT, -- JSON error information
                    performance_metrics TEXT, -- JSON performance data
                    validated_by TEXT,
                    validation_date TIMESTAMP
                )
```


### template_sharing_registry

**Rows**: 3  
**Columns**: 11

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| template_id | TEXT | No | None | No |
| template_name | TEXT | No | None | No |
| template_category | TEXT | Yes | None | No |
| source_database | TEXT | Yes | None | No |
| shared_databases | TEXT | Yes | None | No |
| sharing_rules | TEXT | Yes | None | No |
| access_level | TEXT | Yes | 'SHARED' | No |
| version_compatibility | TEXT | Yes | None | No |
| last_synchronized | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| sharing_status | TEXT | Yes | 'ACTIVE' | No |

#### SQL Definition
```sql
CREATE TABLE template_sharing_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id TEXT NOT NULL UNIQUE,
                template_name TEXT NOT NULL,
                template_category TEXT,
                source_database TEXT,
                shared_databases TEXT, -- JSON array
                sharing_rules TEXT, -- JSON rules
                access_level TEXT DEFAULT 'SHARED',
                version_compatibility TEXT,
                last_synchronized TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sharing_status TEXT DEFAULT 'ACTIVE'
            )
```


### cross_database_sync_log

**Rows**: 0  
**Columns**: 12

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| sync_id | TEXT | No | None | No |
| source_database | TEXT | Yes | None | No |
| target_databases | TEXT | Yes | None | No |
| sync_type | TEXT | Yes | None | No |
| sync_operation | TEXT | Yes | None | No |
| items_synchronized | INTEGER | Yes | 0 | No |
| conflicts_resolved | INTEGER | Yes | 0 | No |
| sync_start | TIMESTAMP | Yes | None | No |
| sync_end | TIMESTAMP | Yes | None | No |
| sync_status | TEXT | Yes | 'PENDING' | No |
| error_details | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE cross_database_sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sync_id TEXT NOT NULL UNIQUE,
                source_database TEXT,
                target_databases TEXT, -- JSON array
                sync_type TEXT, -- TEMPLATE, PLACEHOLDER, SCHEMA
                sync_operation TEXT, -- PUSH, PULL, BIDIRECTIONAL
                items_synchronized INTEGER DEFAULT 0,
                conflicts_resolved INTEGER DEFAULT 0,
                sync_start TIMESTAMP,
                sync_end TIMESTAMP,
                sync_status TEXT DEFAULT 'PENDING',
                error_details TEXT
            )
```


### placeholder_standardization_log

**Rows**: 48  
**Columns**: 9

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| standardization_id | TEXT | No | None | No |
| category | TEXT | No | None | No |
| old_placeholder | TEXT | No | None | No |
| new_placeholder | TEXT | No | None | No |
| affected_databases | TEXT | Yes | None | No |
| standardization_date | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| impact_assessment | TEXT | Yes | None | No |
| rollback_data | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE placeholder_standardization_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                standardization_id TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                old_placeholder TEXT NOT NULL,
                new_placeholder TEXT NOT NULL,
                affected_databases TEXT, -- JSON array
                standardization_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                impact_assessment TEXT, -- JSON impact data
                rollback_data TEXT -- JSON rollback information
            )
```


### data_flow_mapping

**Rows**: 3  
**Columns**: 13

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| flow_id | TEXT | No | None | No |
| flow_name | TEXT | No | None | No |
| flow_description | TEXT | Yes | None | No |
| flow_path | TEXT | Yes | None | No |
| flow_type | TEXT | Yes | None | No |
| data_types | TEXT | Yes | None | No |
| latency_requirement | TEXT | Yes | None | No |
| consistency_level | TEXT | Yes | None | No |
| throughput_estimate | INTEGER | Yes | None | No |
| created_date | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| last_optimized | TIMESTAMP | Yes | None | No |
| flow_status | TEXT | Yes | 'ACTIVE' | No |

#### SQL Definition
```sql
CREATE TABLE data_flow_mapping (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flow_id TEXT NOT NULL UNIQUE,
                flow_name TEXT NOT NULL,
                flow_description TEXT,
                flow_path TEXT, -- JSON array of databases
                flow_type TEXT,
                data_types TEXT, -- JSON array
                latency_requirement TEXT,
                consistency_level TEXT,
                throughput_estimate INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_optimized TIMESTAMP,
                flow_status TEXT DEFAULT 'ACTIVE'
            )
```


### environment_detection

**Rows**: 2  
**Columns**: 9

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| detection_session_id | TEXT | No | None | No |
| detected_environment | TEXT | Yes | None | No |
| confidence_score | REAL | Yes | None | No |
| detection_methods | TEXT | Yes | None | No |
| system_characteristics | TEXT | Yes | None | No |
| override_settings | TEXT | Yes | None | No |
| detection_date | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| validation_status | TEXT | Yes | 'PENDING' | No |

#### SQL Definition
```sql
CREATE TABLE environment_detection (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                detection_session_id TEXT NOT NULL UNIQUE,
                detected_environment TEXT,
                confidence_score REAL,
                detection_methods TEXT, -- JSON
                system_characteristics TEXT, -- JSON
                override_settings TEXT, -- JSON
                detection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                validation_status TEXT DEFAULT 'PENDING'
            )
```


## Relationships

- **enhanced_templates.parent_template_id** → **enhanced_templates.id** (FOREIGN_KEY)
- **template_versions.template_id** → **enhanced_templates.id** (FOREIGN_KEY)
- **environment_adaptations.source_template_id** → **enhanced_templates.id** (FOREIGN_KEY)
- **code_pattern_analysis.analysis_id** → **enhanced_logs.id** (FOREIGN_KEY)
- **template_intelligence.template_id** → **enhanced_templates.id** (FOREIGN_KEY)
- **placeholder_usage_analytics.template_id** → **enhanced_templates.id** (FOREIGN_KEY)
- **placeholder_usage_analytics.placeholder_name** → **template_placeholders.placeholder_name** (FOREIGN_KEY)
- **environment_variables.profile_id** → **environment_profiles.profile_id** (FOREIGN_KEY)
- **integration_points.profile_id** → **environment_profiles.profile_id** (FOREIGN_KEY)
