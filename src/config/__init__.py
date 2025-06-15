"""
Configuration management module.

This module provides comprehensive configuration management for the Discord
self-bot, including environment variable handling, settings validation,
and logging configuration.
"""

from .settings import Settings, get_settings
from .logging import setup_logging, get_logger

__all__ = [
    "Settings",
    "get_settings", 
    "setup_logging",
    "get_logger",
]
