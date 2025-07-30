
# Production Database Documentation

## Overview
**Database**: production  
**Type**: SQLite  
**Tables**: 46  
**Generated**: 2025-07-03 06:23:03

## Purpose
Production-ready configuration storage with optimized templates, deployment configurations, and performance baselines.

## Tables Overview


### file_system_mapping

**Rows**: 3130  
**Columns**: 13

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| file_path | TEXT | No | None | No |
| file_hash | TEXT | Yes | None | No |
| file_size | INTEGER | Yes | None | No |
| last_modified | TIMESTAMP | Yes | None | No |
| status | TEXT | Yes | 'active' | No |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| updated_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| file_content | TEXT | Yes | None | No |
| file_type | TEXT | Yes | None | No |
| backup_location | TEXT | Yes | None | No |
| compression_type | TEXT | Yes | None | No |
| encoding | TEXT | Yes | "utf-8" | No |

#### SQL Definition
```sql
CREATE TABLE file_system_mapping (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                file_hash TEXT,
                file_size INTEGER,
                last_modified TIMESTAMP,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            , file_content TEXT, file_type TEXT, backup_location TEXT, compression_type TEXT, encoding TEXT DEFAULT "utf-8")
```


### sqlite_sequence

**Rows**: 18  
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


### validation_sessions

**Rows**: 0  
**Columns**: 6

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| session_id | TEXT | No | None | No |
| start_time | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| end_time | TIMESTAMP | Yes | None | No |
| status | TEXT | Yes | 'active' | No |
| results | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE validation_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                status TEXT DEFAULT 'active',
                results TEXT
            )
```


### github_sessions

**Rows**: 0  
**Columns**: 7

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| session_id | TEXT | No | None | No |
| start_time | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| end_time | TIMESTAMP | Yes | None | No |
| objective | TEXT | Yes | None | No |
| status | TEXT | Yes | 'active' | No |
| chunks_completed | INTEGER | Yes | 0 | No |

#### SQL Definition
```sql
CREATE TABLE github_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                objective TEXT,
                status TEXT DEFAULT 'active',
                chunks_completed INTEGER DEFAULT 0
            )
```


### system_info

**Rows**: 0  
**Columns**: 5

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| key | TEXT | No | None | No |
| value | TEXT | Yes | None | No |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| updated_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE system_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
```


### log_correlation_results

**Rows**: 6  
**Columns**: 11

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| analysis_timestamp | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| total_files_analyzed | INTEGER | Yes | None | No |
| total_events_found | INTEGER | Yes | None | No |
| events_by_type | TEXT | Yes | None | No |
| error_patterns | TEXT | Yes | None | No |
| success_patterns | TEXT | Yes | None | No |
| compliance_events | TEXT | Yes | None | No |
| performance_metrics | TEXT | Yes | None | No |
| anomalies | TEXT | Yes | None | No |
| execution_time | REAL | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE log_correlation_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        total_files_analyzed INTEGER,
                        total_events_found INTEGER,
                        events_by_type TEXT,
                        error_patterns TEXT,
                        success_patterns TEXT,
                        compliance_events TEXT,
                        performance_metrics TEXT,
                        anomalies TEXT,
                        execution_time REAL
                    )
```


### compliance_events

**Rows**: 5  
**Columns**: 9

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| event_type | TEXT | No | None | No |
| event_category | TEXT | No | None | No |
| description | TEXT | No | None | No |
| severity | TEXT | Yes | 'INFO' | No |
| timestamp | TEXT | No | None | No |
| source_file | TEXT | Yes | None | No |
| compliance_score | REAL | Yes | 100.0 | No |
| created_at | TEXT | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE compliance_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                event_category TEXT NOT NULL,
                description TEXT NOT NULL,
                severity TEXT DEFAULT 'INFO',
                timestamp TEXT NOT NULL,
                source_file TEXT,
                compliance_score REAL DEFAULT 100.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
```


### enhanced_compliance_tracking

**Rows**: 4  
**Columns**: 8

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| check_timestamp | TEXT | No | None | No |
| check_type | TEXT | No | None | No |
| status | TEXT | No | None | No |
| details | TEXT | Yes | None | No |
| compliance_score | REAL | Yes | None | No |
| dual_copilot_validation | BOOLEAN | Yes | TRUE | No |
| created_at | TEXT | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE enhanced_compliance_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                check_timestamp TEXT NOT NULL,
                check_type TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT,
                compliance_score REAL,
                dual_copilot_validation BOOLEAN DEFAULT TRUE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
```


### copilot_learning_events

**Rows**: 0  
**Columns**: 25

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| event_id | TEXT | Yes | None | Yes |
| session_id | TEXT | No | None | No |
| event_type | TEXT | No | None | No |
| event_category | TEXT | No | None | No |
| timestamp | DATETIME | Yes | CURRENT_TIMESTAMP | No |
| component | TEXT | Yes | None | No |
| file_path | TEXT | Yes | None | No |
| function_name | TEXT | Yes | None | No |
| line_number | INTEGER | Yes | None | No |
| action_taken | TEXT | No | None | No |
| reasoning | TEXT | Yes | None | No |
| confidence_score | REAL | Yes | 0.0 | No |
| outcome | TEXT | Yes | None | No |
| effectiveness_score | REAL | Yes | None | No |
| user_feedback | TEXT | Yes | None | No |
| pattern_ids | TEXT | Yes | None | No |
| similar_events | TEXT | Yes | None | No |
| learning_weight | REAL | Yes | 1.0 | No |
| response_time_ms | INTEGER | Yes | None | No |
| tokens_processed | INTEGER | Yes | None | No |
| memory_usage_mb | REAL | Yes | None | No |
| context_data | TEXT | Yes | None | No |
| tags | TEXT | Yes | None | No |
| created_at | DATETIME | Yes | CURRENT_TIMESTAMP | No |
| updated_at | DATETIME | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE copilot_learning_events (
    event_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    event_type TEXT NOT NULL, -- 'decision', 'suggestion', 'error', 'success', 'pattern_match'
    event_category TEXT NOT NULL, -- 'code_generation', 'error_resolution', 'optimization', 'refactoring'
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Context Information
    component TEXT, -- Which system component triggered this
    file_path TEXT, -- File being worked on
    function_name TEXT, -- Function/method context
    line_number INTEGER,
    
    -- Decision/Action Information
    action_taken TEXT NOT NULL, -- What Copilot did/suggested
    reasoning TEXT, -- Why this action was taken
    confidence_score REAL DEFAULT 0.0, -- Copilot's confidence (0.0-1.0)
    
    -- Outcome Tracking
    outcome TEXT, -- 'success', 'failure', 'partial', 'pending'
    effectiveness_score REAL, -- How effective was this action (0.0-1.0)
    user_feedback TEXT, -- 'accepted', 'rejected', 'modified'
    
    -- Learning Metadata
    pattern_ids TEXT, -- JSON array of related pattern IDs
    similar_events TEXT, -- JSON array of similar event IDs
    learning_weight REAL DEFAULT 1.0, -- How much to weight this for learning
    
    -- Performance Metrics
    response_time_ms INTEGER,
    tokens_processed INTEGER,
    memory_usage_mb REAL,
    
    -- Additional Context
    context_data TEXT, -- JSON blob for additional context
    tags TEXT, -- Comma-separated tags for classification
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES copilot_sessions(session_id)
)
```


