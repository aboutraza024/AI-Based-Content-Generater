import logging
import sys

from app.core.config import settings

logger = logging.getLogger("content_writer")


def setup_logging() -> None:
    """Turns on simple console logging for the whole app."""
    level = logging.DEBUG if settings.DEBUG else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
