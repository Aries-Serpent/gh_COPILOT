
# Performance Analysis Database Documentation

## Overview
**Database**: performance_analysis  
**Type**: SQLite  
**Tables**: 5  
**Generated**: 2025-07-03 06:23:03

## Purpose
Advanced performance analysis engine providing optimization recommendations, scaling strategies, and resource utilization insights.

## Tables Overview


### performance_metrics

**Rows**: 14  
**Columns**: 10

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| timestamp | TEXT | No | None | No |
| metric_name | TEXT | No | None | No |
| current_value | REAL | No | None | No |
| baseline_value | REAL | No | None | No |
| performance_score | REAL | No | None | No |
| trend_direction | TEXT | No | None | No |
| confidence_level | REAL | No | None | No |
| analysis_metadata | TEXT | No | None | No |
| session_id | TEXT | No | None | No |

#### SQL Definition
```sql
CREATE TABLE performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    current_value REAL NOT NULL,
                    baseline_value REAL NOT NULL,
                    performance_score REAL NOT NULL,
                    trend_direction TEXT NOT NULL,
                    confidence_level REAL NOT NULL,
                    analysis_metadata TEXT NOT NULL,
                    session_id TEXT NOT NULL
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


### analysis_sessions

**Rows**: 4  
**Columns**: 9

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| session_id | TEXT | No | None | No |
| start_time | TEXT | No | None | No |
| end_time | TEXT | Yes | None | No |
| metrics_analyzed | INTEGER | Yes | 0 | No |
| optimization_opportunities | TEXT | No | None | No |
| performance_grade | TEXT | Yes | 'unknown' | No |
| recommendations | TEXT | No | None | No |
| status | TEXT | Yes | 'active' | No |

#### SQL Definition
```sql
CREATE TABLE analysis_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    metrics_analyzed INTEGER DEFAULT 0,
                    optimization_opportunities TEXT NOT NULL,
                    performance_grade TEXT DEFAULT 'unknown',
                    recommendations TEXT NOT NULL,
                    status TEXT DEFAULT 'active'
                )
```


### baseline_metrics

**Rows**: 0  
**Columns**: 7

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| metric_name | TEXT | No | None | No |
| baseline_value | REAL | No | None | No |
| calculation_method | TEXT | No | None | No |
| data_points_used | INTEGER | No | None | No |
| confidence_score | REAL | No | None | No |
| last_updated | TEXT | No | None | No |

#### SQL Definition
```sql
CREATE TABLE baseline_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT UNIQUE NOT NULL,
                    baseline_value REAL NOT NULL,
                    calculation_method TEXT NOT NULL,
                    data_points_used INTEGER NOT NULL,
                    confidence_score REAL NOT NULL,
                    last_updated TEXT NOT NULL
                )
```


### optimization_recommendations

**Rows**: 22  
**Columns**: 9

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| timestamp | TEXT | No | None | No |
| session_id | TEXT | No | None | No |
| metric_name | TEXT | No | None | No |
| recommendation_type | TEXT | No | None | No |
| description | TEXT | No | None | No |
| expected_improvement | REAL | No | None | No |
| implementation_priority | TEXT | No | None | No |
| status | TEXT | Yes | 'pending' | No |

#### SQL Definition
```sql
CREATE TABLE optimization_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    recommendation_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    expected_improvement REAL NOT NULL,
                    implementation_priority TEXT NOT NULL,
                    status TEXT DEFAULT 'pending'
                )
```

