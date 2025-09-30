import logging
import logging.handlers
import os
from .config import get_settings


def configure_logging() -> None:
    """
    Configure application-wide logging for agent activities and API events.
    Style aligns with 'Ocean Professional' – clean, structured, and informative.
    """
    # PUBLIC_INTERFACE
    settings = get_settings()
    log_dir = os.path.join(settings.STORAGE_BASE_PATH, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "app.log")

    root = logging.getLogger()
    if root.handlers:
        # Avoid double configuration on reload
        return

    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.handlers.RotatingFileHandler(
        log_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    root.addHandler(file_handler)
    root.addHandler(console_handler)

    logging.getLogger("app").info("Logging configured. Level=%s", settings.LOG_LEVEL)
