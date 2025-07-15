# Template Intelligence Platform API Documentation

## Overview
The Template Intelligence Platform provides a comprehensive API for managing templates, placeholders, and environment configurations across multiple databases.

## Authentication
All API endpoints require authentication via API key or JWT token.

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     https://api.template-intelligence.com/v1/
```

## Endpoints

### Template Management

#### GET /api/v1/templates
Retrieve all templates

**Parameters:**
- `environment` (optional): Filter by environment
- `type` (optional): Filter by template type
- `limit` (optional): Limit results (default: 100)

**Response:**
```json
{
  "templates": [
    {
      "id": "template_123",
      "name": "Database Connection Template",
      "type": "database",
      "environment": "production",
      "placeholders": [
        "{{DATABASE_HOST}}",
        "{{DATABASE_PORT}}",
        "{{DATABASE_NAME}}"
      ],
      "quality_score": 95.5,
      "created_timestamp": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1
}
```

#### POST /api/v1/templates
Create a new template

**Request:**
```json
{
  "name": "API Configuration Template",
  "type": "api",
  "environment": "staging",
  "content": "API_BASE_URL={{API_BASE_URL}}\n
## 🤖🤖 DUAL COPILOT PATTERN COMPLIANT
**Enterprise Standards:** This documentation follows DUAL COPILOT patterns with visual processing indicators and anti-recursion protocols.
\nAPI_KEY={{API_KEY}}",
  "placeholders": ["{{API_BASE_URL}}", "{{API_KEY}}"]
}
```

### Placeholder Management

#### GET /api/v1/placeholders
Retrieve all placeholders

#### POST /api/v1/placeholders
Create a new placeholder

#### PUT /api/v1/placeholders/{id}
Update an existing placeholder

### Environment Management

#### GET /api/v1/environments
List all environment profiles

#### GET /api/v1/environments/{name}/config
Get environment-specific configuration

### Analytics and Intelligence

#### GET /api/v1/analytics/usage
Get template usage analytics

#### GET /api/v1/analytics/quality
Get quality metrics

#### POST /api/v1/analytics/analyze
Trigger intelligent analysis

## SDK Examples

### Python SDK
```python
from template_intelligence import TemplateIntelligenceClient

client = TemplateIntelligenceClient(api_key="your_api_key")

# Get all templates
templates = client.templates.list(environment="production")

# Create a new template
template = client.templates.create({
    "name": "New Template",
    "type": "database",
    "environment": "development",
    "content": "DB_HOST={{DATABASE_HOST}}"
})

# Analyze template quality
analysis = client.analytics.analyze_template(template.id)
```

### JavaScript SDK
```javascript
const { TemplateIntelligenceClient } = require('@template-intelligence/sdk');

const client = new TemplateIntelligenceClient({ apiKey: 'your_api_key' });

// Get templates
const templates = await client.templates.list({ environment: 'production' });

// Create template
const template = await client.templates.create({
  name: 'New Template',
  type: 'api',
  environment: 'staging',
  content: 'API_URL={{API_BASE_URL}}'
});
```

## Error Handling

### Standard Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid template format",
    "details": {
      "field": "placeholders",
      "issue": "Missing required placeholder"
    }
  }
}
```

### Error Codes
- `VALIDATION_ERROR`: Request validation failed
- `AUTHENTICATION_ERROR`: Invalid or missing authentication
- `AUTHORIZATION_ERROR`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server error

## Rate Limiting
- 1000 requests per hour for authenticated users
- 100 requests per hour for unauthenticated users

## Webhook Support

### Template Events
Configure webhooks to receive notifications for:
- Template creation
- Template updates
- Quality score changes
- Environment deployments

```json
{
  "event": "template.created",
  "data": {
    "template_id": "template_123",
    "environment": "production",
    "quality_score": 95.5
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

## Security Best Practices
1. Always use HTTPS
2. Rotate API keys regularly
3. Implement request signing for sensitive operations
4. Validate all inputs
5. Use environment-specific configurations
