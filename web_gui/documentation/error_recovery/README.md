# Error Recovery Guide
======================

🚨 Troubleshooting and error handling procedures

## Common Error Scenarios

### Flask Application Errors

#### Application Won't Start
**Symptoms**: 
- `python enterprise_dashboard.py` fails
- Import errors for Flask
- Port binding errors

**Recovery Steps**:
1. **Check Dependencies** (for the web dashboard only):
   ```bash
   pip install flask
   pip install -r requirements.txt  # required only for the dashboard
   ```

2. **Verify Port Availability**:
   ```bash
   netstat -an | grep 5000
   # If port is in use, kill the process or use different port
   ```

3. **Check Python Path**:
   ```bash
   which python
   python --version
   ```

4. **Restart with Different Port**:
   ```python
   app.run(debug=True, host='0.0.0.0', port=5001)
   ```

#### Template Not Found Errors
**Symptoms**: 
- `TemplateNotFound: dashboard.html`
- Web pages show template errors

**Recovery Steps**:
1. **Verify Template Path**:
   ```bash
   ls -la $GH_COPILOT_WORKSPACE/templates/html/
   ```

2. **Check Flask Configuration**:
   ```python
   app.template_folder = '$GH_COPILOT_WORKSPACE/templates/html'
   ```

3. **Fix Template Path in Code**:
   ```python
   # Absolute path approach
   import os
   template_dir = os.path.abspath('$GH_COPILOT_WORKSPACE/templates/html')
   app = Flask(__name__, template_folder=template_dir)
   ```

### Database Connection Errors

#### Database File Not Found
**Symptoms**: 
- `sqlite3.OperationalError: unable to open database file`
- Database connectivity issues

**Recovery Steps**:
1. **Verify Database Path**:
   ```bash
   ls -la $GH_COPILOT_WORKSPACE/production.db
   ```

2. **Check Permissions**:
   ```bash
   chmod 664 $GH_COPILOT_WORKSPACE/production.db
   ```

3. **Create Missing Database**:
   ```python
   import sqlite3
   conn = sqlite3.connect('$GH_COPILOT_WORKSPACE/production.db')
   conn.close()
   ```

#### Database Lock Errors
**Symptoms**: 
- `sqlite3.OperationalError: database is locked`
- Multiple connection conflicts

**Recovery Steps**:
1. **Close All Connections**:
   ```bash
   # Find processes using the database
   lsof $GH_COPILOT_WORKSPACE/production.db
   ```

2. **Restart Flask Application**:
   ```bash
   pkill -f "enterprise_dashboard.py"
   python enterprise_dashboard.py
   ```

3. **Use Connection Pooling**:
   ```python
   import sqlite3
   from contextlib import contextmanager

   @contextmanager
   def get_db_connection():
       conn = sqlite3.connect('production.db', timeout=30)
       try:
           yield conn
       finally:
           conn.close()
   ```

### Web Interface Errors

#### Pages Not Loading
**Symptoms**: 
- HTTP 404 errors
- Blank pages
- CSS/JS not loading

**Recovery Steps**:
1. **Check Flask Routes**:
   ```python
   @app.route('/')
   def index():
       return render_template('dashboard.html')
   ```

2. **Verify Static Files**:
   ```bash
   ls -la templates/html/
   ```

3. **Clear Browser Cache**:
   - Hard refresh (Ctrl+F5)
   - Clear browser cache
   - Try different browser

#### API Endpoints Not Responding
**Symptoms**: 
- `/api/health` returns 404
- JSON responses fail

**Recovery Steps**:
1. **Check Route Definitions**:
   ```python
   @app.route('/api/health')
   def health_check():
       return jsonify({"status": "healthy"})
   ```

2. **Test API Endpoints**:
   ```bash
   curl http://localhost:5000/api/health
   ```

3. **Review Flask Logs**:
   ```bash
   python enterprise_dashboard.py 2>&1 | tee flask.log
   ```

## Error Monitoring

### Log Locations
- **Flask Application**: Console output and flask.log
- **Database**: SQLite built-in logging
- **System**: Windows Event Viewer / Linux syslog
- **Browser**: Developer console (F12)

### Monitoring Tools
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flask.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Real-time Monitoring
```python
@app.route('/api/health')
def health_check():
    try:
        # Test database connection
        with get_database_connection() as conn:
            conn.execute("SELECT 1")
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected"
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500
```

## Recovery Procedures