### error_patterns

**Rows**: 0  
**Columns**: 21

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| pattern_id | TEXT | Yes | None | Yes |
| error_type | TEXT | No | None | No |
| error_category | TEXT | No | None | No |
| error_signature | TEXT | No | None | No |
| error_message_pattern | TEXT | Yes | None | No |
| error_context_pattern | TEXT | Yes | None | No |
| first_seen | DATETIME | No | None | No |
| last_seen | DATETIME | Yes | CURRENT_TIMESTAMP | No |
| occurrence_count | INTEGER | Yes | 1 | No |
| typical_solutions | TEXT | No | None | No |
| resolution_success_rate | REAL | Yes | 0.0 | No |
| average_resolution_time_minutes | REAL | Yes | None | No |
| common_triggers | TEXT | Yes | None | No |
| prevention_strategies | TEXT | Yes | None | No |
| related_components | TEXT | Yes | None | No |
| learning_priority | INTEGER | Yes | 1 | No |
| pattern_confidence | REAL | Yes | 0.0 | No |
| severity_level | TEXT | Yes | 'medium' | No |
| performance_impact | TEXT | Yes | None | No |
| created_at | DATETIME | Yes | CURRENT_TIMESTAMP | No |
| updated_at | DATETIME | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE error_patterns (
    pattern_id TEXT PRIMARY KEY,
    error_type TEXT NOT NULL, -- 'syntax', 'runtime', 'logic', 'import', 'type'
    error_category TEXT NOT NULL, -- 'python', 'javascript', 'sql', 'config'
    
    -- Error Identification
    error_signature TEXT NOT NULL, -- Unique identifier/hash of error pattern
    error_message_pattern TEXT, -- Regex or pattern for matching error messages
    error_context_pattern TEXT, -- Pattern for context where this error occurs
    
    -- Occurrence Tracking
    first_seen DATETIME NOT NULL,
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    occurrence_count INTEGER DEFAULT 1,
    
    -- Resolution Information
    typical_solutions TEXT NOT NULL, -- JSON array of common solutions
    resolution_success_rate REAL DEFAULT 0.0,
    average_resolution_time_minutes REAL,
    
    -- Pattern Analysis
    common_triggers TEXT, -- What typically causes this error
    prevention_strategies TEXT, -- How to prevent this error
    related_components TEXT, -- Which system components are affected
    
    -- Learning Metadata
    learning_priority INTEGER DEFAULT 1, -- 1=low, 5=critical
    pattern_confidence REAL DEFAULT 0.0, -- How confident we are in this pattern
    
    -- Performance Impact
    severity_level TEXT DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    performance_impact TEXT, -- Description of performance impact
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```


### change_tracking

**Rows**: 0  
**Columns**: 28

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| change_id | TEXT | Yes | None | Yes |
| session_id | TEXT | Yes | None | No |
| event_id | TEXT | Yes | None | No |
| change_type | TEXT | No | None | No |
| change_scope | TEXT | No | None | No |
| change_category | TEXT | Yes | None | No |
| file_path | TEXT | No | None | No |
| file_type | TEXT | Yes | None | No |
| lines_added | INTEGER | Yes | 0 | No |
| lines_removed | INTEGER | Yes | 0 | No |
| lines_modified | INTEGER | Yes | 0 | No |
| complexity_delta | REAL | Yes | None | No |
| before_content | TEXT | Yes | None | No |
| after_content | TEXT | Yes | None | No |
| diff_content | TEXT | Yes | None | No |
| affected_functions | TEXT | Yes | None | No |
| affected_components | TEXT | Yes | None | No |
| breaking_change | BOOLEAN | Yes | FALSE | No |
| code_quality_score_before | REAL | Yes | None | No |
| code_quality_score_after | REAL | Yes | None | No |
| test_coverage_before | REAL | Yes | None | No |
| test_coverage_after | REAL | Yes | None | No |
| change_effectiveness | REAL | Yes | None | No |
| side_effects | TEXT | Yes | None | No |
| rollback_required | BOOLEAN | Yes | FALSE | No |
| triggered_by | TEXT | Yes | None | No |
| learning_value | REAL | Yes | 1.0 | No |
| timestamp | DATETIME | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE change_tracking (
    change_id TEXT PRIMARY KEY,
    session_id TEXT,
    event_id TEXT, -- Link to copilot_learning_events if applicable
    
    -- Change Classification
    change_type TEXT NOT NULL, -- 'addition', 'modification', 'deletion', 'refactor', 'optimization'
    change_scope TEXT NOT NULL, -- 'function', 'class', 'module', 'config', 'documentation'
    change_category TEXT, -- 'bug_fix', 'feature', 'optimization', 'maintenance'
    
    -- File Information
    file_path TEXT NOT NULL,
    file_type TEXT, -- Extension or file type
    
    -- Change Details
    lines_added INTEGER DEFAULT 0,
    lines_removed INTEGER DEFAULT 0,
    lines_modified INTEGER DEFAULT 0,
    complexity_delta REAL, -- Change in code complexity
    
    -- Before/After Context
    before_content TEXT, -- Code before change
    after_content TEXT, -- Code after change
    diff_content TEXT, -- Unified diff format
    
    -- Impact Analysis
    affected_functions TEXT, -- JSON array of affected function names
    affected_components TEXT, -- JSON array of affected system components
    breaking_change BOOLEAN DEFAULT FALSE,
    
    -- Quality Metrics
    code_quality_score_before REAL,
    code_quality_score_after REAL,
    test_coverage_before REAL,
    test_coverage_after REAL,
    
    -- Effectiveness Tracking
    change_effectiveness REAL, -- How effective was this change (0.0-1.0)
    side_effects TEXT, -- Any unintended consequences
    rollback_required BOOLEAN DEFAULT FALSE,
    
    -- Learning Metadata
    triggered_by TEXT, -- What caused this change ('copilot_suggestion', 'user_input', 'automated')
    learning_value REAL DEFAULT 1.0, -- How valuable this change is for learning
    
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES copilot_sessions(session_id),
    FOREIGN KEY (event_id) REFERENCES copilot_learning_events(event_id)
)
```


### todo_fixme_tracking

**Rows**: 0  
**Columns**: 28

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| item_id | TEXT | Yes | None | Yes |
| session_id | TEXT | Yes | None | No |
| item_type | TEXT | No | None | No |
| priority_level | TEXT | Yes | 'medium' | No |
| category | TEXT | Yes | None | No |
| file_path | TEXT | No | None | No |
| line_number | INTEGER | No | None | No |
| function_context | TEXT | Yes | None | No |
| class_context | TEXT | Yes | None | No |
| original_text | TEXT | No | None | No |
| description | TEXT | Yes | None | No |
| estimated_effort | TEXT | Yes | None | No |
| status | TEXT | Yes | 'open' | No |
| assigned_to | TEXT | Yes | None | No |
| created_date | DATETIME | Yes | CURRENT_TIMESTAMP | No |
| resolved_date | DATETIME | Yes | None | No |
| resolution_method | TEXT | Yes | None | No |
| resolution_code_changes | TEXT | Yes | None | No |
| resolution_effectiveness | REAL | Yes | None | No |
| similar_items | TEXT | Yes | None | No |
| common_patterns | TEXT | Yes | None | No |
| root_cause | TEXT | Yes | None | No |
| business_impact | TEXT | Yes | None | No |
| technical_debt_score | REAL | Yes | None | No |
| urgency_score | REAL | Yes | None | No |
| learning_insights | TEXT | Yes | None | No |
| prevention_strategies | TEXT | Yes | None | No |
| last_updated | DATETIME | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE todo_fixme_tracking (
    item_id TEXT PRIMARY KEY,
    session_id TEXT,
    
    -- Item Classification
    item_type TEXT NOT NULL, -- 'TODO', 'FIXME', 'HACK', 'NOTE', 'BUG'
    priority_level TEXT DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    category TEXT, -- 'performance', 'security', 'maintainability', 'feature'
    
    -- Location Information
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    function_context TEXT,
    class_context TEXT,
    
    -- Content Information
    original_text TEXT NOT NULL, -- The original TODO/FIXME comment
    description TEXT, -- Parsed/cleaned description
    estimated_effort TEXT, -- 'small', 'medium', 'large', 'epic'
    
    -- Tracking Information
    status TEXT DEFAULT 'open', -- 'open', 'in_progress', 'resolved', 'wontfix', 'duplicate'
    assigned_to TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_date DATETIME,
    
    -- Resolution Information
    resolution_method TEXT, -- How was this resolved
    resolution_code_changes TEXT, -- Changes made to resolve
    resolution_effectiveness REAL, -- How effective was the resolution
    
    -- Pattern Analysis
    similar_items TEXT, -- JSON array of similar TODO/FIXME IDs
    common_patterns TEXT, -- Patterns this item fits into
    root_cause TEXT, -- What typically causes this type of issue
    
    -- Impact Assessment
    business_impact TEXT, -- Impact on business logic
    technical_debt_score REAL, -- Technical debt score (0.0-1.0)
    urgency_score REAL, -- How urgent is this item (0.0-1.0)
    
    -- Learning Metadata
    learning_insights TEXT, -- What can we learn from this item
    prevention_strategies TEXT, -- How to prevent similar items
    
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES copilot_sessions(session_id)
)
```


### feedback_loops

**Rows**: 0  
**Columns**: 22

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| feedback_id | TEXT | Yes | None | Yes |
| loop_type | TEXT | No | None | No |
| source_event_id | TEXT | Yes | None | No |
| source_component | TEXT | Yes | None | No |
| source_session_id | TEXT | Yes | None | No |
| feedback_type | TEXT | No | None | No |
| feedback_content | TEXT | No | None | No |
| feedback_score | REAL | Yes | None | No |
| context_data | TEXT | Yes | None | No |
| environment_info | TEXT | Yes | None | No |
| user_persona | TEXT | Yes | None | No |
| processed | BOOLEAN | Yes | FALSE | No |
| processing_result | TEXT | Yes | None | No |
| processing_effectiveness | REAL | Yes | None | No |
| learning_applied | BOOLEAN | Yes | FALSE | No |
| learning_changes | TEXT | Yes | None | No |
| improvement_metrics | TEXT | Yes | None | No |
| feedback_timestamp | DATETIME | Yes | CURRENT_TIMESTAMP | No |
| processed_timestamp | DATETIME | Yes | None | No |
| applied_timestamp | DATETIME | Yes | None | No |
| feedback_validity | REAL | Yes | 1.0 | No |
| confidence_level | REAL | Yes | 0.5 | No |

#### SQL Definition
```sql
CREATE TABLE feedback_loops (
    feedback_id TEXT PRIMARY KEY,
    loop_type TEXT NOT NULL, -- 'user_feedback', 'automated_validation', 'performance_metrics', 'error_analysis'
    
    -- Source Information
    source_event_id TEXT, -- Related copilot_learning_events ID
    source_component TEXT, -- Which component generated this feedback
    source_session_id TEXT,
    
    -- Feedback Content
    feedback_type TEXT NOT NULL, -- 'positive', 'negative', 'neutral', 'suggestion'
    feedback_content TEXT NOT NULL, -- The actual feedback
    feedback_score REAL, -- Numerical score if applicable (-1.0 to 1.0)
    
    -- Context Information
    context_data TEXT, -- JSON blob with context
    environment_info TEXT, -- Environment where feedback was generated
    user_persona TEXT, -- Type of user providing feedback
    
    -- Processing Information
    processed BOOLEAN DEFAULT FALSE,
    processing_result TEXT, -- What action was taken based on this feedback
    processing_effectiveness REAL, -- How effective was the processing
    
    -- Learning Application
    learning_applied BOOLEAN DEFAULT FALSE,
    learning_changes TEXT, -- What changes were made based on this feedback
    improvement_metrics TEXT, -- Metrics showing improvement
    
    -- Temporal Information
    feedback_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed_timestamp DATETIME,
    applied_timestamp DATETIME,
    
    -- Validation
    feedback_validity REAL DEFAULT 1.0, -- How valid/reliable is this feedback
    confidence_level REAL DEFAULT 0.5, -- Confidence in the feedback
    
    FOREIGN KEY (source_event_id) REFERENCES copilot_learning_events(event_id),
    FOREIGN KEY (source_session_id) REFERENCES copilot_sessions(session_id)
)
```


### pattern_effectiveness

**Rows**: 0  
**Columns**: 26

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| effectiveness_id | TEXT | Yes | None | Yes |
| pattern_id | TEXT | No | None | No |
| pattern_type | TEXT | No | None | No |
| total_applications | INTEGER | Yes | 0 | No |
| successful_applications | INTEGER | Yes | 0 | No |
| failed_applications | INTEGER | Yes | 0 | No |
| average_success_rate | REAL | Yes | 0.0 | No |
| average_response_time_ms | REAL | Yes | None | No |
| average_user_satisfaction | REAL | Yes | None | No |
| most_effective_contexts | TEXT | Yes | None | No |
| least_effective_contexts | TEXT | Yes | None | No |
| optimal_conditions | TEXT | Yes | None | No |
| performance_trend | TEXT | Yes | None | No |
| trend_data | TEXT | Yes | None | No |
| better_alternatives | TEXT | Yes | None | No |
| complementary_patterns | TEXT | Yes | None | No |
| key_success_factors | TEXT | Yes | None | No |
| common_failure_modes | TEXT | Yes | None | No |
| improvement_opportunities | TEXT | Yes | None | No |
| recommendation_score | REAL | Yes | 0.5 | No |
| recommendation_contexts | TEXT | Yes | None | No |
| first_measurement | DATETIME | Yes | CURRENT_TIMESTAMP | No |
| last_updated | DATETIME | Yes | CURRENT_TIMESTAMP | No |
| measurement_count | INTEGER | Yes | 0 | No |
| data_quality_score | REAL | Yes | 1.0 | No |
| statistical_confidence | REAL | Yes | 0.0 | No |

#### SQL Definition
```sql
CREATE TABLE pattern_effectiveness (
    effectiveness_id TEXT PRIMARY KEY,
    pattern_id TEXT NOT NULL, -- Links to pattern_database or quantum_patterns
    pattern_type TEXT NOT NULL,
    
    -- Usage Statistics
    total_applications INTEGER DEFAULT 0,
    successful_applications INTEGER DEFAULT 0,
    failed_applications INTEGER DEFAULT 0,
    
    -- Performance Metrics
    average_success_rate REAL DEFAULT 0.0,
    average_response_time_ms REAL,
    average_user_satisfaction REAL,
    
    -- Context Analysis
    most_effective_contexts TEXT, -- JSON array of contexts where this pattern works best
    least_effective_contexts TEXT, -- JSON array of contexts where this pattern fails
    optimal_conditions TEXT, -- Conditions for optimal performance
    
    -- Trend Analysis
    performance_trend TEXT, -- 'improving', 'declining', 'stable'
    trend_data TEXT, -- JSON array of historical performance data
    
    -- Comparative Analysis
    better_alternatives TEXT, -- JSON array of pattern IDs that perform better
    complementary_patterns TEXT, -- Patterns that work well with this one
    
    -- Learning Insights
    key_success_factors TEXT, -- What makes this pattern successful
    common_failure_modes TEXT, -- How this pattern typically fails
    improvement_opportunities TEXT, -- How to make this pattern better
    
    -- Recommendation Engine Data
    recommendation_score REAL DEFAULT 0.5, -- How often to recommend this pattern
    recommendation_contexts TEXT, -- When to recommend this pattern
    
    -- Temporal Tracking
    first_measurement DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    measurement_count INTEGER DEFAULT 0,
    
    -- Metadata
    data_quality_score REAL DEFAULT 1.0, -- Quality of the effectiveness data
    statistical_confidence REAL DEFAULT 0.0, -- Statistical confidence in metrics
    
    FOREIGN KEY (pattern_id) REFERENCES pattern_database(pattern_id)
)
```


### copilot_decision_tree

**Rows**: 0  
**Columns**: 20

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| decision_id | TEXT | Yes | None | Yes |
| parent_decision_id | TEXT | Yes | None | No |
| event_id | TEXT | No | None | No |
| decision_point | TEXT | No | None | No |
| available_options | TEXT | No | None | No |
| chosen_option | TEXT | No | None | No |
| evaluation_criteria | TEXT | Yes | None | No |
| option_scores | TEXT | Yes | None | No |
| decision_algorithm | TEXT | Yes | None | No |
| decision_confidence | REAL | No | None | No |
| uncertainty_factors | TEXT | Yes | None | No |
| risk_assessment | TEXT | Yes | None | No |
| expected_outcome | TEXT | Yes | None | No |
| actual_outcome | TEXT | Yes | None | No |
| outcome_match_score | REAL | Yes | None | No |
| decision_quality | REAL | Yes | None | No |
| learning_insights | TEXT | Yes | None | No |
| would_decide_differently | TEXT | Yes | None | No |
| decision_timestamp | DATETIME | Yes | CURRENT_TIMESTAMP | No |
| outcome_timestamp | DATETIME | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE copilot_decision_tree (
    decision_id TEXT PRIMARY KEY,
    parent_decision_id TEXT, -- For hierarchical decisions
    event_id TEXT NOT NULL, -- Links to copilot_learning_events
    
    -- Decision Context
    decision_point TEXT NOT NULL, -- What decision was being made
    available_options TEXT NOT NULL, -- JSON array of available options
    chosen_option TEXT NOT NULL, -- Which option was chosen
    
    -- Decision Criteria
    evaluation_criteria TEXT, -- JSON object with criteria and weights
    option_scores TEXT, -- JSON object with scores for each option
    decision_algorithm TEXT, -- Which algorithm/method was used
    
    -- Confidence and Uncertainty
    decision_confidence REAL NOT NULL, -- Confidence in the decision (0.0-1.0)
    uncertainty_factors TEXT, -- What made this decision uncertain
    risk_assessment TEXT, -- Assessed risks of the decision
    
    -- Outcome Tracking
    expected_outcome TEXT, -- What was expected to happen
    actual_outcome TEXT, -- What actually happened
    outcome_match_score REAL, -- How well actual matched expected (0.0-1.0)
    
    -- Learning Value
    decision_quality REAL, -- Quality assessment of the decision (0.0-1.0)
    learning_insights TEXT, -- What was learned from this decision
    would_decide_differently TEXT, -- How to improve this decision in future
    
    -- Timing Information
    decision_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    outcome_timestamp DATETIME,
    
    FOREIGN KEY (parent_decision_id) REFERENCES copilot_decision_tree(decision_id),
    FOREIGN KEY (event_id) REFERENCES copilot_learning_events(event_id)
)
```


### sqlite_stat1

**Rows**: 7  
**Columns**: 3

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| tbl |  | Yes | None | No |
| idx |  | Yes | None | No |
| stat |  | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE sqlite_stat1(tbl,idx,stat)
```


### environment_configs

**Rows**: 0  
**Columns**: 7

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| config_id | TEXT | Yes | None | Yes |
| environment_name | TEXT | No | None | No |
| environment_type | TEXT | No | None | No |
| configuration_data | TEXT | No | None | No |
| deployment_patterns | TEXT | Yes | None | No |
| validation_rules | TEXT | Yes | None | No |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE environment_configs (
            config_id TEXT PRIMARY KEY,
            environment_name TEXT NOT NULL,
            environment_type TEXT NOT NULL,
            configuration_data TEXT NOT NULL,
            deployment_patterns TEXT,
            validation_rules TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
```


### template_effectiveness

**Rows**: 0  
**Columns**: 7

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| effectiveness_id | TEXT | Yes | None | Yes |
| template_id | TEXT | Yes | None | No |
| usage_context | TEXT | Yes | None | No |
| success_rate | REAL | Yes | 0.0 | No |
| performance_metrics | TEXT | Yes | None | No |
| user_feedback | TEXT | Yes | None | No |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE template_effectiveness (
            effectiveness_id TEXT PRIMARY KEY,
            template_id TEXT,
            usage_context TEXT,
            success_rate REAL DEFAULT 0.0,
            performance_metrics TEXT,
            user_feedback TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (template_id) REFERENCES script_templates (template_id)
        )
```


### generation_history

**Rows**: 0  
**Columns**: 8

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| generation_id | TEXT | Yes | None | Yes |
| template_id | TEXT | Yes | None | No |
| environment_id | TEXT | Yes | None | No |
| generated_content | TEXT | Yes | None | No |
| generation_parameters | TEXT | Yes | None | No |
| success_status | TEXT | Yes | None | No |
| execution_results | TEXT | Yes | None | No |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE generation_history (
            generation_id TEXT PRIMARY KEY,
            template_id TEXT,
            environment_id TEXT,
            generated_content TEXT,
            generation_parameters TEXT,
            success_status TEXT,
            execution_results TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (template_id) REFERENCES script_templates (template_id)
        )
```


### codebase_analysis

**Rows**: 1  
**Columns**: 8

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| analysis_id | TEXT | Yes | None | Yes |
| analysis_timestamp | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| total_scripts_analyzed | INTEGER | Yes | None | No |
| patterns_extracted | TEXT | Yes | None | No |
| dependency_graph | TEXT | Yes | None | No |
| complexity_metrics | TEXT | Yes | None | No |
| enterprise_compliance_score | REAL | Yes | None | No |
| analysis_metadata | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE codebase_analysis (
            analysis_id TEXT PRIMARY KEY,
            analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_scripts_analyzed INTEGER,
            patterns_extracted TEXT,
            dependency_graph TEXT,
            complexity_metrics TEXT,
            enterprise_compliance_score REAL,
            analysis_metadata TEXT
        )
```


### script_metadata

**Rows**: 62  
**Columns**: 15

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| filepath | TEXT | Yes | None | No |
| filename | TEXT | Yes | None | No |
| size_bytes | INTEGER | Yes | None | No |
| lines_of_code | INTEGER | Yes | None | No |
| functions | TEXT | Yes | None | No |
| classes | TEXT | Yes | None | No |
| imports | TEXT | Yes | None | No |
| dependencies | TEXT | Yes | None | No |
| patterns | TEXT | Yes | None | No |
| database_connections | TEXT | Yes | None | No |
| complexity_score | INTEGER | Yes | None | No |
| last_modified | TEXT | Yes | None | No |
| category | TEXT | Yes | None | No |
| analysis_timestamp | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE script_metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filepath TEXT UNIQUE,
                        filename TEXT,
                        size_bytes INTEGER,
                        lines_of_code INTEGER,
                        functions TEXT,
                        classes TEXT,
                        imports TEXT,
                        dependencies TEXT,
                        patterns TEXT,
                        database_connections TEXT,
                        complexity_score INTEGER,
                        last_modified TEXT,
                        category TEXT,
                        analysis_timestamp TEXT
                    )
```


### template_patterns

**Rows**: 8  
**Columns**: 9

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| pattern_id | TEXT | Yes | None | No |
| pattern_type | TEXT | Yes | None | No |
| occurrence_count | INTEGER | Yes | None | No |
| files | TEXT | Yes | None | No |
| code_snippet | TEXT | Yes | None | No |
| variables | TEXT | Yes | None | No |
| description | TEXT | Yes | None | No |
| analysis_timestamp | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE template_patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pattern_id TEXT UNIQUE,
                        pattern_type TEXT,
                        occurrence_count INTEGER,
                        files TEXT,
                        code_snippet TEXT,
                        variables TEXT,
                        description TEXT,
                        analysis_timestamp TEXT
                    )
