"""
Protocol interfaces for the Discord self-bot.

This module defines the core interfaces using Python's Protocol system,
providing type safety and clear contracts for different components of
the application. These interfaces follow the Interface Segregation
Principle from SOLID.
"""

from typing import List, Optional, Protocol, runtime_checkable

import discord

from .types import CommandExecutionResult


@runtime_checkable
class ICommand(Protocol):
    """
    Interface for Discord bot commands.
    
    This protocol defines the contract that all commands must implement.
    It ensures type safety and provides a clear interface for command
    implementations.
    
    All commands must have a name, description, trigger, and execute method.
    The execute method should handle the command logic and return a result.
    """
    
    @property
    def name(self) -> str:
        """The name of the command."""
        ...
    
    @property
    def description(self) -> str:
        """Description of what the command does."""
        ...
    
    @property
    def trigger(self) -> str:
        """The trigger text that activates this command."""
        ...
    
    async def execute(self, message: discord.Message) -> CommandExecutionResult:
        """
        Execute the command.
        
        Args:
            message: The Discord message that triggered the command
            
        Returns:
            CommandExecutionResult: Result of the command execution
        """
        ...


@runtime_checkable
class ICommandRegistry(Protocol):
    """
    Interface for command registry.
    
    This protocol defines the contract for managing command registration
    and retrieval. It provides a centralized way to manage all available
    commands in the bot.
    
    The registry should be thread-safe and support async operations.
    """
    
    async def register(self, command: ICommand) -> None:
        """
        Register a command in the registry.
        
        Args:
            command: The command to register
            
        Raises:
            ValueError: If command is invalid or already registered
        """
        ...
    
    async def get_command(self, trigger: str) -> Optional[ICommand]:
        """
        Get a command by its trigger.
        
        Args:
            trigger: The trigger text
            
        Returns:
            The command if found, None otherwise
        """
        ...
    
    async def get_all_commands(self) -> List[ICommand]:
        """
        Get all registered commands.
        
        Returns:
            List of all registered commands
        """
        ...
    
    async def has_command(self, trigger: str) -> bool:
        """
        Check if a trigger is registered.
        
        Args:
            trigger: The trigger text to check
            
        Returns:
            True if trigger is registered, False otherwise
        """
        ...
    
    async def unregister(self, trigger: str) -> bool:
        """
        Unregister a command.
        
        Args:
            trigger: The trigger of the command to unregister
            
        Returns:
            True if command was removed, False if not found
        """
        ...
    
    async def clear(self) -> None:
        """Clear all registered commands."""
        ...


@runtime_checkable
class IBotStats(Protocol):
    """
    Interface for bot statistics tracking.
    
    This protocol defines the contract for tracking and managing bot
    statistics, including performance metrics, activity counters,
    and health monitoring.
    """
    
    async def increment_commands_executed(self) -> None:
        """Increment the count of executed commands."""
        ...
    
    async def increment_messages_processed(self) -> None:
        """Increment the count of processed messages."""
        ...
    
    async def update_last_activity(self) -> None:
        """Update the timestamp of last activity."""
        ...
    
    async def get_uptime(self) -> float:
        """
        Get the bot uptime in milliseconds.
        
        Returns:
            Uptime in milliseconds
        """
        ...
    
    async def get_ping(self) -> float:
        """
        Get the current WebSocket ping.
        
        Returns:
            Ping in milliseconds
        """
        ...


@runtime_checkable
class IDiscordService(Protocol):
    """
    Interface for Discord service.
    
    This protocol defines the contract for the main Discord service
    that manages the Discord client and coordinates between different
    components of the bot.
    """
    
    async def start(self) -> None:
        """Start the Discord service and connect to Discord."""
        ...
    
    async def stop(self) -> None:
        """Stop the Discord service and disconnect from Discord."""
        ...
    
    async def register_command(self, command: ICommand) -> None:
        """
        Register a command with the service.
        
        Args:
            command: The command to register
        """
        ...
    
    def get_client(self) -> discord.Client:
        """
        Get the Discord client instance.
        
        Returns:
            The Discord client
        """
        ...


@runtime_checkable
class ITokenValidator(Protocol):
    """
    Interface for Discord token validation.
    
    This protocol defines the contract for validating Discord tokens,
    including format validation and API validation.
    """
    
    async def validate_format(self, token: str) -> bool:
        """
        Validate token format.
        
        Args:
            token: The token to validate
            
        Returns:
            True if format is valid, False otherwise
        """
        ...
    
    async def validate_api(self, token: str) -> bool:
        """
        Validate token with Discord API.
        
        Args:
            token: The token to validate
            
        Returns:
            True if token is valid with Discord, False otherwise
        """
        ...
    
    async def extract_info(self, token: str) -> dict:
        """
        Extract information from token.
        
        Args:
            token: The token to extract info from
            
        Returns:
            Dictionary containing token information
        """
        ...


@runtime_checkable
class IConfigService(Protocol):
    """
    Interface for configuration service.
    
    This protocol defines the contract for managing application
    configuration, including environment variables and settings.
    """
    
    @property
    def discord_token(self) -> str:
        """Get the Discord token from configuration."""
        ...
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        ...
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        ...
    
    @property
    def log_level(self) -> str:
        """Get the logging level."""
        ...
