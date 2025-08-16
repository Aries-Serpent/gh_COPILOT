"""Feature flags for hardware backend activation.

These flags gate access to experimental hardware integrations. They default to ``False`` so that unit tests and local development use simulator backends. Enabling a flag requires setting the corresponding environment variable to ``"1"``.
"""

from __future__ import annotations

import os


IBM_HARDWARE_ENABLED = os.getenv("ENABLE_IBM_HARDWARE", "0") == "1"
IONQ_HARDWARE_ENABLED = os.getenv("ENABLE_IONQ_HARDWARE", "0") == "1"
DWAVE_HARDWARE_ENABLED = os.getenv("ENABLE_DWAVE_HARDWARE", "0") == "1"


__all__ = [
    "IBM_HARDWARE_ENABLED",
    "IONQ_HARDWARE_ENABLED",
    "DWAVE_HARDWARE_ENABLED",
]
