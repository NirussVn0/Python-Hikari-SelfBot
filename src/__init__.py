__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"

def _get_exports():
    from .core.types import CommandExecutionResult, CommandConfig, BotStats
    from .core.interfaces import ICommand, ICommandRegistry
    from .services.discord_service import DiscordService
    from .services.command_registry import CommandRegistry
    from .commands.ping_command import PingCommand
    from .commands.help_command import HelpCommand
    return {
        "CommandExecutionResult": CommandExecutionResult,
        "CommandConfig": CommandConfig,
        "BotStats": BotStats,
        "ICommand": ICommand,
        "ICommandRegistry": ICommandRegistry,
        "DiscordService": DiscordService,
        "CommandRegistry": CommandRegistry,
        "PingCommand": PingCommand,
        "HelpCommand": HelpCommand,
    }
