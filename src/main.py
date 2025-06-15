"""
Main application entry point for the Discord self-bot.

This module provides the main entry point and application lifecycle management
for the Discord self-bot, including service initialization, command registration,
and graceful shutdown handling.
"""

import asyncio
import signal
import sys
from typing import Optional

from config.logging import setup_logging, get_logger
from config.settings import get_settings, Settings
from core.exceptions import DiscordSelfBotError, ConfigurationError
from services.discord_service import DiscordService
from services.command_registry import CommandRegistry
from services.bot_stats import BotStatsService
from commands.ping_command import PingCommand
from commands.help_command import HelpCommand


class DiscordSelfBot:
    """
    Main application class for the Discord self-bot.
    
    This class manages the application lifecycle, service initialization,
    and coordination between different components of the bot.
    
    Features:
    - Service lifecycle management
    - Command registration and setup
    - Graceful shutdown handling
    - Error handling and recovery
    - Configuration management
    """
    
    def __init__(self, settings: Optional[Settings] = None) -> None:
        """
        Initialize the Discord self-bot application.
        
        Args:
            settings: Application settings (will be loaded if not provided)
        """
        # Load settings
        self.settings = settings or get_settings()
        
        # Setup logging
        setup_logging(self.settings)
        self.logger = get_logger("main")
        
        # Initialize services
        self.command_registry = CommandRegistry()
        self.discord_service: Optional[DiscordService] = None
        self.bot_stats: Optional[BotStatsService] = None
        
        # Shutdown handling
        self._shutdown_event = asyncio.Event()
        self._setup_signal_handlers()
        
        self.logger.info("Discord self-bot application initialized")
    
    async def start(self) -> None:
        """
        Start the Discord self-bot application.
        
        This method initializes all services, registers commands, and starts
        the Discord client connection.
        
        Raises:
            DiscordSelfBotError: If startup fails
        """
        try:
            self.logger.info("🚀 Starting Discord self-bot...")
            
            # Display startup information
            await self._display_startup_info()
            
            # Initialize services
            await self._initialize_services()
            
            # Register commands
            await self._register_commands()
            
            # Start Discord service
            self.logger.info("🔗 Connecting to Discord...")
            await self.discord_service.start()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start Discord self-bot: {e}")
            await self._cleanup()
            raise DiscordSelfBotError(
                f"Application startup failed: {e}",
                error_code="STARTUP_FAILED"
            ) from e
    
    async def stop(self) -> None:
        """
        Stop the Discord self-bot application.
        
        This method gracefully shuts down all services and cleans up resources.
        """
        try:
            self.logger.info("🛑 Stopping Discord self-bot...")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Stop Discord service
            if self.discord_service:
                await self.discord_service.stop()
            
            # Cleanup resources
            await self._cleanup()
            
            self.logger.info("✅ Discord self-bot stopped successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error during shutdown: {e}")
            raise
    
    async def _initialize_services(self) -> None:
        """Initialize all application services."""
        self.logger.info("⚙️ Initializing services...")
        
        # Create Discord service with command registry
        self.discord_service = DiscordService(
            settings=self.settings,
            command_registry=self.command_registry
        )
        
        # Get bot stats service from Discord service
        self.bot_stats = self.discord_service.bot_stats
        
        self.logger.info("✅ Services initialized successfully")
    
    async def _register_commands(self) -> None:
        """Register all available commands."""
        self.logger.info("📝 Registering commands...")
        
        try:
            # Create command instances
            ping_command = PingCommand(self.discord_service.get_client())
            help_command = HelpCommand(self.command_registry)
            
            # Register commands
            await self.discord_service.register_command(ping_command)
            await self.discord_service.register_command(help_command)
            
            # Get registration statistics
            stats = await self.command_registry.get_stats()
            self.logger.info(
                f"✅ Registered {stats['total_commands']} commands successfully",
                total_commands=stats['total_commands'],
                enabled_commands=stats['enabled_commands']
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register commands: {e}")
            raise
    
    async def _display_startup_info(self) -> None:
        """Display startup information and warnings."""
        self.logger.info("=" * 60)
        self.logger.info("🤖 Discord Self-Bot Python Implementation")
        self.logger.info("=" * 60)
        self.logger.info(f"📊 Environment: {self.settings.environment}")
        self.logger.info(f"🐛 Debug Mode: {self.settings.debug}")
        self.logger.info(f"📝 Log Level: {self.settings.get_effective_log_level()}")
        self.logger.info("=" * 60)
        
        # Display warnings
        self.logger.warning("⚠️ WARNING: Self-bots violate Discord's Terms of Service")
        self.logger.warning("⚠️ This implementation is for educational purposes only!")
        self.logger.warning("⚠️ Use at your own risk!")
        self.logger.info("=" * 60)
    
    async def _cleanup(self) -> None:
        """Cleanup resources and perform final tasks."""
        try:
            # Export final metrics if enabled
            if self.settings.enable_metrics and self.bot_stats:
                metrics = await self.bot_stats.export_metrics()
                self.logger.debug("Final metrics exported", **metrics.get("performance_summary", {}))
            
            self.logger.debug("Cleanup completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            """Handle shutdown signals."""
            signal_name = signal.Signals(signum).name
            self.logger.info(f"Received {signal_name}, initiating graceful shutdown...")
            
            # Set shutdown event
            if not self._shutdown_event.is_set():
                self._shutdown_event.set()
                
                # Schedule shutdown coroutine
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.stop())
                else:
                    asyncio.run(self.stop())
        
        # Register signal handlers
        if sys.platform != "win32":
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
    
    @property
    def is_running(self) -> bool:
        """Check if the application is running."""
        return (
            self.discord_service is not None and 
            self.discord_service.is_running and
            not self._shutdown_event.is_set()
        )
    
    async def get_status(self) -> dict:
        """
        Get the current application status.
        
        Returns:
            Dictionary with application status information
        """
        status = {
            "application_running": self.is_running,
            "shutdown_requested": self._shutdown_event.is_set(),
            "environment": self.settings.environment,
            "debug_mode": self.settings.debug,
        }
        
        if self.discord_service:
            service_status = await self.discord_service.get_service_status()
            status.update(service_status)
        
        return status


async def main() -> None:
    """
    Main entry point for the Discord self-bot application.
    
    This function handles application startup, running, and shutdown
    with proper error handling and logging.
    """
    bot = None
    
    try:
        # Load settings and validate configuration
        settings = get_settings()
        
        # Create and start the bot
        bot = DiscordSelfBot(settings)
        await bot.start()
        
        # Keep the application running until shutdown
        while bot.is_running:
            await asyncio.sleep(1)
        
    except ConfigurationError as e:
        print(f"❌ Configuration Error: {e}")
        print("💡 Please check your .env file and configuration settings")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
        
    finally:
        # Ensure cleanup
        if bot:
            try:
                await bot.stop()
            except Exception as e:
                print(f"❌ Error during shutdown: {e}")


def run() -> None:
    try:
        # Use uvloop if available for better performance
        try:
            import uvloop
            uvloop.install()
        except ImportError:
            pass
        
        # Run the main coroutine
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()
