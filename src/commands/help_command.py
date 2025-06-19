"""Help command implementation with enhanced formatting and categorization."""

from typing import Dict, List, Optional
import discord

from core.base_command import BaseCommand
from core.interfaces import ICommand, ICommandRegistry
from core.types import CommandConfig, CommandExecutionResult
from core.exceptions import CommandError


class HelpCommand(BaseCommand):
    # Help command: shows command list and details
    def __init__(self, command_registry: ICommandRegistry) -> None:
        super().__init__(
            command_name="help", config=CommandConfig(enabled=True, cooldown=2000)
        )
        self.command_registry = command_registry

    @property
    def name(self) -> str:
        return "help"

    @property
    def description(self) -> str:
        return (
            "Shows available commands and their descriptions with enhanced formatting"
        )

    @property
    def trigger(self) -> str:
        return ".help"

    async def execute_command(self, message: discord.Message) -> CommandExecutionResult:
        try:
            args = self._parse_arguments(message.content)
            if args and len(args) > 0:
                help_response = await self._build_detailed_help(args[0])
            else:
                help_response = await self._build_general_help()
            await message.edit(help_response)
            self.logger.debug(
                "Help command executed successfully",
                response_length=len(help_response),
                specific_command=args[0] if args else None,
            )
            return CommandExecutionResult(
                success=True,
                response=help_response,
                metadata={
                    "response_length": len(help_response),
                    "specific_command": args[0] if args else None,
                    "total_commands": len(
                        await self.command_registry.get_all_commands()
                    ),
                },
            )
        except Exception as error:
            self.logger.error(f"Failed to generate help response: {error}")
            raise CommandError(
                f"Failed to generate help: {error}",
                command_name=self.name,
                error_code="HELP_GENERATION_FAILED",
            ) from error

    async def _build_general_help(self) -> str:
        commands = await self.command_registry.get_all_commands()
        if not commands:
            return "❌ No commands available"
        categorized_commands = await self._categorize_commands(commands)
        sections: List[str] = []
        total_commands = len(commands)
        enabled_commands = len([cmd for cmd in commands if cmd.get_config().enabled])
        sections.append("📚 **Discord Self-Bot Commands**")
        sections.append("")
        sections.append(
            f"📊 **Statistics**: {enabled_commands}/{total_commands} commands enabled"
        )
        sections.append("")
        for category, category_commands in categorized_commands.items():
            if category_commands:
                sections.append(f"**{self._get_category_emoji(category)} {category}**")
                sorted_commands = sorted(category_commands, key=lambda x: x.name)
                for command in sorted_commands:
                    status_emoji = self._get_status_emoji(command)
                    trigger = command.trigger
                    description = command.description or "No description available"
                    if len(description) > 60:
                        description = description[:57] + "..."
                    sections.append(f"  {status_emoji} `{trigger}` - {description}")
                sections.append("")
        sections.append("💡 **Usage**: Type any command to execute it")
        sections.append(
            "📖 **Detailed Help**: `.help <command>` for specific command info"
        )
        sections.append("⚠️ **Note**: Self-bot for educational purposes only")
        return "\n".join(sections)

    async def _build_detailed_help(self, command_name: str) -> str:
        command = await self._find_command(command_name)
        if not command:
            return (
                f"❌ **Command not found**: `{command_name}`\n\n"
                f"💡 Use `.help` to see all available commands"
            )
        sections: List[str] = []
        sections.append(f"📖 **Help for `{command.trigger}`**")
        sections.append("")
        sections.append(f"**Name**: {command.name}")
        sections.append(
            f"**Description**: {command.description or 'No description available'}"
        )
        sections.append(f"**Usage**: `{command.trigger}`")
        sections.append("")
        config = command.get_config()
        sections.append("**Configuration**:")
        sections.append(
            f"• Status: {self._get_status_emoji(command)} {'Enabled' if config.enabled else 'Disabled'}"
        )
        if config.cooldown:
            cooldown_seconds = config.cooldown / 1000
            sections.append(f"• Cooldown: {cooldown_seconds:.1f}s")
        if config.aliases:
            sections.append(f"• Aliases: {', '.join(config.aliases)}")
        if config.permissions:
            sections.append(f"• Permissions: {', '.join(config.permissions)}")
        sections.append("")
        category = self._categorize_single_command(command)
        sections.append(
            f"**Category**: {self._get_category_emoji(category)} {category}"
        )
        sections.append("")
        sections.append("💡 **Tip**: Use `.help` to see all commands")
        return "\n".join(sections)

    async def _categorize_commands(
        self, commands: List[ICommand]
    ) -> Dict[str, List[ICommand]]:
        categories: Dict[str, List[ICommand]] = {
            "Utility": [],
            "Fun": [],
            "Information": [],
            "Moderation": [],
            "Other": [],
        }
        for command in commands:
            category = self._categorize_single_command(command)
            if category in categories:
                categories[category].append(command)
            else:
                categories["Other"].append(command)
        return {k: v for k, v in categories.items() if v}

    def _categorize_single_command(self, command: ICommand) -> str:
        name_lower = command.name.lower()
        utility_commands = {"ping", "help", "status", "info", "stats", "uptime"}
        if name_lower in utility_commands:
            return "Utility"
        fun_commands = {"hurt", "owo", "meow", "hentai", "joke", "meme", "ascii"}
        if name_lower in fun_commands:
            return "Fun"
        info_commands = {"user", "server", "channel", "role", "avatar", "whois"}
        if name_lower in info_commands:
            return "Information"
        mod_commands = {"ban", "kick", "mute", "warn", "clear", "purge"}
        if name_lower in mod_commands:
            return "Moderation"
        return "Other"

    def _get_category_emoji(self, category: str) -> str:
        category_emojis = {
            "Utility": "🔧",
            "Fun": "🎉",
            "Information": "ℹ️",
            "Moderation": "🛡️",
            "Other": "📦",
        }
        return category_emojis.get(category, "📦")

    def _get_status_emoji(self, command: ICommand) -> str:
        return "✅" if command.get_config().enabled else "❌"

    async def _find_command(self, identifier: str) -> Optional[ICommand]:
        if identifier.startswith("."):
            return await self.command_registry.get_command(identifier)
        trigger_with_dot = f".{identifier}"
        command = await self.command_registry.get_command(trigger_with_dot)
        if command:
            return command
        commands = await self.command_registry.get_all_commands()
        for command in commands:
            if command.name.lower() == identifier.lower():
                return command
        return None

    def _parse_arguments(self, content: str) -> List[str]:
        args_text = content[len(self.trigger) :].strip()
        if not args_text:
            return []
        return args_text.split()

    def __str__(self) -> str:
        return f"HelpCommand(trigger='{self.trigger}', enabled={self.config.enabled})"

    def __repr__(self) -> str:
        return (
            f"HelpCommand("
            f"name='{self.name}', "
            f"trigger='{self.trigger}', "
            f"enabled={self.config.enabled}, "
            f"cooldown={self.config.cooldown})"
        )
