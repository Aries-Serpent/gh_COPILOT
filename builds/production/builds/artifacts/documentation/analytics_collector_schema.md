
# Analytics Collector Database Documentation

## Overview
**Database**: analytics_collector  
**Type**: SQLite  
**Tables**: 4  
**Generated**: 2025-07-03 06:23:03

## Purpose
Comprehensive analytics collection including usage patterns, performance metrics, and error analysis for continuous improvement.

## Tables Overview


### analytics_data_points

**Rows**: 36  
**Columns**: 10

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| timestamp | TEXT | No | None | No |
| source | TEXT | No | None | No |
| category | TEXT | No | None | No |
| metric_name | TEXT | No | None | No |
| metric_value | TEXT | No | None | No |
| metadata | TEXT | No | None | No |
| quality_score | REAL | No | None | No |
| validation_status | TEXT | No | None | No |
| session_id | TEXT | No | None | No |

#### SQL Definition
```sql
CREATE TABLE analytics_data_points (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    source TEXT NOT NULL,
                    category TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    quality_score REAL NOT NULL,
                    validation_status TEXT NOT NULL,
                    session_id TEXT NOT NULL
                )
```


### sqlite_sequence

**Rows**: 2  
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


### analytics_sessions

**Rows**: 4  
**Columns**: 9

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| session_id | TEXT | No | None | No |
| start_time | TEXT | No | None | No |
| end_time | TEXT | Yes | None | No |
| total_data_points | INTEGER | Yes | 0 | No |
| data_sources | TEXT | No | None | No |
| categories_processed | TEXT | No | None | No |
| status | TEXT | Yes | 'active' | No |
| quality_metrics | TEXT | No | None | No |

#### SQL Definition
```sql
CREATE TABLE analytics_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    total_data_points INTEGER DEFAULT 0,
                    data_sources TEXT NOT NULL,
                    categories_processed TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    quality_metrics TEXT NOT NULL
                )
```


### data_aggregations

**Rows**: 0  
**Columns**: 9

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| aggregation_timestamp | TEXT | No | None | No |
| source | TEXT | No | None | No |
| category | TEXT | No | None | No |
| metric_name | TEXT | No | None | No |
| aggregation_type | TEXT | No | None | No |
| aggregated_value | REAL | No | None | No |
| data_point_count | INTEGER | No | None | No |
| time_window_hours | REAL | No | None | No |

#### SQL Definition
```sql
CREATE TABLE data_aggregations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    aggregation_timestamp TEXT NOT NULL,
                    source TEXT NOT NULL,
                    category TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    aggregation_type TEXT NOT NULL,
                    aggregated_value REAL NOT NULL,
                    data_point_count INTEGER NOT NULL,
                    time_window_hours REAL NOT NULL
                )
```

