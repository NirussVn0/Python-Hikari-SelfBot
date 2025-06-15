"""
Core module containing fundamental abstractions and interfaces.

This module provides the foundational components for the Discord self-bot:
- Abstract base classes for commands
- Protocol interfaces for type safety
- Type definitions and data classes
- Custom exception hierarchy
- Core utilities and helpers

The core module follows SOLID principles and provides a clean foundation
for building maintainable and extensible Discord bot functionality.
"""

from .base_command import BaseCommand
from .interfaces import ICommand, ICommandRegistry
from .types import (
    CommandExecutionResult,
    CommandConfig,
    BotStats,
    ConnectionStatus,
)
from .exceptions import (
    DiscordSelfBotError,
    CommandError,
    ConfigurationError,
    ValidationError,
)

__all__ = [
    # Abstract base classes
    "BaseCommand",
    
    # Interfaces
    "ICommand",
    "ICommandRegistry",
    
    # Types and data classes
    "CommandExecutionResult",
    "CommandConfig",
    "BotStats",
    "ConnectionStatus",
    
    # Exceptions
    "DiscordSelfBotError",
    "CommandError",
    "ConfigurationError",
    "ValidationError",
]
