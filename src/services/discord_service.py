import asyncio
import logging
import time
from typing import Dict, List, Optional

import discord

from config.logging import StructuredLogger
from config.settings import Settings
from core.exceptions import ConnectionError, CommandError
from core.interfaces import ICommand, ICommandRegistry, IDiscordService
from .bot_stats import BotStatsService
from .command_registry import CommandRegistry


class DiscordService(IDiscordService):
    def __init__(
        self,
        settings: Settings,
        command_registry: Optional[CommandRegistry] = None,
        bot_stats: Optional[BotStatsService] = None,
    ) -> None:
        self.settings = settings
        self.logger = StructuredLogger("services.discord")
        
        # Initialize Discord client
        intents = discord.Intents.default()
        intents.message_content = True  # Enable message content intent for self-bot
        self.client = discord.Client(
            intents=intents,
            heartbeat_timeout=settings.heartbeat_timeout,
            max_messages=None,  # Don't cache messages for self-bot
        )
        
        # Initialize services
        self.command_registry = command_registry or CommandRegistry()
        self.bot_stats = bot_stats or BotStatsService(self.client)
        
        # State management
        self._is_running = False
        self._shutdown_event = asyncio.Event()
        
        # Setup event handlers
        self._setup_event_handlers()
        
        self.logger.info("Discord service initialized")
    
    async def start(self) -> None:
        if self._is_running:
            self.logger.warning("Discord service is already running")
            return
        
        try:
            self.logger.info("Starting Discord service...")
            
            # Validate token before attempting connection
            await self._validate_token()
            
            # Connect to Discord
            self.logger.info("Connecting to Discord...")
            await self.client.login(self.settings.discord_token)
            
            # Start the client
            self._is_running = True
            
            # Run the client in a task so we can handle shutdown
            client_task = asyncio.create_task(self.client.connect())
            shutdown_task = asyncio.create_task(self._shutdown_event.wait())
            
            # Wait for either client completion or shutdown signal
            done, pending = await asyncio.wait(
                [client_task, shutdown_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel pending tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # Check if client task completed with an error
            if client_task in done:
                try:
                    await client_task
                except Exception as e:
                    raise ConnectionError(
                        f"Discord client error: {e}",
                        connection_type="discord_client",
                        error_code="CLIENT_ERROR"
                    ) from e
            
            self.logger.info("Discord service stopped")
            
        except Exception as e:
            self._is_running = False
            self.logger.error(f"Failed to start Discord service: {e}")
            await self._handle_connection_error(e)
            raise
    
    async def stop(self) -> None:
        if not self._is_running:
            self.logger.warning("Discord service is not running")
            return
        
        try:
            self.logger.info("Stopping Discord service...")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Close the Discord client
            if not self.client.is_closed():
                await self.client.close()
            
            self._is_running = False
            
            self.logger.info("Discord service stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping Discord service: {e}")
            raise
    
    async def register_command(self, command: ICommand) -> None:
        """
        Register a command with the service.
        
        Args:
            command: The command to register
        """
        await self.command_registry.register(command)
        self.logger.info(f"Registered command: {command.name}")
    
    def get_client(self) -> discord.Client:
        """
        Get the Discord client instance.
        
        Returns:
            The Discord client
        """
        return self.client
    
    def _setup_event_handlers(self) -> None:
        """Setup Discord client event handlers."""
        
        @self.client.event
        async def on_ready():
            """Handle client ready event."""
            user = self.client.user
            self.logger.info(
                f"Bot logged in as {user}",
                user_id=str(user.id) if user else None,
                username=str(user) if user else None
            )
            self.logger.warning("⚠️ Self-bot is now active - Use responsibly!")
        
        @self.client.event
        async def on_message(message: discord.Message):
            """Handle incoming messages."""
            await self._handle_message(message)
        
        @self.client.event
        async def on_error(event, *args, **kwargs):
            """Handle Discord client errors."""
            self.logger.error(f"Discord client error in {event}", event=event)
        
        @self.client.event
        async def on_disconnect():
            """Handle client disconnect."""
            self.logger.warning("Disconnected from Discord")
        
        @self.client.event
        async def on_resumed():
            """Handle client resume."""
            self.logger.info("Connection to Discord resumed")
    
    async def _handle_message(self, message: discord.Message) -> None:
        try:
            # Update message processing stats
            await self.bot_stats.increment_messages_processed()
            
            # Skip if message is not from the bot user (self-bot only responds to own messages)
            if not message.author or message.author.id != self.client.user.id:
                return
            
            # Skip empty messages
            if not message.content or not message.content.strip():
                return
            
            content = message.content.strip()
            
            # Find matching command
            command = await self._find_matching_command(content)
            if command:
                self.logger.debug(
                    f"Executing command: {command.name}",
                    command_name=command.name,
                    trigger=command.trigger,
                    user_id=str(message.author.id)
                )
                
                # Execute command and track statistics
                start_time = time.time()
                result = await command.execute(message)
                execution_time = (time.time() - start_time) * 1000
                
                # Update statistics
                await self.bot_stats.increment_commands_executed()
                await self.bot_stats.record_command_execution(
                    command.name, execution_time, result.success
                )
                
                if result.success:
                    self.logger.debug(
                        f"Command {command.name} executed successfully",
                        command_name=command.name,
                        execution_time=execution_time,
                        response_time=result.response_time
                    )
                else:
                    self.logger.warning(
                        f"Command {command.name} failed: {result.error}",
                        command_name=command.name,
                        error=result.error,
                        execution_time=execution_time
                    )
            
        except Exception as e:
            self.logger.error(f"Error handling message: {e}", error=str(e))
    
    async def _find_matching_command(self, content: str) -> Optional[ICommand]:
        # Get all registered commands
        commands = await self.command_registry.get_all_commands()
        
        # Find command with matching trigger
        for command in commands:
            if content.startswith(command.trigger):
                # Check if command is enabled
                if command.get_config().enabled:
                    return command
                else:
                    self.logger.debug(
                        f"Command {command.name} is disabled",
                        command_name=command.name
                    )
        
        return None
    
    async def _validate_token(self) -> None:
        token = self.settings.discord_token
        
        # Basic format validation
        if not token or len(token) < 50:
            raise ConnectionError(
                "Invalid Discord token format",
                connection_type="token_validation",
                error_code="INVALID_TOKEN_FORMAT"
            )
        
        self.logger.debug("Discord token format validation passed")
    
    async def _handle_connection_error(self, error: Exception) -> None:
        """
        Handle connection errors with specific guidance.
        
        Args:
            error: The error that occurred during connection
        """
        error_message = str(error).lower()
        
        if "token" in error_message and "invalid" in error_message:
            self.logger.error("💡 Token is invalid. Please check:")
            self.logger.error("   1. Token is correctly copied from Discord")
            self.logger.error("   2. Token is a USER token, not a BOT token")
            self.logger.error("   3. Token hasn't expired")
            self.logger.error("   4. Run token validation to verify")
        elif "rate" in error_message and "limit" in error_message:
            self.logger.error("💡 Rate limited. Please wait before retrying.")
        elif "network" in error_message or "connection" in error_message:
            self.logger.error("💡 Network error. Check your internet connection.")
        else:
            self.logger.error("💡 Unexpected connection error. Check logs for details.")
    
    @property
    def is_running(self) -> bool:
        """Check if the Discord service is running."""
        return self._is_running
    
    async def get_service_status(self) -> dict:
        stats = await self.bot_stats.get_stats()
        registry_stats = await self.command_registry.get_stats()
        
        return {
            "service_running": self._is_running,
            "client_ready": self.client.is_ready() if self.client else False,
            "client_closed": self.client.is_closed() if self.client else True,
            "connection_status": stats.status.value,
            "uptime_ms": stats.uptime,
            "ping_ms": stats.ping,
            "commands_executed": stats.commands_executed,
            "messages_processed": stats.messages_processed,
            "registered_commands": registry_stats["total_commands"],
            "enabled_commands": registry_stats["enabled_commands"],
        }
