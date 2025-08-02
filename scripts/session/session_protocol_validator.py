#!/usr/bin/env python3
"""CLI wrapper for :class:`validation.protocols.session.SessionProtocolValidator`."""

from validation.protocols.session import SessionProtocolValidator, main as _main

__all__ = ["SessionProtocolValidator", "main"]


def main() -> int:
    """Entry point for CLI compatibility."""
    return _main()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
