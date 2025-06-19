import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Optional

import discord

from .exceptions import CommandError, ValidationError
from .interfaces import ICommand
from .types import CommandConfig, CommandExecutionResult


class BaseCommand(ABC, ICommand):
    def __init__(self, command_name: str, config: Optional[CommandConfig] = None) -> None:
        self.command_name = command_name
        self.config = config or CommandConfig()
        self.logger = logging.getLogger(f"commands.{command_name}")
        self._last_execution: Dict[str, float] = {}
        self._execution_lock = asyncio.Lock()
        self.logger.debug(f"Initialized command: {command_name}")

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        ...

    @property
    @abstractmethod
    def trigger(self) -> str:
        ...

    async def execute(self, message: discord.Message) -> CommandExecutionResult:
        """
        Execute the command with error handling and logging.

        This method provides the common execution flow for all commands:
        1. Validate the command is enabled
        2. Check cooldowns
        3. Validate the message
        4. Execute the command logic
        5. Handle errors and logging
        6. Return execution result

        Args:
            message: The Discord message that triggered the command

        Returns:
            CommandExecutionResult: Result of the command execution
        """
        start_time = time.time()

        try:
            # Check if command is enabled
            if not self.config.enabled:
                self.logger.warning(f"Command {self.name} is disabled")
                return CommandExecutionResult(
                    success=False,
                    error="Command is currently disabled",
                    response_time=(time.time() - start_time) * 1000,
                )

            # Check cooldown
            if not await self._check_cooldown(message.author.id):
                cooldown_remaining = await self._get_cooldown_remaining(
                    message.author.id
                )
                self.logger.debug(
                    f"Command {self.name} on cooldown for user {message.author.id}, "
                    f"{cooldown_remaining:.1f}s remaining"
                )
                return CommandExecutionResult(
                    success=False,
                    error=f"Command on cooldown. Try again in {cooldown_remaining:.1f}s",
                    response_time=(time.time() - start_time) * 1000,
                )

            # Validate the message
            if not await self._validate_message(message):
                raise ValidationError(
                    "Invalid message format or content",
                    field_name="message",
                    error_code="INVALID_MESSAGE",
                )

            self.logger.debug(f"Executing command: {self.name}")

            # Execute the actual command logic
            result = await self.execute_command(message)

            # Update cooldown
            await self._update_cooldown(message.author.id)

            # Add response time if not already set
            if result.response_time is None:
                result.response_time = (time.time() - start_time) * 1000

            # Add command name to metadata
            if result.metadata is None:
                result.metadata = {}
            result.metadata["command_name"] = self.name
            result.metadata["user_id"] = str(message.author.id)

            self.logger.debug(
                f"Command {self.name} executed successfully in "
                f"{result.response_time:.2f}ms"
            )

            return result

        except Exception as error:
            response_time = (time.time() - start_time) * 1000
            self.logger.error(f"Failed to execute command {self.name}: {error}")

            # Try to send error message to user
            await self._handle_error(message, error)

            return CommandExecutionResult(
                success=False,
                error=str(error),
                response_time=response_time,
                metadata={
                    "command_name": self.name,
                    "user_id": str(message.author.id),
                    "error_type": type(error).__name__,
                },
            )

    @abstractmethod
    async def execute_command(self, message: discord.Message) -> CommandExecutionResult:
        ...
