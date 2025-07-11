# MCP Server Setup

## Overview
The term **MCP server** stands for **Master Control Program server**. It acts as the central authority for coordinating gh_COPILOT modules and enforcing enterprise compliance.

## Server Purpose
- Orchestrate Copilot tasks across modules
- Provide API endpoints for monitoring and automation
- Manage authentication and session integrity

## Configuration Steps
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set environment variables:
   - `MCP_SERVER_HOST` – network address (default `localhost`)
   - `MCP_SERVER_PORT` – port to listen on (default `8080`)
   - `MCP_SERVER_ENABLED` – set to `1` to enable integration
3. Start the server:
   ```bash
   python mcp_server.py
   ```

## Integration with Copilot
- Ensure `MCP_SERVER_ENABLED` is set before launching Copilot components.
- Copilot modules contact the server at `$MCP_SERVER_HOST:$MCP_SERVER_PORT` for job coordination.
- All actions are logged in `production.db` for audit purposes.
