# gh_COPILOT Session Startup Guide

This guide summarizes the environment setup and manual startup commands required to run the enterprise services. It also references the session templates and response chunking rules.

## Environment Setup

Follow the installation steps below (from `documentation/INSTALLATION_GUIDE.md`):

1. Install **Python 3.12 or higher** on Windows 10/11 or Linux.
2. Ensure at least **8GB RAM** and **50GB** of free disk space.
3. From the repository root (`e:\gh_COPILOT` on Windows), run:
   ```bash
   python deployment/install.py
   ```
4. To start the Template Intelligence Platform for the first time:
   ```bash
   python core/template_intelligence_platform.py
   ```

## Manual Service Startup

See `documentation/MANUAL_STARTUP_GUIDE.md` for complete instructions. The key commands are:

```bash
# Generate dashboard scripts
python web_gui/database_driven_web_gui_generator.py

# Recommended: start each service in its own terminal
python file_browser_api.py
python database_query_api.py
python copilot_cli_relay_api.py
python documentation_generation_api.py
python file_browser_websocket.py
python copilot_cli_relay_websocket.py
python web_gui_scripts/flask_apps/enterprise_dashboard.py
```

Batch options are also available via `start_all_services.bat`, `start_all_services.sh`, or `START_ALL_SERVICES.py`.

## Session Templates

Standard session patterns are defined in `.github/instructions/SESSION_TEMPLATES.instructions.md`. They describe database-first workflows and validation steps for consistent enterprise sessions.

## Anti-Recursion Guard

Entry points that start or end a session should apply the
`anti_recursion_guard` decorator from `scripts.session.anti_recursion_enforcer`.
This guard uses both a lock file and process checks to prevent accidentally
starting multiple session managers at the same time.

```python
from scripts.session.anti_recursion_enforcer import anti_recursion_guard

@anti_recursion_guard
def main():
    ...
```

## Response Chunking

All Copilot responses must follow the rules in `.github/instructions/RESPONSE_CHUNKING.instructions.md`:

- Limit each chunk to **2,000 tokens** or less (optimal range: 1,500–1,800).
- Begin with anti-recursion validation when file operations occur.
- Break work into logical phases with clear validation at the end of each chunk.

## Example Prompts

**Start Session Prompt**
```
Apply session template DATABASE_FIRST_ANALYSIS. Validate workspace and begin environment setup checks.
```

**Next Session Prompt**
```
Use the enterprise chunking framework from .github/instructions/RESPONSE_CHUNKING.instructions.md. Continue with the next implementation phase.
```
