# Entity-Relationship Diagram: production.db

## Database Overview
- **Database Name**: production.db
- **Total Tables**: 44
- **Total Relationships**: 29
- **Generated**: 2025-07-03 05:53:03

## Table Definitions

### file_system_mapping

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

### validation_sessions

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

### environment_configs

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

```sql
CREATE TABLE generated_scripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                script_name TEXT NOT NULL,
                script_content TEXT NOT NULL,
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

| From Table | From Column | To Table | To Column |
|------------|-------------|----------|----------|
| copilot_learning_events | session_id | copilot_sessions | session_id |
| change_tracking | event_id | copilot_learning_events | event_id |
| change_tracking | session_id | copilot_sessions | session_id |
| todo_fixme_tracking | session_id | copilot_sessions | session_id |
| feedback_loops | source_session_id | copilot_sessions | session_id |
| feedback_loops | source_event_id | copilot_learning_events | event_id |
| pattern_effectiveness | pattern_id | pattern_database | pattern_id |
| copilot_decision_tree | event_id | copilot_learning_events | event_id |
| copilot_decision_tree | parent_decision_id | copilot_decision_tree | decision_id |
| template_effectiveness | template_id | script_templates | template_id |
| generation_history | template_id | script_templates | template_id |
| template_variables | template_id | script_templates | id |
| template_dependencies | template_id | script_templates | id |
| environment_variables | profile_id | environment_profiles | id |
| environment_adaptations | target_environment_id | environment_profiles | id |
| environment_adaptations | source_template_id | script_templates | id |
| generation_sessions | environment_profile_id | environment_profiles | id |
| generation_sessions | template_used_id | script_templates | id |
| generated_scripts | session_id | generation_sessions | session_id |
| generation_logs | session_id | generation_sessions | session_id |
| user_feedback | template_id | script_templates | id |
| user_feedback | script_id | generated_scripts | id |
| user_feedback | session_id | generation_sessions | session_id |
| performance_metrics | template_id | script_templates | id |
| performance_metrics | session_id | generation_sessions | session_id |
| copilot_suggestions | session_id | generation_sessions | session_id |
| copilot_analytics | template_id | script_templates | id |
| copilot_analytics | session_id | generation_sessions | session_id |
| template_usage_analytics | template_id | script_templates | template_name |

## Mermaid ER Diagram

```mermaid
erDiagram
    FILE_SYSTEM_MAPPING {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    VALIDATION_SESSIONS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    GITHUB_SESSIONS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    SYSTEM_INFO {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    LOG_CORRELATION_RESULTS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    COMPLIANCE_EVENTS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    ENHANCED_COMPLIANCE_TRACKING {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    COPILOT_LEARNING_EVENTS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    ERROR_PATTERNS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    CHANGE_TRACKING {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    TODO_FIXME_TRACKING {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    FEEDBACK_LOOPS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    PATTERN_EFFECTIVENESS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    COPILOT_DECISION_TREE {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    ENVIRONMENT_CONFIGS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    TEMPLATE_EFFECTIVENESS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    GENERATION_HISTORY {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    CODEBASE_ANALYSIS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    SCRIPT_METADATA {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    TEMPLATE_PATTERNS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    TEMPLATE_VARIABLES {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    TEMPLATE_DEPENDENCIES {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    ENVIRONMENT_PROFILES {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    ENVIRONMENT_VARIABLES {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    ENVIRONMENT_ADAPTATIONS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    GENERATION_SESSIONS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    GENERATED_SCRIPTS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    GENERATION_LOGS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    USER_FEEDBACK {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    PERFORMANCE_METRICS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    COPILOT_CONTEXTS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    COPILOT_SUGGESTIONS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    COPILOT_ANALYTICS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    COMPLIANCE_CHECKS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    ANTI_RECURSION_TRACKING {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    COMPLIANCE_PATTERNS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    SCRIPT_TEMPLATES {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    ADVANCED_SCRIPT_ANALYSIS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    ENVIRONMENT_ADAPTATION_RULES {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    COPILOT_INTEGRATION_SESSIONS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    TEMPLATE_USAGE_ANALYTICS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    FILESYSTEM_SYNC_LOG {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    SHARED_TEMPLATES {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    SHARED_PLACEHOLDERS {
        int id PK
        string created_timestamp
        string updated_timestamp
    }
    COPILOT_LEARNING_EVENTS ||--|| COPILOT_SESSIONS : has
    CHANGE_TRACKING ||--|| COPILOT_LEARNING_EVENTS : has
    CHANGE_TRACKING ||--|| COPILOT_SESSIONS : has
    TODO_FIXME_TRACKING ||--|| COPILOT_SESSIONS : has
    FEEDBACK_LOOPS ||--|| COPILOT_SESSIONS : has
    FEEDBACK_LOOPS ||--|| COPILOT_LEARNING_EVENTS : has
    PATTERN_EFFECTIVENESS ||--|| PATTERN_DATABASE : has
    COPILOT_DECISION_TREE ||--|| COPILOT_LEARNING_EVENTS : has
    COPILOT_DECISION_TREE ||--|| COPILOT_DECISION_TREE : has
    TEMPLATE_EFFECTIVENESS ||--|| SCRIPT_TEMPLATES : has
    GENERATION_HISTORY ||--|| SCRIPT_TEMPLATES : has
    TEMPLATE_VARIABLES ||--|| SCRIPT_TEMPLATES : has
    TEMPLATE_DEPENDENCIES ||--|| SCRIPT_TEMPLATES : has
    ENVIRONMENT_VARIABLES ||--|| ENVIRONMENT_PROFILES : has
    ENVIRONMENT_ADAPTATIONS ||--|| ENVIRONMENT_PROFILES : has
    ENVIRONMENT_ADAPTATIONS ||--|| SCRIPT_TEMPLATES : has
    GENERATION_SESSIONS ||--|| ENVIRONMENT_PROFILES : has
    GENERATION_SESSIONS ||--|| SCRIPT_TEMPLATES : has
    GENERATED_SCRIPTS ||--|| GENERATION_SESSIONS : has
    GENERATION_LOGS ||--|| GENERATION_SESSIONS : has
    USER_FEEDBACK ||--|| SCRIPT_TEMPLATES : has
    USER_FEEDBACK ||--|| GENERATED_SCRIPTS : has
    USER_FEEDBACK ||--|| GENERATION_SESSIONS : has
    PERFORMANCE_METRICS ||--|| SCRIPT_TEMPLATES : has
    PERFORMANCE_METRICS ||--|| GENERATION_SESSIONS : has
    COPILOT_SUGGESTIONS ||--|| GENERATION_SESSIONS : has
    COPILOT_ANALYTICS ||--|| SCRIPT_TEMPLATES : has
    COPILOT_ANALYTICS ||--|| GENERATION_SESSIONS : has
    TEMPLATE_USAGE_ANALYTICS ||--|| SCRIPT_TEMPLATES : has
```

## Usage Guidelines

### Querying Guidelines
- Use appropriate indices for performance
- Consider transaction isolation levels
- Implement proper error handling

### Security Considerations
- Validate all inputs
- Use parameterized queries
- Implement access controls

### Performance Optimization
- Use connection pooling
- Implement caching where appropriate
- Monitor query performance
\n
## 🤖🤖 DUAL COPILOT PATTERN COMPLIANT
**Enterprise Standards:** This documentation follows DUAL COPILOT patterns with visual processing indicators and anti-recursion protocols.
