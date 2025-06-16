# Package metadata
__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"

# Lazy imports to avoid circular import issues when running modules
def _get_exports():
    """Lazy import function to avoid circular imports."""
    from .core.types import CommandExecutionResult, CommandConfig, BotStats
    from .core.interfaces import ICommand, ICommandRegistry
    from .services.discord_service import DiscordService
    from .services.command_registry import CommandRegistry
    from .commands.ping_command import PingCommand
    from .commands.help_command import HelpCommand

    return {
        # Core types and interfaces
        "CommandExecutionResult": CommandExecutionResult,
        "CommandConfig": CommandConfig,
        "BotStats": BotStats,
        "ICommand": ICommand,
        "ICommandRegistry": ICommandRegistry,

        # Services
        "DiscordService": DiscordService,
        "CommandRegistry": CommandRegistry,

        # Commands
        "PingCommand": PingCommand,
        "HelpCommand": HelpCommand,

        # Metadata
        "__version__": __version__,
        "__author__": __author__,
        "__license__": __license__,
    }

# Only perform imports when explicitly requested
def __getattr__(name):
    """Dynamic attribute access for lazy imports."""
    exports = _get_exports()
    if name in exports:
        return exports[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

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
