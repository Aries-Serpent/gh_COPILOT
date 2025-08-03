# API Documentation
==================

🔌 REST API reference and integration guides

## Base URL
```
http://localhost:5000/api
```

## Authentication
Currently using basic Flask session management. In production, implement:
```http
Authorization: Bearer <token>
```

## Core Endpoints

### Health Check
**Endpoint**: `GET /api/health`
**Description**: Check system health and database connectivity

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-06T12:00:00Z",
  "database": "connected"
}
```

**Status Codes**:
- `200`: System healthy
- `500`: System error

### Scripts Data
**Endpoint**: `GET /api/scripts`
**Description**: Retrieve all tracked scripts information

**Response**:
```json
{
  "success": true,
  "scripts": [
    {
      "path": "script_path.py",
      "type": "automation",
      "category": "enterprise",
      "lines": 150,
      "updated": "2025-01-06T11:30:00Z"
    }
  ]
}
```

**Status Codes**:
- `200`: Success
- `500`: Database error

### Database Query (Future Enhancement)
**Endpoint**: `POST /api/database/query`
**Description**: Execute safe database queries
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "query": "SELECT * FROM enhanced_script_tracking LIMIT 10",
  "validate": true
}
```

**Response**:
```json
{
  "success": true,
  "data": [...],
  "execution_time": "0.05s",
  "row_count": 10
}
```

### Backup Operations (Future Enhancement)
**Endpoint**: `POST /api/backup/create`
**Description**: Create system backup
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "type": "full",
  "destination": "e:/_copilot_backups",
  "compress": true
}
```

**Response**:
```json
{
  "success": true,
  "backup_id": "backup_20250106_120000",
  "location": "e:/_copilot_backups/backup_20250106_120000.tar.gz",
  "size": "125MB"
}
```

## Monitoring Endpoints

### Metrics
**Endpoint**: `GET /metrics`
**Description**: Return aggregated system and compliance metrics.

### Corrections
**Endpoint**: `GET /corrections`
**Description**: List recorded correction entries.

### Compliance
**Endpoint**: `GET /compliance`
**Description**: Combine metric data and correction summaries.

### Violations
**Endpoint**: `GET /violations`
**Description**: Retrieve recent violation log entries.

## SDK Examples

### Python SDK
```python
import requests
import json

class GhCopilotAPI:
    def __init__(self, base_url="http://localhost:5000/api"):
        self.base_url = base_url
    
    def health_check(self):
        """Check system health"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def get_scripts(self):
        """Get all tracked scripts"""
        response = requests.get(f"{self.base_url}/scripts")
        return response.json()
    
    def create_backup(self, backup_type="full"):
        """Create system backup"""
        payload = {"type": backup_type, "compress": True}
        response = requests.post(
            f"{self.base_url}/backup/create", 
            json=payload
        )
        return response.json()

# Usage example
api = GhCopilotAPI()

# Health check
health = api.health_check()
print(f"System status: {health['status']}")

# Get scripts
scripts_data = api.get_scripts()
print(f"Total scripts: {len(scripts_data.get('scripts', []))}")
```

### JavaScript SDK
```javascript
class GhCopilotAPI {
    constructor(baseUrl = 'http://localhost:5000/api') {
        this.baseUrl = baseUrl;
    }
    
    async healthCheck() {
        const response = await fetch(`${this.baseUrl}/health`);
        return response.json();
    }
    
    async getScripts() {
        const response = await fetch(`${this.baseUrl}/scripts`);
        return response.json();
    }
    
    async createBackup(type = 'full') {
        const response = await fetch(`${this.baseUrl}/backup/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ type, compress: true })
        });
        return response.json();
    }
}

// Usage example
const api = new GhCopilotAPI();

// Health check
api.healthCheck().then(health => {
    console.log('System status:', health.status);
});

// Get scripts
api.getScripts().then(data => {
    console.log('Scripts:', data.scripts);
});
```

### cURL Examples
```bash
# Health check
curl -X GET http://localhost:5000/api/health

# Get scripts data
curl -X GET http://localhost:5000/api/scripts

# Create backup (future)
curl -X POST http://localhost:5000/api/backup/create \
  -H "Content-Type: application/json" \
  -d '{"type": "full", "compress": true}'
```

## Error Handling

### Standard Error Response
```json
{
  "success": false,
  "error": "Error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-01-06T12:00:00Z"
}
```

### Error Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | System maintenance |

## Rate Limiting

### Default Limits
- **Health Check**: 60 requests/minute
- **Scripts Data**: 30 requests/minute
- **Database Operations**: 10 requests/minute
- **Backup Operations**: 5 requests/hour

### Rate Limit Headers
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1641484800
```

## Security Considerations

### Data Protection
- All database queries are parameterized
- Input validation on all endpoints
- SQL injection prevention
- XSS protection enabled

### Authentication (Future)
```python
# JWT token authentication
from flask_jwt_extended import JWTManager, jwt_required

@app.route('/api/protected')
@jwt_required()
def protected_endpoint():
    return {"message": "Access granted"}
```

### HTTPS Configuration (Production)
```python
# SSL context for production
if app.config['ENV'] == 'production':
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain('cert.pem', 'key.pem')
    app.run(host='0.0.0.0', port=443, ssl_context=context)
```

## Integration Examples

### Database Integration
```python
# Connect to production database
import sqlite3
from pathlib import Path

def get_database_metrics():
    db_path = Path(os.getenv("GH_COPILOT_WORKSPACE", "/path/to/workspace")) / "production.db"
    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM enhanced_script_tracking")
        return {"total_scripts": cursor.fetchone()[0]}
```

### Template Intelligence Integration
```python
# Leverage template intelligence patterns
def get_template_patterns():
    with get_database_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pattern_name, pattern_description 
            FROM solution_patterns 
            WHERE status = 'ACTIVE'
        """)
        return cursor.fetchall()
```

## Future API Enhancements

### Planned Endpoints
- `POST /api/scripts/analyze` - Script analysis
- `GET /api/templates/suggest` - Template suggestions
- `POST /api/migration/plan` - Migration planning
- `GET /api/compliance/report` - Compliance reporting

### WebSocket Support
```javascript
// Real-time updates
const socket = new WebSocket('ws://localhost:5000/ws');
socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    updateDashboard(data);
};
```

Generated: 2025-01-06T04:53:00Z
