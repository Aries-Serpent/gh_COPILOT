"""Lightweight session utilities.

This package provides minimal validation helpers used during test
sessions.  Only the pieces required by the tests are implemented; the
implementations favour simplicity over completeness.
"""

from .manager import SessionManager

__all__ = ["SessionManager"]