```


### template_variables

**Rows**: 0  
**Columns**: 9

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| template_id | INTEGER | No | None | No |
| variable_name | TEXT | No | None | No |
| variable_type | TEXT | No | None | No |
| default_value | TEXT | Yes | None | No |
| description | TEXT | Yes | None | No |
| required | BOOLEAN | Yes | 0 | No |
| validation_pattern | TEXT | Yes | None | No |
| example_value | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE template_variables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                variable_name TEXT NOT NULL,
                variable_type TEXT NOT NULL, -- string, integer, boolean, list, object
                default_value TEXT,
                description TEXT,
                required BOOLEAN DEFAULT 0,
                validation_pattern TEXT,
                example_value TEXT,
                FOREIGN KEY (template_id) REFERENCES script_templates (id)
            )
```


### template_dependencies

**Rows**: 0  
**Columns**: 7

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| template_id | INTEGER | No | None | No |
| dependency_type | TEXT | No | None | No |
| dependency_name | TEXT | No | None | No |
| version_requirement | TEXT | Yes | None | No |
| optional | BOOLEAN | Yes | 0 | No |
| description | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE template_dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                dependency_type TEXT NOT NULL, -- module, package, database, file
                dependency_name TEXT NOT NULL,
                version_requirement TEXT,
                optional BOOLEAN DEFAULT 0,
                description TEXT,
                FOREIGN KEY (template_id) REFERENCES script_templates (id)
            )
