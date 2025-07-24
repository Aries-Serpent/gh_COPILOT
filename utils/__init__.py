# Utility modules for gh_COPILOT Enterprise Toolkit
"""utils package"""
__version__ = "1.0.0"

# Re-export commonly used logging helper
from .log_utils import _log_event

__all__ = ["_log_event"]
