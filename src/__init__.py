from .core.types import CommandExecutionResult, CommandConfig, BotStats
from .core.interfaces import ICommand, ICommandRegistry
from .services.discord_service import DiscordService
from .services.command_registry import CommandRegistry
from .commands.ping_command import PingCommand
from .commands.help_command import HelpCommand

__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"

__all__ = [
    # Core types and interfaces
    "CommandExecutionResult",
    "CommandConfig", 
    "BotStats",
    "ICommand",
    "ICommandRegistry",
    
    # Services
    "DiscordService",
    "CommandRegistry",
    
    # Commands
    "PingCommand",
    "HelpCommand",
    
    # Metadata
    "__version__",
    "__author__",
    "__license__",
]
