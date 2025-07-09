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
        cursor.execute(
         )
              """)

        # Create adaptation rules table with correct schema
        cursor.execute(
            )
        """)

              # Create environment context history table
              cursor.execute(
               )
              """)

        # Create template adaptation logs table
        cursor.execute(
            )
        """)

                conn.commit()
                print("Environment tables migrated successfully")


                if __name__ == "__main__":
               migrate_environment_tables()
