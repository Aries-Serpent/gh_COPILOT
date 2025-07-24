"""Wrapper for the enterprise compliance monitor."""

from scripts.enterprise_compliance_monitor import main as enterprise_main

__all__ = ["enterprise_main"]

if __name__ == "__main__":
    enterprise_main()