```


### environment_profiles

**Rows**: 3  
**Columns**: 11

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| profile_name | TEXT | No | None | No |
| description | TEXT | Yes | None | No |
| target_platform | TEXT | Yes | None | No |
| python_version | TEXT | Yes | None | No |
| enterprise_level | TEXT | Yes | None | No |
| compliance_requirements | TEXT | Yes | None | No |
| default_packages | TEXT | Yes | None | No |
| security_level | INTEGER | Yes | 1 | No |
| created_timestamp | TEXT | No | None | No |
| active | BOOLEAN | Yes | 1 | No |

#### SQL Definition
```sql
CREATE TABLE environment_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_name TEXT UNIQUE NOT NULL,
                description TEXT,
                target_platform TEXT, -- windows, linux, macos, cross-platform
                python_version TEXT,
                enterprise_level TEXT, -- development, staging, production
                compliance_requirements TEXT, -- JSON array
                default_packages TEXT, -- JSON array
                security_level INTEGER DEFAULT 1,
                created_timestamp TEXT NOT NULL,
                active BOOLEAN DEFAULT 1
            )
```


### environment_variables

**Rows**: 0  
**Columns**: 7

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| profile_id | INTEGER | No | None | No |
| variable_name | TEXT | No | None | No |
| variable_value | TEXT | Yes | None | No |
| variable_type | TEXT | Yes | 'string' | No |
| sensitive | BOOLEAN | Yes | 0 | No |
| description | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE environment_variables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER NOT NULL,
                variable_name TEXT NOT NULL,
                variable_value TEXT,
                variable_type TEXT DEFAULT 'string',
                sensitive BOOLEAN DEFAULT 0,
                description TEXT,
                FOREIGN KEY (profile_id) REFERENCES environment_profiles (id)
            )
```


