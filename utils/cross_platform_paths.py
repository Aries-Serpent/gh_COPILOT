#!/usr/bin/env python3
"""Cross-Platform Path Detection System."""

import logging
import os
import shutil
from pathlib import Path
from typing import Any, Dict

# Default workspace path using environment variable or current directory
DEFAULT_WORKSPACE = os.getenv("GH_COPILOT_WORKSPACE", str(Path.cwd()))


class CrossPlatformPathManager:
    """Cross-Platform Path Management System."""

    @staticmethod
    def get_workspace_path() -> Path:
        """Return workspace path with cross-platform detection."""
        workspace_env = os.getenv("GH_COPILOT_WORKSPACE", str(Path.cwd()))
        workspace_path = Path(workspace_env)
        if workspace_path.exists():
            return workspace_path

        current_dir = Path.cwd()
        if current_dir.name == "gh_COPILOT":
            return current_dir

        for parent in current_dir.parents:
            if parent.name == "gh_COPILOT":
                return parent

        if os.name == "nt":
            potential_paths = [
                Path(DEFAULT_WORKSPACE),
                Path("E:/gh_COPILOT"),
                Path("C:/gh_COPILOT"),
                Path("D:/gh_COPILOT"),
            ]
        else:
            user_home = Path.home()
            potential_paths = [
                Path(DEFAULT_WORKSPACE),
                user_home / "gh_COPILOT",
                Path("/opt/gh_COPILOT"),
                Path("/usr/local/gh_COPILOT"),
            ]

        for path in potential_paths:
            if path.exists():
                return path

        logging.warning(
            "Could not detect gh_COPILOT workspace, using current directory"
        )
        return current_dir

    @staticmethod
    def get_backup_root() -> Path:
        """Return backup root path with cross-platform detection."""
        backup_env = os.getenv("GH_COPILOT_BACKUP_ROOT")
        if backup_env:
            return Path(backup_env)

        if os.name == "nt":
            return Path("E:/temp/gh_COPILOT_Backups")

        return Path(f"/tmp/{os.getenv('USER', 'user')}/gh_COPILOT_Backups")

    @staticmethod
    def validate_path_portability(file_path: str) -> Dict[str, Any]:
        """Validate path portability and suggest fixes."""
        validation_result = {
            "original_path": file_path,
            "is_portable": True,
            "issues": [],
            "suggested_fix": None,
        }

        hard_coded_patterns = [
            "E:/gh_COPILOT",
            "C:/gh_COPILOT",
            "E\\gh_COPILOT",
            "C\\gh_COPILOT",
            "E:\\gh_COPILOT",
            "C:\\gh_COPILOT",
        ]

        for pattern in hard_coded_patterns:
            if pattern in file_path:
                validation_result["is_portable"] = False
                validation_result["issues"].append(f"Hard-coded path found: {pattern}")
                validation_result["suggested_fix"] = (
                    "Use CrossPlatformPathManager.get_workspace_path()"
                )

        return validation_result


def migrate_hard_coded_paths(file_path: Path) -> Dict[str, Any]:
    """Migrate hard-coded paths to cross-platform equivalents.

    The original file is backed up under
    ``CrossPlatformPathManager.get_backup_root() / 'migration_backups'``.
    """
    if not file_path.exists():
        return {"error": f"File not found: {file_path}"}

    content = file_path.read_text(encoding="utf-8")

    replacements = {
        'r"E:/gh_COPILOT"': "CrossPlatformPathManager.get_workspace_path()",
        '"E:/gh_COPILOT"': "str(CrossPlatformPathManager.get_workspace_path())",
        "'E:/gh_COPILOT'": "str(CrossPlatformPathManager.get_workspace_path())",
        'r"E:\\gh_COPILOT"': "CrossPlatformPathManager.get_workspace_path()",
        '"E:\\gh_COPILOT"': "str(CrossPlatformPathManager.get_workspace_path())",
    }

    updated_content = content
    changes_made = []

    for old, new in replacements.items():
        if old in updated_content:
            updated_content = updated_content.replace(old, new)
            changes_made.append(f"{old} -> {new}")

    if changes_made:
        backup_root = CrossPlatformPathManager.get_backup_root() / "migration_backups"
        backup_root.mkdir(parents=True, exist_ok=True)
        backup_path = backup_root / f"{file_path.name}.backup"
        shutil.copy2(file_path, backup_path)
        file_path.write_text(updated_content, encoding="utf-8")

        if (
            "CrossPlatformPathManager" in updated_content
            and "from utils.cross_platform_paths import CrossPlatformPathManager"
            not in updated_content
        ):
            lines = updated_content.split("\n")
            import_line = (
                "from utils.cross_platform_paths import CrossPlatformPathManager"
            )
            insert_index = 0
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    insert_index = i + 1
            lines.insert(insert_index, import_line)
            updated_content = "\n".join(lines)
            file_path.write_text(updated_content, encoding="utf-8")

    return {
        "file_path": str(file_path),
        "changes_made": changes_made,
        "backup_created": str(backup_path) if changes_made else None,
    }


def verify_environment_variables() -> None:
    """Ensure ``GH_COPILOT_WORKSPACE`` and ``GH_COPILOT_BACKUP_ROOT`` are set.

    Raises
    ------
    EnvironmentError
        If required environment variables are missing or point to invalid paths.
    """

    workspace_env = os.getenv("GH_COPILOT_WORKSPACE")
    backup_env = os.getenv("GH_COPILOT_BACKUP_ROOT")

    if not workspace_env or not backup_env:
        raise EnvironmentError(
            "GH_COPILOT_WORKSPACE and GH_COPILOT_BACKUP_ROOT must be set"
        )

    workspace = CrossPlatformPathManager.get_workspace_path()
    backup_root = CrossPlatformPathManager.get_backup_root()

    if not workspace.exists():
        raise EnvironmentError(f"Workspace does not exist: {workspace}")

    if workspace == backup_root or workspace in backup_root.parents:
        raise EnvironmentError("Backup root cannot reside within the workspace")

    if not backup_root.parent.exists():
        raise EnvironmentError(
            f"Backup root parent does not exist: {backup_root.parent}"
        )

