
# Backup Database Documentation

## Overview
**Database**: backup  
**Type**: SQLite  
**Tables**: 5  
**Generated**: 2025-07-03 06:23:03

## Purpose
Backup and disaster recovery database ensuring data protection and business continuity.

## Tables Overview


### templates

**Rows**: 0  
**Columns**: 6

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| template_name | TEXT | No | None | No |
| template_content | TEXT | No | None | No |
| created_timestamp | DATETIME | Yes | CURRENT_TIMESTAMP | No |
| updated_timestamp | DATETIME | Yes | CURRENT_TIMESTAMP | No |
| is_active | BOOLEAN | Yes | 1 | No |

#### SQL Definition
```sql
CREATE TABLE templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_name TEXT UNIQUE NOT NULL,
                    template_content TEXT NOT NULL,
                    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
```


### sqlite_sequence

**Rows**: 1  
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


### placeholder_usage

**Rows**: 0  
**Columns**: 5

#### Columns
| Column | Type | Nullable | Default | Primary Key |
|--------|------|----------|---------|-------------|
| id | INTEGER | Yes | None | Yes |
| placeholder_name | TEXT | No | None | No |
| template_id | INTEGER | Yes | None | No |
| usage_count | INTEGER | Yes | 1 | No |
| last_used | DATETIME | Yes | CURRENT_TIMESTAMP | No |

#### SQL Definition
```sql
CREATE TABLE placeholder_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    placeholder_name TEXT NOT NULL,
                    template_id INTEGER,
                    usage_count INTEGER DEFAULT 1,
                    last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (template_id) REFERENCES templates(id)
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

- **placeholder_usage.template_id** → **templates.id** (FOREIGN_KEY)
