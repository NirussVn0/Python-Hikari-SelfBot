"""
Services module containing business logic and core services.

This module provides the service layer for the Discord self-bot, including:
- Discord client management
- Command registry and management
- Bot statistics and monitoring
- Performance metrics tracking

All services follow SOLID principles and provide clean interfaces
for interaction with other components.
"""

from services.command_registry import CommandRegistry
from services.bot_stats import BotStatsService
from services.discord_service import DiscordService

__all__ = [
    "CommandRegistry",
    "BotStatsService", 
    "DiscordService",
]
