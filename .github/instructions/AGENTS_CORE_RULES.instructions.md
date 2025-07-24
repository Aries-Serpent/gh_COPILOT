# AGENTS Core Rules (Quick Reference)

- **Environment Setup**: Run `bash setup.sh` first and activate the virtual environment with `source .venv/bin/activate`. Set `GH_COPILOT_WORKSPACE` to the repo root and `GH_COPILOT_BACKUP_ROOT` to an external path.
- **Non-Interactive Commands**: Use only non-interactive shell tools (e.g., `cat`, `grep`, `sed`). Do not launch editors or commands that require a TTY.
- **clw for Long Output**: Pipe any command that might produce lengthy lines through `/usr/local/bin/clw` or redirect to a file and read in chunks. This prevents exceeding the 1600-byte line limit.
- **No Extra Dependencies**: Install packages only from `requirements*.txt` via the setup script. Mention any missing dependencies in the PR instead of installing them.
- **Stay on Task**: Keep changes focused on the prompt and follow repository conventions.
