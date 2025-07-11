# MCP Server Guide

## Overview
The Flask-based dashboard in gh_COPILOT acts as the **Master Control Program (MCP) server**. It provides a centralized interface to start, monitor and coordinate the other services that make up the toolkit.

## Starting the MCP Server
Use one of the following methods to launch the dashboard:

### Python
```bash
python web_gui_scripts/flask_apps/enterprise_dashboard.py
```

### Docker Compose
```bash
docker-compose up web_gui
```
This starts the `web_gui` service defined in `docker-compose.yml`.

## Port Mappings
The dashboard listens on port **8080** and proxies to the supporting APIs. The services use the following default ports:

| Service            | Port |
|--------------------|-----|
| File Browser API   | 5001 |
| Database Query API | 5002 |
| CLI Relay API      | 5003 |
| Documentation API  | 5004 |
| File Browser WS    | 5005 |
| CLI Relay WS       | 5006 |
| Dashboard (MCP)    | 8080 |

Access `http://localhost:8080` in your browser after startup. In production environments you can map port **443** for HTTPS.
