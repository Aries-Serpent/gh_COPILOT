# DASHBOARD MODULE: ENTERPRISE MONITORING AND COMPLIANCE
# > Generated: 2025-07-24 19:22:23 | Author: mbaetiong

import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory, abort

# --- Anti-Recursion Validation ---
def chunk_anti_recursion_validation():
    """CRITICAL: Validate workspace before chunk execution"""
    if not validate_no_recursive_folders():
        raise RuntimeError("CRITICAL: Recursive violations prevent chunk execution")
    if detect_c_temp_violations():
        raise RuntimeError("CRITICAL: E:/temp/ violations prevent chunk execution")
    return True

def validate_no_recursive_folders():
    # Placeholder: Implement workspace root and backup root recursion checks
    workspace = os.environ.get("GH_COPILOT_WORKSPACE", os.getcwd())
    backup_root = os.environ.get("GH_COPILOT_BACKUP_ROOT", "/tmp/gh_COPILOT_backup")
    # No subfolder in workspace should be the same as workspace or backup root
    real_workspace = os.path.realpath(workspace)
    real_backup = os.path.realpath(backup_root)
    if real_workspace == real_backup:
        return False
    for root, dirs, files in os.walk(workspace):
        for d in dirs:
            dpath = os.path.realpath(os.path.join(root, d))
            if dpath == real_workspace or dpath == real_backup:
                return False
    return True

def detect_c_temp_violations():
    # Placeholder: Prevent workspace or backup root from being set to E:/temp/
    forbidden = ["E:/temp/", "E:\\temp\\"]
    workspace = os.environ.get("GH_COPILOT_WORKSPACE", os.getcwd())
    backup_root = os.environ.get("GH_COPILOT_BACKUP_ROOT", "/tmp/gh_COPILOT_backup")
    for forbidden_path in forbidden:
        if workspace.startswith(forbidden_path) or backup_root.startswith(forbidden_path):
            return True
    return False

chunk_anti_recursion_validation()

# --- Flask Application Setup ---
app = Flask(__name__, template_folder="templates", static_folder="static")

# --- Database and File Paths ---
WORKSPACE = os.environ.get("GH_COPILOT_WORKSPACE", os.getcwd())
DB_PRODUCTION = os.path.join(WORKSPACE, "production.db")
DB_ANALYTICS = os.path.join(WORKSPACE, "analytics.db")
DB_MONITORING = os.path.join(WORKSPACE, "monitoring.db")
COMPLIANCE_METRICS_FILE = os.path.join(os.path.dirname(__file__), "compliance", "metrics.json")
CORRECTION_SUMMARY_FILE = os.path.join(os.path.dirname(__file__), "compliance", "correction_summary.json")

# --- Utility Functions ---
def get_db_metrics():
    """Aggregate compliance and session metrics from analytics.db"""
    metrics = {
        "placeholder_removal": 0,
        "compliance_score": 0.0,
        "active_sessions": 0,
        "total_sessions": 0,
    }
    try:
        if os.path.exists(DB_ANALYTICS):
            conn = sqlite3.connect(DB_ANALYTICS)
            cur = conn.cursor()
            # Example: Placeholder removal count
            cur.execute("SELECT value FROM metrics WHERE key='placeholder_removal'")
            row = cur.fetchone()
            if row:
                metrics["placeholder_removal"] = int(row[0])
            # Example: Compliance score
            cur.execute("SELECT value FROM metrics WHERE key='compliance_score'")
            row = cur.fetchone()
            if row:
                metrics["compliance_score"] = float(row[0])
            # Example: Session counts
            cur.execute("SELECT COUNT(*) FROM session_log WHERE status='active'")
            row = cur.fetchone()
            if row:
                metrics["active_sessions"] = int(row[0])
            cur.execute("SELECT COUNT(*) FROM session_log")
            row = cur.fetchone()
            if row:
                metrics["total_sessions"] = int(row[0])
            conn.close()
    except Exception as e:
        metrics["error"] = str(e)
    return metrics

def get_correction_summaries():
    """Load correction and rollback summaries from compliance/correction_summary.json"""
    if os.path.exists(CORRECTION_SUMMARY_FILE):
        with open(CORRECTION_SUMMARY_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

def get_metrics_json_fallback():
    """Fallback for compliance/metrics.json, used if analytics.db is missing"""
    if os.path.exists(COMPLIANCE_METRICS_FILE):
        with open(COMPLIANCE_METRICS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}

def get_dashboard_status():
    """Aggregate all relevant dashboard status for main view."""
    metrics = get_db_metrics()
    correction_summaries = get_correction_summaries()
    backup_root = os.environ.get("GH_COPILOT_BACKUP_ROOT", "/tmp/gh_COPILOT_backup")
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    return {
        "timestamp": timestamp,
        "metrics": metrics,
        "correction_summaries": correction_summaries,
        "backup_root": backup_root,
        "production_db_exists": os.path.exists(DB_PRODUCTION),
        "analytics_db_exists": os.path.exists(DB_ANALYTICS),
        "monitoring_db_exists": os.path.exists(DB_MONITORING),
    }

# --- Flask Endpoints ---

@app.route("/")
def main_dashboard():
    status = get_dashboard_status()
    return render_template("dashboard.html", **status)

@app.route("/database")
def database_browser():
    status = get_dashboard_status()
    # Optionally, add table and schema browsing here
    return render_template("database.html", **status)

@app.route("/backup")
def backup_manager():
    status = get_dashboard_status()
    # Optionally, list backups, show logs
    return render_template("backup.html", **status)

@app.route("/migration")
def migration_manager():
    status = get_dashboard_status()
    return render_template("migration.html", **status)

@app.route("/deployment")
def deployment_manager():
    status = get_dashboard_status()
    return render_template("deployment.html", **status)

@app.route("/api/scripts", methods=["GET", "POST"])
def api_scripts():
    # Example: Run script or return script status
    if request.method == "POST":
        script_name = request.form.get("script")
        # Implement script execution and monitoring
        return jsonify({"status": "started", "script": script_name})
    return jsonify({"scripts": ["self_healing_self_learning_system.py", "database_sync_scheduler.py"]})

@app.route("/api/health")
def api_health():
    # Simple health check
    status = {
        "production_db": os.path.exists(DB_PRODUCTION),
        "analytics_db": os.path.exists(DB_ANALYTICS),
        "monitoring_db": os.path.exists(DB_MONITORING),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status": "healthy"
    }
    if not all([status["production_db"], status["analytics_db"], status["monitoring_db"]]):
        status["status"] = "degraded"
    return jsonify(status)

@app.route("/dashboard/compliance")
def dashboard_compliance():
    # Returns compliance metrics and rollbacks in JSON
    metrics = get_db_metrics()
    # Fallback to metrics.json if DB not available
    if (not metrics or ("error" in metrics and metrics["error"])):
        metrics = get_metrics_json_fallback()
    rollbacks = get_correction_summaries()
    return jsonify({
        "metrics": metrics,
        "rollbacks": rollbacks
    })

@app.route("/static/<path:filename>")
def static_content(filename):
    # Serve static files
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    return send_from_directory(static_dir, filename)

@app.route("/favicon.ico")
def favicon():
    return abort(404)

# --- Error Handlers ---
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html", error=str(e)), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html", error=str(e)), 500

# --- Main Entrypoint ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=bool(os.environ.get("FLASK_ENV") == "development"))
