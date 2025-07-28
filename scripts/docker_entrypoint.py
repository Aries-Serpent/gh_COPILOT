#!/usr/bin/env python3
"""Docker entrypoint for the enterprise dashboard."""

from utils.validation_utils import validate_enterprise_environment
from dashboard.enterprise_dashboard import main

if __name__ == "__main__":
    validate_enterprise_environment()
    main()