### Quick Recovery (5-15 minutes)
```bash
# 1. Stop current services
pkill -f "enterprise_dashboard.py"

# 2. Check and fix common issues
python -c "import flask; print('Flask OK')"
ls -la $GH_COPILOT_WORKSPACE/production.db
ls -la $GH_COPILOT_WORKSPACE/templates/html/

# 3. Restart services
cd $GH_COPILOT_WORKSPACE/web_gui/scripts/flask_apps
python enterprise_dashboard.py

# 4. Verify functionality
curl http://localhost:5000/api/health
```

### Full Recovery (30-60 minutes)
```bash
# 1. Stop all services
pkill -f "enterprise_dashboard.py"

# 2. Backup current state
cp -r $GH_COPILOT_WORKSPACE $GH_COPILOT_WORKSPACE_backup

# 3. Restore from known good backup
python backup_scripts/restore_latest_backup.py

# 4. Reinstall dashboard dependencies
pip install -r web_gui/scripts/requirements.txt  # only needed for the dashboard

# 5. Restart all services
cd web_gui/scripts/flask_apps
python enterprise_dashboard.py

# 6. Validate recovery
python validation_scripts/validate_recovery.py
```

### Emergency Recovery (When Nothing Works)
```bash
# 1. Download fresh copy from repository
git clone <repository> $GH_COPILOT_WORKSPACE_fresh

# 2. Copy critical data
cp $GH_COPILOT_WORKSPACE/production.db $GH_COPILOT_WORKSPACE_fresh/

# 3. Switch to fresh installation
mv $GH_COPILOT_WORKSPACE $GH_COPILOT_WORKSPACE_failed
mv $GH_COPILOT_WORKSPACE_fresh $GH_COPILOT_WORKSPACE

# 4. Reinstall and restart (dashboard only)
cd $GH_COPILOT_WORKSPACE
pip install -r web_gui/scripts/requirements.txt  # reinstall dashboard packages
cd web_gui/scripts/flask_apps
python enterprise_dashboard.py
```

## Prevention Strategies

### Proactive Monitoring
```python
# Health check automation
import schedule
import time

def automated_health_check():
    try:
        response = requests.get('http://localhost:5000/api/health')
        if response.status_code != 200:
            send_alert("Web GUI health check failed")
    except Exception as e:
        send_alert(f"Web GUI unreachable: {e}")

schedule.every(5).minutes.do(automated_health_check)
```

### Regular Maintenance
- **Daily**: Check application logs
- **Weekly**: Verify database integrity
- **Monthly**: Update dependencies
- **Quarterly**: Full system testing

### Backup Strategies
```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="e:/_copilot_backups"

# Backup web GUI components
tar -czf $BACKUP_DIR/web_gui_$DATE.tar.gz \
    web_gui/scripts/ \
    templates/ \
    web_gui_documentation/

# Backup database
cp production.db $BACKUP_DIR/production_db_$DATE.db

echo "Backup completed: $DATE"
```

## Escalation Procedures

### Level 1: Self-Service (0-30 minutes)
- Check this documentation
- Review error messages
- Apply common fixes
- Restart services

### Level 2: Technical Support (30 minutes - 2 hours)
- **Contact**: support@company.com
- **Provide**: 
  - Error logs
  - System information
  - Steps to reproduce
- **Expected Response**: 2 hours

### Level 3: Emergency Support (Immediate)
- **Contact**: emergency@company.com
- **Provide**: 
  - Complete system state
  - Business impact assessment
  - Immediate workaround needs
- **Expected Response**: 30 minutes

### Level 4: Vendor Support (2-24 hours)
- **Contact**: vendor-support@company.com
- **Provide**: 
  - Full diagnostic package
  - System configuration
  - Historical data
- **Expected Response**: 24 hours

## Diagnostic Tools

### System Information Collection
```python
import platform
import psutil
import sqlite3

def collect_diagnostic_info():
    return {
        "system": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "memory": psutil.virtual_memory()._asdict(),
            "disk": psutil.disk_usage('/')._asdict()
        },
        "flask": {
            "version": flask.__version__,
            "running": check_flask_running(),
            "port": check_port_status(5000)
        },
        "database": {
            "file_exists": os.path.exists("production.db"),
            "file_size": os.path.getsize("production.db"),
            "connection_test": test_db_connection()
        }
    }
```

### Automated Diagnostics
```bash
# Create diagnostic script
python << EOF
import json
from datetime import datetime

diagnostic_data = collect_diagnostic_info()
diagnostic_data['timestamp'] = datetime.now().isoformat()

with open('diagnostic_report.json', 'w') as f:
    json.dump(diagnostic_data, f, indent=2)

print("Diagnostic report saved to diagnostic_report.json")
EOF
```

Generated: 2025-01-06T04:53:00Z
