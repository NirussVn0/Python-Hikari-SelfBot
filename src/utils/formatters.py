from typing import Dict, List, Optional, Any

try:
    from ..core.types import CommandConfig
except ImportError:
    from core.types import CommandConfig


class MessageFormatter:
    @staticmethod
    def format_command_output(content: str, success: bool = True) -> str:
        prefix = "\u2705" if success else "\u274c"
        return f"{prefix} {content}"
    
    @staticmethod
    def format_code_block(content: str, language: str = "") -> str:
        return f"```{language}\n{content}\n```"
    
    @staticmethod
    def format_info_message(title: str, content: str) -> str:
        return f"**{title}**\n{content}"


def format_help_message(command_config: CommandConfig, name: str, description: str = "", 
                       usage: str = "", examples: List[str] = None) -> str:
    examples = examples or []
    parts = [f"## Help: {name}"]
    
    if description:
        parts.append(description)
    
    if usage:
        parts.append(f"**Usage:**\n```{usage}```")
    
    if examples:
        examples_text = "\n".join(examples)
        parts.append(f"**Examples:**\n```{examples_text}```")
    
    if command_config.aliases and len(command_config.aliases) > 0:
        aliases = ", ".join(command_config.aliases)
        parts.append(f"**Aliases:** {aliases}")
    
    return "\n\n".join(parts)


def format_error_message(error_text: str, details: Optional[str] = None) -> str:
    message = f"❌ **Error:** {error_text}"
    
    if details:
        message += f"\n```{details}```"
    
    return message


def format_command_config(config: CommandConfig) -> str:
    """
    Formats a CommandConfig object into a human-readable string.

    Args:
        config (CommandConfig): The command configuration to format.

    Returns:
        str: A formatted string representation of the command configuration.
    """
    status = "Enabled" if config.enabled else "Disabled"
    cooldown_info = f"{config.cooldown / 1000} seconds" if config.cooldown else "None"
    usage = f"Usage: `{config.usage}`" if config.usage else ""
    examples = "\n".join([f"        - `{ex}`" for ex in config.examples]) if config.examples else ""

    formatted_string = (
        f"**Command Configuration:**\n"
        f"    Status: {status}\n"
        f"    Cooldown: {cooldown_info}\n"
    )
    if usage:
        formatted_string += f"    {usage}\n"
    if examples:
        formatted_string += f"    Examples:\n{examples}\n"

    return formatted_string


def format_duration(seconds: float) -> str:
    """
    Formats a duration in seconds into a human-readable string (e.g., '1h 30m 5s').
    """
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:  # Include seconds if there are any, or if the duration is 0
        parts.append(f"{seconds}s")

    return " ".join(parts)