# CONTINUOUS OPERATION MONITOR MODULE: ENTERPRISE SYSTEM HEALTH & UPTIME TRACKING
# > Generated: 2025-07-24 19:52:00 | Author: mbaetiong

import os
import sys
import time
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Ensure repository root is on sys.path when executed directly
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tqdm import tqdm
from scripts.monitoring.unified_monitoring_optimization_system import (
    EnterpriseUtility,
)

# --- Anti-Recursion Validation (MANDATORY) ---

def chunk_anti_recursion_validation():
    """CRITICAL: Validate workspace before chunk execution"""
    if not validate_no_recursive_folders():
        raise RuntimeError("CRITICAL: Recursive violations prevent chunk execution")
    if detect_c_temp_violations():
        raise RuntimeError("CRITICAL: E:/temp/ violations prevent chunk execution")
    return True

def validate_no_recursive_folders():
    workspace = os.environ.get("GH_COPILOT_WORKSPACE", os.getcwd())
    backup_root = os.environ.get("GH_COPILOT_BACKUP_ROOT", "/tmp/gh_COPILOT_backup")
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
    forbidden = ["E:/temp/", "E:\\temp\\"]
    workspace = os.environ.get("GH_COPILOT_WORKSPACE", os.getcwd())
    backup_root = os.environ.get("GH_COPILOT_BACKUP_ROOT", "/tmp/gh_COPILOT_backup")
    for forbidden_path in forbidden:
        if workspace.startswith(forbidden_path) or backup_root.startswith(forbidden_path):
            return True
    return False

chunk_anti_recursion_validation()

# --- Monitor Class ---

