import subprocess
import sys
import os
import time
from pathlib import Path
from typing import Optional, List

import psutil
import requests


def launch_service(script_path: Path, workspace: Path, wait_time: int = 3) -> Optional[subprocess.Popen]:
    """Launch a Python service and return the process if successful."""
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return None

    try:
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            cwd=str(workspace),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0,
        )
        time.sleep(max(wait_time, 0))
        if process.poll() is None:
            return process
        process.wait(timeout=1)
    except Exception as e:
        print(f"❌ Error starting service {script_path}: {e}")
    return None


def check_service_running(names: List[str], port: Optional[int] = None) -> bool:
    """Return True if a service appears to be running."""
    if port:
        try:
            resp = requests.get(f"http://localhost:{port}/health", timeout=3)
            if resp.status_code == 200:
                return True
        except Exception:
            pass

    try:
        for proc in psutil.process_iter(['name', 'cmdline']):
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if any(name.lower() in cmdline.lower() for name in names):
                    return True
    except Exception:
        pass

    return False
