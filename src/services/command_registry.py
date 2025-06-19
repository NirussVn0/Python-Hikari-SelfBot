import asyncio
from typing import Dict, List, Optional

from core.exceptions import CommandError, ValidationError
from core.interfaces import ICommand, ICommandRegistry
from config.logging import StructuredLogger


class CommandRegistry(ICommandRegistry):
    def __init__(self) -> None:
        self.logger = StructuredLogger("services.command_registry")
        self._commands: Dict[str, ICommand] = {}
        self._command_names: Dict[str, ICommand] = {}
        self._lock = asyncio.Lock()
        self._stats = {
            "total_registered": 0,
            "total_unregistered": 0,
            "registration_errors": 0,
        }
        self.logger.info("Command registry initialized")

    async def register(self, command: ICommand) -> None:
        if not command:
            raise ValidationError(
                "Command cannot be None",
                field_name="command",
                error_code="NULL_COMMAND",
            )

        await self._validate_command(command)

        async with self._lock:
            try:
                if command.trigger in self._commands:
                    existing_command = self._commands[command.trigger]
                    self.logger.warning(
                        f"Overwriting command '{existing_command.name}' with '{command.name}'",
                        trigger=command.trigger,
                        existing_command=existing_command.name,
                        new_command=command.name,
                    )

                if command.name in self._command_names:
                    existing_command = self._command_names[command.name]
                    if existing_command.trigger != command.trigger:
                        raise CommandError(
                            f"Command name '{command.name}' already exists with "
                            f"different trigger '{existing_command.trigger}'",
                            command_name=command.name,
                            error_code="DUPLICATE_COMMAND_NAME",
                        )

                self._commands[command.trigger] = command
                self._command_names[command.name] = command
                self._stats["total_registered"] += 1

                self.logger.info(f"Registered command: {command.name}", trigger=command.trigger)
            except Exception as e:
                self._stats["registration_errors"] += 1
                self.logger.error(f"Failed to register command: {command.name}", error=str(e))
                raise

    async def get_command(self, trigger: str) -> Optional[ICommand]:
        """Get a command by its trigger."""
        if not trigger:
            return None
        async with self._lock:
            return self._commands.get(trigger)

    async def get_command_by_name(self, name: str) -> Optional[ICommand]:
        """Get a command by its name."""
        if not name:
            return None
        async with self._lock:
            return self._command_names.get(name)

    async def get_all_commands(self) -> List[ICommand]:
        """Get all registered commands."""
        async with self._lock:
            return list(self._commands.values())

    async def has_command(self, trigger: str) -> bool:
        """Check if a trigger is registered."""
        if not trigger:
            return False
        async with self._lock:
            return trigger in self._commands

    async def unregister(self, trigger: str) -> bool:
        """Unregister a command by trigger."""
        if not trigger:
            return False

        async with self._lock:
            command = self._commands.get(trigger)
            if command:
                del self._commands[trigger]
                if command.name in self._command_names:
                    del self._command_names[command.name]

                self._stats["total_unregistered"] += 1
                self.logger.info(
                    f"Unregistered command: {command.name}",
                    command_name=command.name,
                    trigger=trigger,
                    total_commands=len(self._commands),
                )
                return True
            else:
                self.logger.warning(f"Command not found: {trigger}", trigger=trigger)
                return False

    async def clear(self) -> None:
        """Clear all registered commands."""
        async with self._lock:
            command_count = len(self._commands)
            self._commands.clear()
            self._command_names.clear()
            self.logger.info(
                f"Cleared {command_count} commands", cleared_count=command_count
            )

    async def get_stats(self) -> Dict[str, any]:
        """Get command registry statistics."""
        async with self._lock:
            commands = list(self._commands.values())
            return {
                "total_commands": len(commands),
                "triggers": list(self._commands.keys()),
                "command_names": [cmd.name for cmd in commands],
                "enabled_commands": len(
                    [cmd for cmd in commands if cmd.get_config().enabled]
                ),
                "disabled_commands": len(
                    [cmd for cmd in commands if not cmd.get_config().enabled]
                ),
                "registration_stats": self._stats.copy(),
            }

    async def find_commands(self, partial_trigger: str) -> List[ICommand]:
        """Find commands that match a partial trigger."""
        if not partial_trigger:
            return []

        async with self._lock:
            partial_lower = partial_trigger.lower()
            return [
                command
                for trigger, command in self._commands.items()
                if partial_lower in trigger.lower()
            ]

    async def get_commands_by_category(self) -> Dict[str, List[ICommand]]:
        """Get commands grouped by category."""
        async with self._lock:
            categories: Dict[str, List[ICommand]] = {}
            for command in self._commands.values():
                category = self._categorize_command(command)
                if category not in categories:
                    categories[category] = []
                categories[category].append(command)
            return categories

    async def validate_all_commands(self) -> Dict[str, List[str]]:
        """Validate all registered commands."""
        async with self._lock:
            results = {"valid": [], "invalid": [], "errors": []}
            for command in self._commands.values():
                try:
                    await self._validate_command(command)
                    results["valid"].append(command.name)
                except Exception as e:
                    results["invalid"].append(command.name)
                    results["errors"].append(f"{command.name}: {str(e)}")
            return results

    async def _validate_command(self, command: ICommand) -> None:
        """Validate a command implementation."""
        if not hasattr(command, "name") or not command.name:
            raise ValidationError(
                "Command must have a non-empty name",
                field_name="name",
                error_code="MISSING_NAME",
            )

        if not hasattr(command, "description") or not command.description:
            raise ValidationError(
                "Command must have a non-empty description",
                field_name="description",
                error_code="MISSING_DESCRIPTION",
            )

        if not hasattr(command, "trigger") or not command.trigger:
            raise ValidationError(
                "Command must have a non-empty trigger",
                field_name="trigger",
                error_code="MISSING_TRIGGER",
            )

        if not hasattr(command, "execute") or not callable(command.execute):
            raise ValidationError(
                "Command must have an executable 'execute' method",
                field_name="execute",
                error_code="MISSING_EXECUTE_METHOD",
            )

        if not command.trigger.startswith("."):
            raise ValidationError(
                "Command trigger must start with '.'",
                field_name="trigger",
                field_value=command.trigger,
                error_code="INVALID_TRIGGER_FORMAT",
            )

    def _categorize_command(self, command: ICommand) -> str:
        """Categorize a command based on its name."""
        name_lower = command.name.lower()

        categories = {
            "Utility": {"ping", "help", "status", "info", "stats"},
            "Fun": {"hurt", "owo", "meow", "hentai", "joke", "meme"},
            "Moderation": {"ban", "kick", "mute", "warn", "clear"},
            "Information": {"user", "server", "channel", "role"},
        }

        for category, commands in categories.items():
            if name_lower in commands:
                return category

        return "Other"