### environment_adaptations

**Rows**: 0  
**Columns**: 6

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| source_template_id | INTEGER | No | None | No |
| target_environment_id | INTEGER | No | None | No |
| adaptation_rules | TEXT | Yes | None | No |
| success_rate | REAL | Yes | 0.0 | No |
| last_adaptation_timestamp | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE environment_adaptations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_template_id INTEGER NOT NULL,
                target_environment_id INTEGER NOT NULL,
                adaptation_rules TEXT, -- JSON object with transformation rules
                success_rate REAL DEFAULT 0.0,
                last_adaptation_timestamp TEXT,
                FOREIGN KEY (source_template_id) REFERENCES script_templates (id),
                FOREIGN KEY (target_environment_id) REFERENCES environment_profiles (id)
            )
```


### generation_sessions

**Rows**: 7  
**Columns**: 11

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| session_id | TEXT | No | None | No |
| user_prompt | TEXT | No | None | No |
| template_used_id | INTEGER | Yes | None | No |
| environment_profile_id | INTEGER | Yes | None | No |
| generation_mode | TEXT | Yes | None | No |
| success | BOOLEAN | Yes | 0 | No |
| output_file_path | TEXT | Yes | None | No |
| generation_timestamp | TEXT | No | None | No |
| completion_timestamp | TEXT | Yes | None | No |
| duration_seconds | REAL | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE generation_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                user_prompt TEXT NOT NULL,
                template_used_id INTEGER,
                environment_profile_id INTEGER,
                generation_mode TEXT, -- manual, assisted, automated
                success BOOLEAN DEFAULT 0,
                output_file_path TEXT,
                generation_timestamp TEXT NOT NULL,
                completion_timestamp TEXT,
                duration_seconds REAL,
                FOREIGN KEY (template_used_id) REFERENCES script_templates (id),
                FOREIGN KEY (environment_profile_id) REFERENCES environment_profiles (id)
            )
```