class ContinuousOperationMonitor:
    """
    Enterprise continuous operation monitor for real-time system uptime, health, and anomaly tracking.
    Features:
    - Monitors critical system metrics (uptime, load, memory, file descriptors)
    - Logs periodic health data to analytics.db (monitoring.health_monitor)
    - Detects anomalies and writes alerts
    - Provides visual progress/status indicators
    - Compliant with DUAL COPILOT and enterprise validation standards
    """

    def __init__(self, monitor_interval: int = 60, log_db: Optional[str] = None, verbose: bool = True):
        self.monitor_interval = monitor_interval
        self.verbose = verbose
        self.workspace_root = Path(os.environ.get("GH_COPILOT_WORKSPACE", os.getcwd()))
        self.analytics_db = log_db or str(self.workspace_root / "analytics.db")
        self.monitoring_table = "monitoring_health"
        self.last_metrics: Dict[str, Any] = {}
        self.status = "INIT"
        self.session_id = f"SESSION_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        self._setup_db()
        self._log_event("monitor_start", {"monitor_interval": self.monitor_interval, "status": self.status})

    def _setup_db(self):
        if not os.path.exists(self.analytics_db):
            print(f"[WARN] analytics.db does not exist, creating new database at {self.analytics_db}")
        with sqlite3.connect(self.analytics_db) as conn:
            cur = conn.cursor()
            cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.monitoring_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TEXT,
                uptime_seconds REAL,
                cpu_load REAL,
                total_mem_mb REAL,
                available_mem_mb REAL,
                open_fds INTEGER,
                status TEXT,
                anomaly INTEGER,
                note TEXT
            )
            """)
            conn.commit()

    def _log_event(self, event: str, data: Optional[Dict[str, Any]] = None):
        timestamp = datetime.utcnow().isoformat() + "Z"
        entry = {"timestamp": timestamp, "event": event}
        if data:
            entry.update(data)
        if self.verbose:
            print(f"[{event.upper()}] {timestamp} | {data if data else ''}")

    def _get_system_metrics(self) -> Dict[str, Any]:
        metrics = {
            "uptime_seconds": 0.0,
            "cpu_load": 0.0,
            "total_mem_mb": 0.0,
            "available_mem_mb": 0.0,
            "open_fds": 0,
            "status": "UNKNOWN",
            "anomaly": 0,
            "note": ""
        }
        try:
            # Uptime (since script start)
            now = time.time()
            if not hasattr(self, "_start_time"):
                self._start_time = now
            metrics["uptime_seconds"] = now - self._start_time

            # CPU load (system load average)
            try:
                import psutil
                metrics["cpu_load"] = psutil.getloadavg()[0] if hasattr(psutil, "getloadavg") else psutil.cpu_percent(interval=1) / 100.0
            except (ImportError, AttributeError):
                metrics["cpu_load"] = 0.0

            # Memory stats
            if sys.platform == "linux" or sys.platform == "darwin":
                import resource
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                total_mem = int([x for x in meminfo.splitlines() if "MemTotal" in x][0].split()[1])
                avail_mem = int([x for x in meminfo.splitlines() if "MemAvailable" in x][0].split()[1])
                metrics["total_mem_mb"] = total_mem / 1024
                metrics["available_mem_mb"] = avail_mem / 1024
                metrics["open_fds"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            elif sys.platform == "win32":
                import psutil
                mem = psutil.virtual_memory()
                metrics["total_mem_mb"] = mem.total / 1024 / 1024
                metrics["available_mem_mb"] = mem.available / 1024 / 1024
                metrics["open_fds"] = 0
            else:
                metrics["total_mem_mb"] = 0.0
                metrics["available_mem_mb"] = 0.0
                metrics["open_fds"] = 0

            metrics["status"] = "OK"
            metrics["anomaly"] = 0
            metrics["note"] = ""

            # Simple anomaly: high load or low memory
            if metrics["cpu_load"] > 4.0 or metrics["available_mem_mb"] < 256:
                metrics["anomaly"] = 1
                metrics["status"] = "ALERT"
                metrics["note"] = "High load or low memory"
        except Exception as e:
            metrics["status"] = "ERROR"
            metrics["anomaly"] = 1
            metrics["note"] = str(e)
        return metrics

    def _write_metrics(self, metrics: Dict[str, Any]):
        try:
            with sqlite3.connect(self.analytics_db) as conn:
                cur = conn.cursor()
                cur.execute(f"""
                    INSERT INTO {self.monitoring_table}
                    (session_id, timestamp, uptime_seconds, cpu_load, total_mem_mb, available_mem_mb, open_fds, status, anomaly, note)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.session_id,
                    datetime.utcnow().isoformat() + "Z",
                    metrics.get("uptime_seconds", 0.0),
                    metrics.get("cpu_load", 0.0),
                    metrics.get("total_mem_mb", 0.0),
                    metrics.get("available_mem_mb", 0.0),
                    metrics.get("open_fds", 0),
                    metrics.get("status", ""),
                    metrics.get("anomaly", 0),
                    metrics.get("note", "")
                ))
                conn.commit()
            self._log_event("metrics_logged", metrics)
        except Exception as e:
            self._log_event("metrics_log_error", {"error": str(e)})

    def monitor_loop(self):
        print(f"[INFO] CONTINUOUS OPERATION MONITOR STARTED | Session: {self.session_id}")
        print(f"Logging to: {self.analytics_db}")
        print("=" * 60)
        try:
            with tqdm(desc="[INFO] Monitoring", unit="cycles") as pbar:
                while True:
                    metrics = self._get_system_metrics()
                    self._write_metrics(metrics)
                    self.last_metrics = metrics
                    pbar.set_postfix({
                        "status": metrics["status"],
                        "load": f"{metrics['cpu_load']:.2f}",
                        "mem_avail": f"{metrics['available_mem_mb']:.1f}MB"
                    })
                    pbar.update(1)
                    if metrics["anomaly"]:
                        print(f"[ALERT] Anomaly detected: {metrics['note']}")
                    time.sleep(self.monitor_interval)
        except KeyboardInterrupt:
            print("\n[STOP] Monitor interrupted by user.")
            self._log_event("monitor_stopped", {"status": "USER_INTERRUPT"})

def main():
    import argparse
    EnterpriseUtility().execute_utility()
    parser = argparse.ArgumentParser(description="Enterprise Continuous Operation Monitor for gh_COPILOT Toolkit")
    parser.add_argument("--interval", type=int, default=60, help="Monitor interval in seconds")
    parser.add_argument("--log-db", type=str, default=None, help="Path to analytics.db (default: workspace)")
    parser.add_argument("--quiet", action="store_true", help="Suppress detailed console output")
    args = parser.parse_args()
    monitor = ContinuousOperationMonitor(
        monitor_interval=args.interval,
        log_db=args.log_db,
        verbose=not args.quiet
    )
    monitor.monitor_loop()

if __name__ == "__main__":
    EnterpriseUtility().execute_utility()
    main()