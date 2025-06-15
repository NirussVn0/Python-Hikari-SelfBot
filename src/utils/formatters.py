from typing import Dict, List, Optional, Any
from ..core.types import CommandConfig


class MessageFormatter:

    @staticmethod
    def format_command_output(content: str, success: bool = True) -> str:
        """Format standard command output with appropriate styling."""
        prefix = "✅" if success else "❌"
        return f"{prefix} {content}"
    
    @staticmethod
    def format_code_block(content: str, language: str = "") -> str:
        """Format content as a Discord code block with optional language."""
        return f"```{language}\n{content}\n```"
    
    @staticmethod
    def format_info_message(title: str, content: str) -> str:
        """Format an information message with a title."""
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