### generated_scripts

**Rows**: 5  
**Columns**: 12

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| session_id | TEXT | No | None | No |
| script_name | TEXT | No | None | No |
| script_path | TEXT | No | None | No |
| content_hash | TEXT | Yes | None | No |
| lines_of_code | INTEGER | Yes | None | No |
| functions_count | INTEGER | Yes | None | No |
| classes_count | INTEGER | Yes | None | No |
| complexity_score | INTEGER | Yes | None | No |
| validation_status | TEXT | Yes | 'pending' | No |
| execution_status | TEXT | Yes | 'not_tested' | No |
| file_size_bytes | INTEGER | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE generated_scripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                script_name TEXT NOT NULL,
                script_path TEXT NOT NULL,
                content_hash TEXT UNIQUE,
                lines_of_code INTEGER,
                functions_count INTEGER,
                classes_count INTEGER,
                complexity_score INTEGER,
                validation_status TEXT DEFAULT 'pending', -- pending, passed, failed
                execution_status TEXT DEFAULT 'not_tested', -- not_tested, success, failed
                file_size_bytes INTEGER,
                FOREIGN KEY (session_id) REFERENCES generation_sessions (session_id)
            )
```


### generation_logs

**Rows**: 0  
**Columns**: 7

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| session_id | TEXT | No | None | No |
| log_level | TEXT | No | None | No |
| message | TEXT | No | None | No |
| timestamp | TEXT | No | None | No |
| component | TEXT | Yes | None | No |
| details | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE generation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                log_level TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                component TEXT,
                details TEXT, -- JSON object with additional details
                FOREIGN KEY (session_id) REFERENCES generation_sessions (session_id)
            )
```


### user_feedback

**Rows**: 0  
**Columns**: 10

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| session_id | TEXT | No | None | No |
| script_id | INTEGER | Yes | None | No |
| template_id | INTEGER | Yes | None | No |
| satisfaction_rating | INTEGER | Yes | None | No |
| quality_rating | INTEGER | Yes | None | No |
| usefulness_rating | INTEGER | Yes | None | No |
| feedback_text | TEXT | Yes | None | No |
| suggestions | TEXT | Yes | None | No |
| timestamp | TEXT | No | None | No |

#### SQL Definition
```sql
CREATE TABLE user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                script_id INTEGER,
                template_id INTEGER,
                satisfaction_rating INTEGER, -- 1-5 scale
                quality_rating INTEGER, -- 1-5 scale
                usefulness_rating INTEGER, -- 1-5 scale
                feedback_text TEXT,
                suggestions TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES generation_sessions (session_id),
                FOREIGN KEY (script_id) REFERENCES generated_scripts (id),
                FOREIGN KEY (template_id) REFERENCES script_templates (id)
            )
```


### performance_metrics

**Rows**: 0  
**Columns**: 7

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| metric_type | TEXT | No | None | No |
| metric_value | REAL | No | None | No |
| session_id | TEXT | Yes | None | No |
| template_id | INTEGER | Yes | None | No |
| timestamp | TEXT | No | None | No |
| context | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_type TEXT NOT NULL, -- generation_time, memory_usage, cpu_usage
                metric_value REAL NOT NULL,
                session_id TEXT,
                template_id INTEGER,
                timestamp TEXT NOT NULL,
                context TEXT, -- JSON object with additional context
                FOREIGN KEY (session_id) REFERENCES generation_sessions (session_id),
                FOREIGN KEY (template_id) REFERENCES script_templates (id)
            )
```


### copilot_contexts

**Rows**: 15  
**Columns**: 10

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| context_name | TEXT | No | None | No |
| context_type | TEXT | No | None | No |
| context_content | TEXT | No | None | No |
| usage_instructions | TEXT | Yes | None | No |
| effectiveness_score | REAL | Yes | 0.0 | No |
| usage_count | INTEGER | Yes | 0 | No |
| created_timestamp | TEXT | No | None | No |
| updated_timestamp | TEXT | No | None | No |
| active | BOOLEAN | Yes | 1 | No |

#### SQL Definition
```sql
CREATE TABLE copilot_contexts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                context_name TEXT UNIQUE NOT NULL,
                context_type TEXT NOT NULL, -- template, pattern, example
                context_content TEXT NOT NULL,
                usage_instructions TEXT,
                effectiveness_score REAL DEFAULT 0.0,
                usage_count INTEGER DEFAULT 0,
                created_timestamp TEXT NOT NULL,
                updated_timestamp TEXT NOT NULL,
                active BOOLEAN DEFAULT 1
            )
