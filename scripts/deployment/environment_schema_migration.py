#!/usr/bin/env python3
"""
Database Schema Migration for Environment Adaptation System
Fixes table structure for Phase 4 environment profiles and adaptation rules
"""

import sqlite3
import json
from pathlib import Path

def migrate_environment_tables():
    """Migrate environment tables to support advanced adaptation features"""
    
    db_path = Path("e:/gh_COPILOT/databases/learning_monitor.db")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Drop existing tables if they exist (but preserve data)
        cursor.execute("DROP TABLE IF EXISTS environment_profiles")
        cursor.execute("DROP TABLE IF EXISTS adaptation_rules")
        cursor.execute("DROP TABLE IF EXISTS environment_context_history")
        cursor.execute("DROP TABLE IF EXISTS template_adaptation_logs")
        
        # Create environment profiles table with correct schema
        cursor.execute("""
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
        """)
        
        # Create adaptation rules table with correct schema
        cursor.execute("""
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
        """)
        
        # Create environment context history table
        cursor.execute("""
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
        """)
        
        # Create template adaptation logs table
        cursor.execute("""
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
        """)
        
        conn.commit()
        print("Environment tables migrated successfully")

if __name__ == "__main__":
    migrate_environment_tables()
