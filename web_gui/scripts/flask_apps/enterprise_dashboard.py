#!/usr/bin/env python3
"""
Enterprise Flask Dashboard - Database-Driven Web Interface
=========================================================

This module provides a database-driven web interface for enterprise-level dashboard management.
It includes features such as anti-recursion handling, visual processing, and database pattern analysis.

Features:
- Executive dashboard with real-time metrics
- Database visualization and management
- Enterprise compliance reporting
- Role-based access control
- Backup/restore interfaces
- Migration tools
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
import json
from datetime import datetime
from pathlib import Path
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_development_secret_key')

class EnterpriseDashboardApp:
    """[TARGET] Enterprise Dashboard Application Core"""
    
    def __init__(self, workspace_path=None):
        workspace_path = workspace_path or os.getenv("ENTERPRISE_WORKSPACE_PATH", "./workspace")
        self.workspace_path = Path(workspace_path)
        self.production_db = (
            self.workspace_path / "production.db"
        )
        
    def get_database_connection(self):
        """Get production database connection"""
        return sqlite3.connect(str(self.production_db))
    
    def get_dashboard_metrics(self):
        """[BAR_CHART] Get dashboard metrics from production database"""
        try:
            with self.get_database_connection() as conn:
                cursor = conn.cursor()
                
                # Get script tracking metrics
                cursor.execute("SELECT COUNT(*) FROM enhanced_script_tracking")
                total_scripts = cursor.fetchone()[0]
                
                # Get solution patterns count
                cursor.execute("SELECT COUNT(*) FROM solution_patterns")
                total_patterns = cursor.fetchone()[0]
                
                # Get functional components count
                cursor.execute("SELECT COUNT(*) FROM functional_components")
                total_components = cursor.fetchone()[0]
                
                # Get recent activity
                cursor.execute("""
                    SELECT script_path, last_updated 
                    FROM enhanced_script_tracking 
                    ORDER BY last_updated DESC 
                    LIMIT 10
                """)
                recent_activity = cursor.fetchall()
                
                return {
                    "total_scripts": total_scripts,
                    "total_patterns": total_patterns,
                    "total_components": total_components,
                    "recent_activity": recent_activity,
                    "last_updated": datetime.now().isoformat()
                }
        except Exception as e:
            logging.error(f"Error getting dashboard metrics: {e}")
            return {}

dashboard = EnterpriseDashboardApp()

@app.route('/')
def index():
    """[?] Main dashboard page"""
    metrics = dashboard.get_dashboard_metrics()
    return render_template('dashboard.html', metrics=metrics)

@app.route('/database')
def database_view():
    """[FILE_CABINET] Database management interface"""
    return render_template('database.html')

@app.route('/api/scripts')
def api_scripts():
    """[CLIPBOARD] API endpoint for scripts data"""
    try:
        with dashboard.get_database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT script_path, script_type, functionality_category, 
                       lines_of_code, last_updated
                FROM enhanced_script_tracking
                ORDER BY last_updated DESC
            """)
            scripts = cursor.fetchall()
            
            return jsonify({
                "success": True,
                "scripts": [{
                    "path": script[0],
                    "type": script[1],
                    "category": script[2],
                    "lines": script[3],
                    "updated": script[4]
                } for script in scripts]
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/backup')
def backup_interface():
    """[STORAGE] Backup and restore interface"""
    return render_template('backup_restore.html')

@app.route('/migration')
def migration_interface():
    """[PROCESSING] Migration tools interface"""
    return render_template('migration.html')


@app.route('/deployment')
def deployment_interface():
    """[LAUNCH] Deployment management interface"""
    return render_template('deployment.html')


@app.route('/api/health')
def health_check():
    """[?] Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": (
            "connected" if dashboard.production_db.exists() else "disconnected"
        )
    })


if __name__ == '__main__':
    print("[NETWORK] Starting Enterprise Flask Dashboard...")
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    print(f"[CHAIN] Access at: http://localhost:{port}")
    app.run(debug=True, host='0.0.0.0', port=port)