```


### copilot_suggestions

**Rows**: 3  
**Columns**: 8

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| session_id | TEXT | No | None | No |
| suggestion_type | TEXT | No | None | No |
| suggestion_content | TEXT | No | None | No |
| confidence_score | REAL | Yes | 0.0 | No |
| accepted | BOOLEAN | Yes | 0 | No |
| timestamp | TEXT | No | None | No |
| context_used | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE copilot_suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                suggestion_type TEXT NOT NULL, -- completion, template, pattern
                suggestion_content TEXT NOT NULL,
                confidence_score REAL DEFAULT 0.0,
                accepted BOOLEAN DEFAULT 0,
                timestamp TEXT NOT NULL,
                context_used TEXT, -- JSON array of context IDs
                FOREIGN KEY (session_id) REFERENCES generation_sessions (session_id)
            )
```


### copilot_analytics

**Rows**: 0  
**Columns**: 7

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| metric_name | TEXT | No | None | No |
| metric_value | REAL | No | None | No |
| session_id | TEXT | Yes | None | No |
| template_id | INTEGER | Yes | None | No |
| timestamp | TEXT | No | None | No |
| details | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE copilot_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                session_id TEXT,
                template_id INTEGER,
                timestamp TEXT NOT NULL,
                details TEXT, -- JSON object
                FOREIGN KEY (session_id) REFERENCES generation_sessions (session_id),
                FOREIGN KEY (template_id) REFERENCES script_templates (id)
            )
```


### compliance_checks

**Rows**: 4  
**Columns**: 10

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| check_name | TEXT | No | None | No |
| check_type | TEXT | No | None | No |
| target_type | TEXT | No | None | No |
| target_id | TEXT | No | None | No |
| check_result | TEXT | No | None | No |
| details | TEXT | Yes | None | No |
| timestamp | TEXT | No | None | No |
| auto_fix_attempted | BOOLEAN | Yes | 0 | No |
| auto_fix_success | BOOLEAN | Yes | 0 | No |

#### SQL Definition
```sql
CREATE TABLE compliance_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                check_name TEXT NOT NULL,
                check_type TEXT NOT NULL, -- anti_recursion, enterprise, dual_copilot
                target_type TEXT NOT NULL, -- template, generated_script, session
                target_id TEXT NOT NULL,
                check_result TEXT NOT NULL, -- passed, failed, warning
                details TEXT,
                timestamp TEXT NOT NULL,
                auto_fix_attempted BOOLEAN DEFAULT 0,
                auto_fix_success BOOLEAN DEFAULT 0
            )
```


### anti_recursion_tracking

**Rows**: 0  
**Columns**: 8

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| operation_type | TEXT | No | None | No |
| resource_path | TEXT | No | None | No |
| access_count | INTEGER | Yes | 1 | No |
| last_access_timestamp | TEXT | No | None | No |
| blocked | BOOLEAN | Yes | 0 | No |
| session_id | TEXT | Yes | None | No |
| details | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE anti_recursion_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT NOT NULL,
                resource_path TEXT NOT NULL,
                access_count INTEGER DEFAULT 1,
                last_access_timestamp TEXT NOT NULL,
                blocked BOOLEAN DEFAULT 0,
                session_id TEXT,
                details TEXT -- JSON object
            )
```


### compliance_patterns

**Rows**: 4  
**Columns**: 9

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| pattern_name | TEXT | No | None | No |
| pattern_type | TEXT | No | None | No |
| pattern_regex | TEXT | Yes | None | No |
| description | TEXT | Yes | None | No |
| severity | TEXT | Yes | 'medium' | No |
| auto_fix_available | BOOLEAN | Yes | 0 | No |
| auto_fix_pattern | TEXT | Yes | None | No |
| active | BOOLEAN | Yes | 1 | No |

#### SQL Definition
```sql
CREATE TABLE compliance_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_name TEXT UNIQUE NOT NULL,
                pattern_type TEXT NOT NULL,
                pattern_regex TEXT,
                description TEXT,
                severity TEXT DEFAULT 'medium', -- low, medium, high, critical
                auto_fix_available BOOLEAN DEFAULT 0,
                auto_fix_pattern TEXT,
                active BOOLEAN DEFAULT 1
            )
```


### script_templates

**Rows**: 11  
**Columns**: 16

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| template_name | TEXT | No | None | No |
| template_type | TEXT | No | 'script' | No |
| category | TEXT | No | None | No |
| description | TEXT | Yes | None | No |
| base_template | TEXT | No | None | No |
| variables | TEXT | Yes | '[]' | No |
| dependencies | TEXT | Yes | '[]' | No |
| compliance_patterns | TEXT | Yes | '[]' | No |
| complexity_level | INTEGER | Yes | 1 | No |
| author | TEXT | Yes | 'Enterprise Framework' | No |
| version | TEXT | Yes | '1.0.0' | No |
| tags | TEXT | Yes | '[]' | No |
| created_timestamp | TEXT | No | None | No |
| updated_timestamp | TEXT | No | None | No |
| active | BOOLEAN | Yes | 1 | No |

#### SQL Definition
```sql
CREATE TABLE script_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_name TEXT UNIQUE NOT NULL,
                template_type TEXT NOT NULL DEFAULT 'script',
                category TEXT NOT NULL,
                description TEXT,
                base_template TEXT NOT NULL,
                variables TEXT DEFAULT '[]',
                dependencies TEXT DEFAULT '[]',
                compliance_patterns TEXT DEFAULT '[]',
                complexity_level INTEGER DEFAULT 1,
                author TEXT DEFAULT 'Enterprise Framework',
                version TEXT DEFAULT '1.0.0',
                tags TEXT DEFAULT '[]',
                created_timestamp TEXT NOT NULL,
                updated_timestamp TEXT NOT NULL,
                active BOOLEAN DEFAULT 1
            )
```


### advanced_script_analysis

**Rows**: 0  
**Columns**: 10

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| script_path | TEXT | No | None | No |
| ast_complexity_score | REAL | Yes | None | No |
| pattern_fingerprint | TEXT | Yes | None | No |
| dependency_graph | TEXT | Yes | None | No |
| template_similarity_score | REAL | Yes | None | No |
| environment_compatibility | TEXT | Yes | None | No |
| generation_potential | REAL | Yes | None | No |
| last_analyzed | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE advanced_script_analysis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        script_path TEXT UNIQUE NOT NULL,
                        ast_complexity_score REAL,
                        pattern_fingerprint TEXT,
                        dependency_graph TEXT,
                        template_similarity_score REAL,
                        environment_compatibility TEXT,
                        generation_potential REAL,
                        last_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
