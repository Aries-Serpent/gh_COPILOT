"""ML script utilities package.

Heavy ML dependencies such as ``torch`` and ``tensorflow`` are only imported
when the ``ENABLE_ML_FEATURES`` environment variable is set to ``"1"``. This
keeps lightweight environments usable without the optional packages.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

ENABLE_ML_FEATURES = os.getenv("ENABLE_ML_FEATURES", "0") == "1"

if ENABLE_ML_FEATURES:
    try:  # pragma: no cover - optional imports
        import torch  # type: ignore
        import tensorflow as tf  # type: ignore
    except ImportError as exc:  # pragma: no cover - allow missing deps
        logger.warning("ML features disabled due to missing dependency: %s", exc)
        ENABLE_ML_FEATURES = False
else:  # pragma: no cover - simple logging path
    logger.info("ML features are disabled via ENABLE_ML_FEATURES")

__all__ = ["ENABLE_ML_FEATURES"]

