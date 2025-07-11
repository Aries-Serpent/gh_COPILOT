---
applyTo: '**'
---

# 🖥️ MCP SERVER ACTIVATION INSTRUCTIONS
## Master Control Program Server for gh_COPILOT Toolkit

### 🎯 **MCP SERVER OVERVIEW**
The MCP server (Master Control Program server) orchestrates Copilot modules and manages compliance events.

## ⚙️ **ACTIVATION COMMANDS**
```bash
# Install dependencies
pip install -r requirements.txt

# Start the MCP server
python mcp_server.py
```

## 🌐 **ENVIRONMENT VARIABLES**
- `MCP_SERVER_HOST` – server address (`localhost` by default)
- `MCP_SERVER_PORT` – listening port (`8080` by default)
- `MCP_SERVER_ENABLED` – set to `1` to activate integration

All Copilot components should check `MCP_SERVER_ENABLED` and use the host and port for coordination.
