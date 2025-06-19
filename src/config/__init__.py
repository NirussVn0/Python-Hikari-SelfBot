"""
Configuration management for the Discord self-bot.
Handles environment variables, settings validation, and logging config.
"""

from .settings import Settings, get_settings
from .logging import setup_logging, get_logger

__all__ = [
    "Settings",
    "get_settings",
    "setup_logging",
    "get_logger",
]