```


### environment_adaptation_rules

**Rows**: 4  
**Columns**: 9

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| rule_name | TEXT | No | None | No |
| source_pattern | TEXT | No | None | No |
| target_pattern | TEXT | No | None | No |
| environment_filter | TEXT | Yes | None | No |
| transformation_logic | TEXT | Yes | None | No |
| priority | INTEGER | Yes | 0 | No |
| active | BOOLEAN | Yes | TRUE | No |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE environment_adaptation_rules (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        rule_name TEXT UNIQUE NOT NULL,
                        source_pattern TEXT NOT NULL,
                        target_pattern TEXT NOT NULL,
                        environment_filter TEXT,
                        transformation_logic TEXT,
                        priority INTEGER DEFAULT 0,
                        active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
```


### copilot_integration_sessions

**Rows**: 0  
**Columns**: 10

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| session_id | TEXT | No | None | No |
| request_type | TEXT | No | None | No |
| context_data | TEXT | Yes | None | No |
| template_used | TEXT | Yes | None | No |
| generated_content | TEXT | Yes | None | No |
| user_feedback | TEXT | Yes | None | No |
| effectiveness_score | REAL | Yes | None | No |
| environment | TEXT | Yes | None | No |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE copilot_integration_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE NOT NULL,
                        request_type TEXT NOT NULL,
                        context_data TEXT,
                        template_used TEXT,
                        generated_content TEXT,
                        user_feedback TEXT,
                        effectiveness_score REAL,
                        environment TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
```


### template_usage_analytics

**Rows**: 4  
**Columns**: 8

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| template_id | TEXT | No | None | No |
| usage_timestamp | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |
| environment | TEXT | Yes | None | No |
| success_rate | REAL | Yes | None | No |
| generation_time_ms | INTEGER | Yes | None | No |
| user_satisfaction | INTEGER | Yes | None | No |
| customizations_applied | TEXT | Yes | None | No |

#### SQL Definition
```sql
CREATE TABLE template_usage_analytics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        template_id TEXT NOT NULL,
                        usage_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        environment TEXT,
                        success_rate REAL,
                        generation_time_ms INTEGER,
                        user_satisfaction INTEGER,
                        customizations_applied TEXT,
                        FOREIGN KEY (template_id) REFERENCES script_templates(template_name)
                    )
```


### filesystem_sync_log

**Rows**: 72  
**Columns**: 7

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| sync_session_id | TEXT | No | None | No |
| action_type | TEXT | No | None | No |
| file_path | TEXT | No | None | No |
| status | TEXT | No | None | No |
| error_message | TEXT | Yes | None | No |
| sync_timestamp | TIMESTAMP | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE filesystem_sync_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sync_session_id TEXT NOT NULL,
                        action_type TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        status TEXT NOT NULL,
                        error_message TEXT,
                        sync_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
```


### shared_templates

**Rows**: 0  
**Columns**: 7

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| template_id | TEXT | No | None | No |
| source_database | TEXT | No | None | No |
| template_content | TEXT | No | None | No |
| placeholder_mapping | TEXT | Yes | None | No |
| sync_timestamp | DATETIME | Yes | CURRENT_TIMESTAMP | No |
| sync_status | TEXT | Yes | 'active' | No |

#### SQL Definition
```sql
CREATE TABLE shared_templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        template_id TEXT NOT NULL,
                        source_database TEXT NOT NULL,
                        template_content TEXT NOT NULL,
                        placeholder_mapping TEXT, -- JSON
                        sync_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        sync_status TEXT DEFAULT 'active'
                    )
```


### shared_placeholders

**Rows**: 60  
**Columns**: 7

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| placeholder_name | TEXT | No | None | No |
| placeholder_type | TEXT | No | None | No |
| category | TEXT | No | None | No |
| source_database | TEXT | Yes | 'learning_monitor' | No |
| local_override | TEXT | Yes | None | No |
| sync_timestamp | DATETIME | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE shared_placeholders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        placeholder_name TEXT NOT NULL,
                        placeholder_type TEXT NOT NULL,
                        category TEXT NOT NULL,
                        source_database TEXT DEFAULT 'learning_monitor',
                        local_override TEXT,
                        sync_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
```


## Relationships

- **copilot_learning_events.session_id** → **copilot_sessions.session_id** (FOREIGN_KEY)
- **change_tracking.event_id** → **copilot_learning_events.event_id** (FOREIGN_KEY)
- **change_tracking.session_id** → **copilot_sessions.session_id** (FOREIGN_KEY)
- **todo_fixme_tracking.session_id** → **copilot_sessions.session_id** (FOREIGN_KEY)
- **feedback_loops.source_session_id** → **copilot_sessions.session_id** (FOREIGN_KEY)
- **feedback_loops.source_event_id** → **copilot_learning_events.event_id** (FOREIGN_KEY)
- **pattern_effectiveness.pattern_id** → **pattern_database.pattern_id** (FOREIGN_KEY)
- **copilot_decision_tree.event_id** → **copilot_learning_events.event_id** (FOREIGN_KEY)
- **copilot_decision_tree.parent_decision_id** → **copilot_decision_tree.decision_id** (FOREIGN_KEY)
- **template_effectiveness.template_id** → **script_templates.template_id** (FOREIGN_KEY)
- **generation_history.template_id** → **script_templates.template_id** (FOREIGN_KEY)
- **template_variables.template_id** → **script_templates.id** (FOREIGN_KEY)
- **template_dependencies.template_id** → **script_templates.id** (FOREIGN_KEY)
- **environment_variables.profile_id** → **environment_profiles.id** (FOREIGN_KEY)
- **environment_adaptations.target_environment_id** → **environment_profiles.id** (FOREIGN_KEY)
- **environment_adaptations.source_template_id** → **script_templates.id** (FOREIGN_KEY)
- **generation_sessions.environment_profile_id** → **environment_profiles.id** (FOREIGN_KEY)
- **generation_sessions.template_used_id** → **script_templates.id** (FOREIGN_KEY)
- **generated_scripts.session_id** → **generation_sessions.session_id** (FOREIGN_KEY)
- **generation_logs.session_id** → **generation_sessions.session_id** (FOREIGN_KEY)
- **user_feedback.template_id** → **script_templates.id** (FOREIGN_KEY)
- **user_feedback.script_id** → **generated_scripts.id** (FOREIGN_KEY)
- **user_feedback.session_id** → **generation_sessions.session_id** (FOREIGN_KEY)
- **performance_metrics.template_id** → **script_templates.id** (FOREIGN_KEY)
- **performance_metrics.session_id** → **generation_sessions.session_id** (FOREIGN_KEY)
- **copilot_suggestions.session_id** → **generation_sessions.session_id** (FOREIGN_KEY)
- **copilot_analytics.template_id** → **script_templates.id** (FOREIGN_KEY)
- **copilot_analytics.session_id** → **generation_sessions.session_id** (FOREIGN_KEY)
- **template_usage_analytics.template_id** → **script_templates.template_name** (FOREIGN_KEY)
