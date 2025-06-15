"""
Abstract base class for all Discord commands.

This module provides the BaseCommand abstract class that implements common
functionality and enforces command structure following the Command pattern
and SOLID principles.
"""

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
    """
    Abstract base class for all Discord commands.
    
    This class implements common functionality and enforces command structure
    following the Command pattern. It provides:
    - Error handling and logging
    - Command configuration management
    - Execution timing and metrics
    - Message validation
    - Cooldown management
    
    All concrete command implementations must inherit from this class and
    implement the execute_command method.
    """
    
    def __init__(
        self,
        command_name: str,
        config: Optional[CommandConfig] = None,
    ) -> None:
        """
        Initialize the base command.
        
        Args:
            command_name: The name of the command
            config: Command configuration options
        """
        self.command_name = command_name
        self.config = config or CommandConfig()
        self.logger = logging.getLogger(f"commands.{command_name}")
        
        # Cooldown tracking
        self._last_execution: Dict[str, float] = {}
        self._execution_lock = asyncio.Lock()
        
        self.logger.debug(f"Initialized command: {command_name}")
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the command."""
        ...
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the command does."""
        ...
    
    @property
    @abstractmethod
    def trigger(self) -> str:
        """The trigger text that activates this command."""
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
                cooldown_remaining = await self._get_cooldown_remaining(message.author.id)
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
                    error_code="INVALID_MESSAGE"
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
                }
            )
    
    @abstractmethod
    async def execute_command(self, message: discord.Message) -> CommandExecutionResult:
        """
        Abstract method that subclasses must implement.
        
        This method contains the actual command logic and should be
        implemented by all concrete command classes.
        
        Args:
            message: The Discord message that triggered the command
            
        Returns:
            CommandExecutionResult: Result of the command execution
        """
        ...
    
    async def _validate_message(self, message: discord.Message) -> bool:
        """
        Validate the Discord message.
        
        This method performs basic validation on the message to ensure
        it's suitable for command execution.
        
        Args:
            message: The Discord message to validate
            
        Returns:
            True if message is valid, False otherwise
        """
        if not message:
            return False
        
        if not message.author:
            return False
        
        if not message.content:
            return False
        
        # Check if message starts with the command trigger
        if not message.content.strip().startswith(self.trigger):
            return False
        
        return True
    
    async def _check_cooldown(self, user_id: int) -> bool:
        """
        Check if the command is on cooldown for a user.
        
        Args:
            user_id: The Discord user ID
            
        Returns:
            True if command can be executed, False if on cooldown
        """
        if not self.config.cooldown:
            return True
        
        async with self._execution_lock:
            last_execution = self._last_execution.get(str(user_id), 0)
            current_time = time.time()
            
            return (current_time - last_execution) >= (self.config.cooldown / 1000)
    
    async def _get_cooldown_remaining(self, user_id: int) -> float:
        """
        Get the remaining cooldown time for a user.
        
        Args:
            user_id: The Discord user ID
            
        Returns:
            Remaining cooldown time in seconds
        """
        if not self.config.cooldown:
            return 0.0
        
        async with self._execution_lock:
            last_execution = self._last_execution.get(str(user_id), 0)
            current_time = time.time()
            cooldown_seconds = self.config.cooldown / 1000
            
            remaining = cooldown_seconds - (current_time - last_execution)
            return max(0.0, remaining)
    
    async def _update_cooldown(self, user_id: int) -> None:
        """
        Update the cooldown timestamp for a user.
        
        Args:
            user_id: The Discord user ID
        """
        if self.config.cooldown:
            async with self._execution_lock:
                self._last_execution[str(user_id)] = time.time()
    
    async def _handle_error(self, message: discord.Message, error: Exception) -> None:
        """
        Handle command execution errors.
        
        This method attempts to send an error message to the user and
        logs the error for debugging purposes.
        
        Args:
            message: The Discord message that triggered the command
            error: The exception that occurred
        """
        try:
            # Create user-friendly error message
            if isinstance(error, CommandError):
                error_msg = f"❌ Command failed: {error.message}"
            elif isinstance(error, ValidationError):
                error_msg = "❌ Invalid input. Please check your command format."
            else:
                error_msg = "❌ An unexpected error occurred. Please try again."
            
            # Try to edit the original message with error
            await message.edit(error_msg)
            
        except Exception as edit_error:
            self.logger.error(
                f"Failed to send error message for command {self.name}: {edit_error}"
            )
    
    def get_config(self) -> CommandConfig:
        """
        Get the command configuration.
        
        Returns:
            CommandConfig: The current command configuration
        """
        return self.config
    
    def update_config(self, config: CommandConfig) -> None:
        """
        Update the command configuration.
        
        Args:
            config: New configuration to apply
        """
        self.config = config
        self.logger.debug(f"Updated configuration for command {self.name}")
    
    def __str__(self) -> str:
        """Return string representation of the command."""
        return f"{self.__class__.__name__}(name='{self.name}', trigger='{self.trigger}')"
    
    def __repr__(self) -> str:
        """Return detailed representation of the command."""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"trigger='{self.trigger}', "
            f"enabled={self.config.enabled}, "
            f"cooldown={self.config.cooldown})"
        )
