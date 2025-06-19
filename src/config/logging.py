# Logging configuration for the Discord self-bot.
import logging
import logging.config
import sys
from typing import Dict, Any, Optional

try:
    from rich.console import Console
    from rich.logging import RichHandler

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from .settings import Settings


def setup_logging(settings: Optional[Settings] = None) -> None:
    if settings is None:
        from .settings import get_settings

        settings = get_settings()

    # Determine log level
    log_level = settings.get_effective_log_level()

    # Create logging configuration
    config = _create_logging_config(settings, log_level)

    # Apply configuration
    logging.config.dictConfig(config)

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))

    # Log startup information
    logger = logging.getLogger("discord_selfbot.config")
    logger.info(f"Logging configured with level: {log_level}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    if settings.is_production:
        logger.warning("Running in PRODUCTION mode")

    # Suppress noisy third-party loggers in production
    if settings.is_production:
        logging.getLogger("discord").setLevel(logging.WARNING)
        logging.getLogger("aiohttp").setLevel(logging.WARNING)
        logging.getLogger("asyncio").setLevel(logging.WARNING)


def _create_logging_config(settings: Settings, log_level: str) -> Dict[str, Any]:
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": (
                    "%(asctime)s | %(levelname)-8s | %(name)-30s | "
                    "%(funcName)-20s:%(lineno)-4d | %(message)s"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {
                "format": "%(levelname)-8s | %(name)-20s | %(message)s",
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": (
                    "%(asctime)s %(name)s %(levelname)s %(funcName)s "
                    "%(lineno)d %(message)s"
                ),
            },
        },
        "handlers": {},
        "loggers": {
            "discord_selfbot": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "commands": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "services": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["console"],
        },
    }

    # Configure console handler
    if RICH_AVAILABLE and settings.enable_rich_logging and not settings.is_production:
        # Use Rich handler for development
        config["handlers"]["console"] = {
            "class": "rich.logging.RichHandler",
            "level": log_level,
            "formatter": "simple",
            "rich_tracebacks": True,
            "show_time": True,
            "show_path": settings.is_development,
        }
    else:
        # Use standard handler for production or when Rich is not available
        config["handlers"]["console"] = {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "detailed" if settings.is_development else "simple",
            "stream": "ext://sys.stdout",
        }

    # Add file handler for production
    if settings.is_production:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "json" if settings.enable_metrics else "detailed",
            "filename": "discord_selfbot.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf-8",
        }

        # Add file handler to all loggers
        for logger_config in config["loggers"].values():
            logger_config["handlers"].append("file")
        config["root"]["handlers"].append("file")

    # Add error file handler for all environments
    config["handlers"]["error_file"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "level": "ERROR",
        "formatter": "detailed",
        "filename": "discord_selfbot_errors.log",
        "maxBytes": 5242880,  # 5MB
        "backupCount": 3,
        "encoding": "utf-8",
    }

    # Add error handler to all loggers
    for logger_config in config["loggers"].values():
        logger_config["handlers"].append("error_file")
    config["root"]["handlers"].append("error_file")

    return config


def get_logger(name: str) -> logging.Logger:
    if not name.startswith("discord_selfbot."):
        name = f"discord_selfbot.{name}"

    return logging.getLogger(name)


class StructuredLogger:
    def __init__(self, name: str):
        self.logger = get_logger(name)
        self.context: Dict[str, Any] = {}

    def add_context(self, **kwargs: Any) -> None:
        self.context.update(kwargs)

    def remove_context(self, *keys: str) -> None:
        """
        Remove context keys.

        Args:
            *keys: Context keys to remove
        """
        for key in keys:
            self.context.pop(key, None)

    def clear_context(self) -> None:
        """Clear all context information."""
        self.context.clear()

    def _format_message(self, message: str, **kwargs: Any) -> str:
        return message

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message with metadata."""
        self.logger.debug(message, extra={**self.context, **kwargs})

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message with metadata."""
        self.logger.info(message, extra={**self.context, **kwargs})

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with metadata."""
        self.logger.warning(message, extra={**self.context, **kwargs})

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message with metadata."""
        self.logger.error(message, extra={**self.context, **kwargs})

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message with metadata."""
        self.logger.critical(message, extra={**self.context, **kwargs})

    def exception(self, message: str, **kwargs: Any) -> None:
        """Log exception message with metadata and traceback."""
        self.logger.exception(message, extra={**self.context, **kwargs})
