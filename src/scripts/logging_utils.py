from __future__ import annotations

import logging


def setup_logging(level: str = "INFO") -> logging.Logger:
    logging.basicConfig(
        level=level.upper(),
        format="%(levelname)s: %(message)s",
    )
    return logging.getLogger(__name__)
