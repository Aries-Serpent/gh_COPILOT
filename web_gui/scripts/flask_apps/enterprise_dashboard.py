#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enterprise Flask Dashboard - Database-Driven Web Interface
=========================================================

🛡️ DUAL COPILOT ✅ | Anti-Recursion ✅ | Visual Processing ✅
Generated from Database Pattern Analysis

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

# Configure Flask with correct template folder
template_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'templates', 'html')
app = Flask(__name__, template_folder=template_folder)
app.secret_key = 'enterprise_dashboard_secret_key_change_in_production'

class EnterpriseDashboardApp:
    """🎯 Enterprise Dashboard Application Core"""
    
    def __init__(self, workspace_path: str | None = None):
        if workspace_path is None:
            workspace_path = os.environ.get("GH_COPILOT_ROOT", os.getcwd())
        self.workspace_path = Path(workspace_path)
        self.production_db = self.workspace_path / "databases" / "production.db"
        
    def get_database_connection(self):
        """Get production database connection"""
        return sqlite3.connect(str(self.production_db))
    
    def get_dashboard_metrics(self):
        """📊 Get dashboard metrics from production database"""
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
            print(f"❌ Error getting dashboard metrics: {e}")
            return {
                "total_scripts": 0,
                "total_patterns": 0,
                "total_components": 0,
                "recent_activity": [],
                "last_updated": datetime.now().isoformat()
            }

dashboard = EnterpriseDashboardApp()

@app.route('/')
def index():
    """🏠 Main dashboard page"""
    metrics = dashboard.get_dashboard_metrics()
    return render_template('dashboard.html', metrics=metrics)

@app.route('/database')
def database_view():
    """🗄️ Database management interface"""
    return render_template('database.html')

@app.route('/api/scripts')
def api_scripts():
    """📋 API endpoint for scripts data"""
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
    """💾 Backup and restore interface"""
    return render_template('backup_restore.html')

@app.route('/migration')
def migration_interface():
    """🔄 Migration tools interface"""
    return render_template('migration.html')

@app.route('/deployment')
def deployment_interface():
    """🚀 Deployment management interface"""
    return render_template('deployment.html')

@app.route('/health')
def health_check_simple():
    """🏥 Simple health check endpoint for system monitoring"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected" if dashboard.production_db.exists() else "disconnected"
    })

@app.route('/api/health')
def health_check():
    """🏥 Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected" if dashboard.production_db.exists() else "disconnected"
    })

if __name__ == '__main__':
    print("Starting Enterprise Flask Dashboard...")
    print("Access at: http://localhost:5000")
    print(f"Template folder: {app.template_folder}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
