
# Capability Scaler Database Documentation

## Overview
**Database**: capability_scaler  
**Type**: SQLite  
**Tables**: 5  
**Generated**: 2025-07-03 06:23:03

## Purpose
Dynamic scaling system identifying scaling patterns, optimizing resource allocations, and managing auto-scaling configurations.

## Tables Overview


### scaling_capabilities

**Rows**: 0  
**Columns**: 10

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| capability_id | TEXT | No | None | No |
| capability_name | TEXT | No | None | No |
| current_level | INTEGER | No | None | No |
| target_level | INTEGER | No | None | No |
| scaling_factor | REAL | No | None | No |
| resource_requirements | TEXT | No | None | No |
| performance_impact | REAL | No | None | No |
| implementation_status | TEXT | No | None | No |
| timestamp | TEXT | No | None | No |

#### SQL Definition
```sql
CREATE TABLE scaling_capabilities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    capability_id TEXT UNIQUE NOT NULL,
                    capability_name TEXT NOT NULL,
                    current_level INTEGER NOT NULL,
                    target_level INTEGER NOT NULL,
                    scaling_factor REAL NOT NULL,
                    resource_requirements TEXT NOT NULL,
                    performance_impact REAL NOT NULL,
                    implementation_status TEXT NOT NULL,
                    timestamp TEXT NOT NULL
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


### scaling_sessions

**Rows**: 4  
**Columns**: 10

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| session_id | TEXT | No | None | No |
| start_time | TEXT | No | None | No |
| end_time | TEXT | Yes | None | No |
| capabilities_scaled | TEXT | No | None | No |
| total_scaling_operations | INTEGER | Yes | 0 | No |
| success_rate | REAL | Yes | 0.0 | No |
| performance_improvement | REAL | Yes | 0.0 | No |
| resource_utilization | TEXT | No | None | No |
| status | TEXT | Yes | 'active' | No |

#### SQL Definition
```sql
CREATE TABLE scaling_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    capabilities_scaled TEXT NOT NULL,
                    total_scaling_operations INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0,
                    performance_improvement REAL DEFAULT 0.0,
                    resource_utilization TEXT NOT NULL,
                    status TEXT DEFAULT 'active'
                )
```


### scaling_operations

**Rows**: 31  
**Columns**: 12

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| operation_id | TEXT | No | None | No |
| session_id | TEXT | No | None | No |
| capability_id | TEXT | No | None | No |
| operation_type | TEXT | No | None | No |
| start_time | TEXT | No | None | No |
| end_time | TEXT | Yes | None | No |
| success | BOOLEAN | Yes | FALSE | No |
| performance_impact | REAL | Yes | 0.0 | No |
| resource_usage | TEXT | No | None | No |
| error_message | TEXT | Yes | None | No |
| status | TEXT | Yes | 'pending' | No |

#### SQL Definition
```sql
CREATE TABLE scaling_operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_id TEXT UNIQUE NOT NULL,
                    session_id TEXT NOT NULL,
                    capability_id TEXT NOT NULL,
                    operation_type TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    success BOOLEAN DEFAULT FALSE,
                    performance_impact REAL DEFAULT 0.0,
                    resource_usage TEXT NOT NULL,
                    error_message TEXT,
                    status TEXT DEFAULT 'pending'
                )
```


### scaling_metrics

**Rows**: 12  
**Columns**: 7

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| timestamp | TEXT | No | None | No |
| session_id | TEXT | No | None | No |
| metric_name | TEXT | No | None | No |
| metric_value | REAL | No | None | No |
| metric_type | TEXT | No | None | No |
| capability_id | TEXT | No | None | No |

#### SQL Definition
```sql
CREATE TABLE scaling_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metric_type TEXT NOT NULL,
                    capability_id TEXT NOT NULL
                )
```

