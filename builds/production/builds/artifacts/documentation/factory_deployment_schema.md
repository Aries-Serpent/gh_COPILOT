
# Factory Deployment Database Documentation

## Overview
**Database**: factory_deployment  
**Type**: SQLite  
**Tables**: 4  
**Generated**: 2025-07-03 06:23:03

## Purpose
Automated deployment system managing deployment templates, automation scripts, and deployment pipeline configurations.

## Tables Overview


### deployment_sessions

**Rows**: 1  
**Columns**: 10

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| deployment_id | TEXT | No | None | No |
| start_time | TEXT | No | None | No |
| end_time | TEXT | Yes | None | No |
| status | TEXT | Yes | 'in_progress' | No |
| workspace_path | TEXT | No | None | No |
| phases_completed | INTEGER | Yes | 0 | No |
| total_phases | INTEGER | Yes | 5 | No |
| success_rate | REAL | Yes | 0.0 | No |
| created_at | TEXT | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE deployment_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        deployment_id TEXT UNIQUE NOT NULL,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        status TEXT DEFAULT 'in_progress',
                        workspace_path TEXT NOT NULL,
                        phases_completed INTEGER DEFAULT 0,
                        total_phases INTEGER DEFAULT 5,
                        success_rate REAL DEFAULT 0.0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
```


### sqlite_sequence

**Rows**: 3  
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


### factory_validation

**Rows**: 1  
**Columns**: 9

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| deployment_id | TEXT | No | None | No |
| validation_type | TEXT | No | None | No |
| validation_result | TEXT | No | None | No |
| files_checked | INTEGER | Yes | 0 | No |
| violations_found | INTEGER | Yes | 0 | No |
| compliance_score | REAL | Yes | 0.0 | No |
| timestamp | TEXT | No | None | No |
| created_at | TEXT | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE factory_validation (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        deployment_id TEXT NOT NULL,
                        validation_type TEXT NOT NULL,
                        validation_result TEXT NOT NULL,
                        files_checked INTEGER DEFAULT 0,
                        violations_found INTEGER DEFAULT 0,
                        compliance_score REAL DEFAULT 0.0,
                        timestamp TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
```


### cleanup_actions

**Rows**: 13  
**Columns**: 8

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| deployment_id | TEXT | No | None | No |
| action_type | TEXT | No | None | No |
| target_path | TEXT | No | None | No |
| action_result | TEXT | No | None | No |
| files_affected | INTEGER | Yes | 0 | No |
| timestamp | TEXT | No | None | No |
| created_at | TEXT | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE cleanup_actions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        deployment_id TEXT NOT NULL,
                        action_type TEXT NOT NULL,
                        target_path TEXT NOT NULL,
                        action_result TEXT NOT NULL,
                        files_affected INTEGER DEFAULT 0,
                        timestamp TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
```

