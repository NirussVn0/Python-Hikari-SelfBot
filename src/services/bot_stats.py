import asyncio
import time
from datetime import datetime
from typing import Dict, Optional

import discord

from core.exceptions import ValidationError
from core.interfaces import IBotStats
from core.types import BotStats, ConnectionStatus, CommandMetrics
from config.logging import StructuredLogger


class BotStatsService(IBotStats):
    
    def __init__(self, client: discord.Client) -> None:
        self.client = client
        self.logger = StructuredLogger("services.bot_stats")
        
        # Core statistics
        self.start_time = datetime.now()
        self.commands_executed = 0
        self.messages_processed = 0
        self.last_activity = datetime.now()
        self.current_status = ConnectionStatus.DISCONNECTED
        
        # Performance metrics
        self.command_metrics: Dict[str, CommandMetrics] = {}
        
        # Thread safety
        self._lock = asyncio.Lock()
        
        # Setup event listeners
        self._setup_event_listeners()
        
        self.logger.info("Bot statistics service initialized")
    
    def _setup_event_listeners(self) -> None:
        """Setup event listeners to track bot activity."""
        
        @self.client.event
        async def on_ready():
            """Handle client ready event."""
            await self._update_status(ConnectionStatus.CONNECTED)
            await self.update_last_activity()
            self.logger.info(
                f"Bot connected as {self.client.user}",
                user_id=str(self.client.user.id) if self.client.user else None,
                username=str(self.client.user) if self.client.user else None
            )
        
        @self.client.event
        async def on_disconnect():
            """Handle client disconnect event."""
            await self._update_status(ConnectionStatus.DISCONNECTED)
            await self.update_last_activity()
            self.logger.warning("Bot disconnected from Discord")
        
        @self.client.event
        async def on_resumed():
            """Handle client resume event."""
            await self._update_status(ConnectionStatus.CONNECTED)
            await self.update_last_activity()
            self.logger.info("Bot connection resumed")
        
        @self.client.event
        async def on_error(event, *args, **kwargs):
            """Handle client error event."""
            await self._update_status(ConnectionStatus.ERROR)
            await self.update_last_activity()
            self.logger.error(f"Discord client error in {event}", event=event)
        
        @self.client.event
        async def on_message(message):
            """Handle message event."""
            await self.increment_messages_processed()
    
    async def increment_commands_executed(self) -> None:
        """Increment the count of executed commands."""
        async with self._lock:
            self.commands_executed += 1
            await self.update_last_activity()
            
            self.logger.debug(
                "Command executed",
                total_commands=self.commands_executed
            )
    
    async def increment_messages_processed(self) -> None:
        """Increment the count of processed messages."""
        async with self._lock:
            self.messages_processed += 1
            await self.update_last_activity()
    
    async def update_last_activity(self) -> None:
        """Update the timestamp of last activity."""
        async with self._lock:
            self.last_activity = datetime.now()
    
    async def get_uptime(self) -> float:
        """
        Get the bot uptime in milliseconds.
        
        Returns:
            Uptime in milliseconds
        """
        current_time = datetime.now()
        uptime_delta = current_time - self.start_time
        return uptime_delta.total_seconds() * 1000
    
    async def get_ping(self) -> float:
        """
        Get the current WebSocket ping.
        
        Returns:
            Ping in milliseconds
        """
        if self.client.ws and hasattr(self.client.ws, 'latency'):
            return self.client.ws.latency * 1000
        return 0.0
    
    async def get_stats(self) -> BotStats:
        """
        Get comprehensive bot statistics.
        
        Returns:
            BotStats object with current statistics
        """
        async with self._lock:
            return BotStats(
                status=self.current_status,
                ping=await self.get_ping(),
                uptime=await self.get_uptime(),
                commands_executed=self.commands_executed,
                messages_processed=self.messages_processed,
                last_activity=self.last_activity,
                start_time=self.start_time,
            )
    
    async def record_command_execution(
        self,
        command_name: str,
        execution_time: float,
        success: bool
    ) -> None:
        """
        Record command execution metrics.
        
        Args:
            command_name: Name of the executed command
            execution_time: Time taken for execution in milliseconds
            success: Whether the execution was successful
        """
        async with self._lock:
            if command_name not in self.command_metrics:
                self.command_metrics[command_name] = CommandMetrics(
                    command_name=command_name
                )
            
            self.command_metrics[command_name].update_metrics(execution_time, success)
            
            self.logger.debug(
                f"Recorded metrics for command {command_name}",
                command_name=command_name,
                execution_time=execution_time,
                success=success
            )
    
    async def get_command_metrics(self, command_name: str) -> Optional[CommandMetrics]:
        """
        Get metrics for a specific command.
        
        Args:
            command_name: Name of the command
            
        Returns:
            CommandMetrics object or None if not found
        """
        async with self._lock:
            return self.command_metrics.get(command_name)
    
    async def get_all_command_metrics(self) -> Dict[str, CommandMetrics]:
        """
        Get metrics for all commands.
        
        Returns:
            Dictionary mapping command names to their metrics
        """
        async with self._lock:
            return self.command_metrics.copy()
    
    async def get_performance_summary(self) -> Dict[str, any]:
        """
        Get a performance summary with key metrics.
        
        Returns:
            Dictionary with performance summary
        """
        async with self._lock:
            stats = await self.get_stats()
            
            # Calculate average command execution time
            total_execution_time = sum(
                metrics.total_execution_time 
                for metrics in self.command_metrics.values()
            )
            total_executions = sum(
                metrics.execution_count 
                for metrics in self.command_metrics.values()
            )
            avg_execution_time = (
                total_execution_time / total_executions 
                if total_executions > 0 else 0.0
            )
            
            # Find most used command
            most_used_command = None
            max_executions = 0
            for metrics in self.command_metrics.values():
                if metrics.execution_count > max_executions:
                    max_executions = metrics.execution_count
                    most_used_command = metrics.command_name
            
            return {
                "uptime_hours": stats.uptime / (1000 * 60 * 60),
                "total_commands": stats.commands_executed,
                "total_messages": stats.messages_processed,
                "avg_execution_time_ms": avg_execution_time,
                "current_ping_ms": stats.ping,
                "connection_status": stats.status.value,
                "most_used_command": most_used_command,
                "unique_commands_used": len(self.command_metrics),
                "success_rate": self._calculate_success_rate(),
            }
    
    async def reset_stats(self) -> None:
        """Reset all statistics (except start time)."""
        async with self._lock:
            self.commands_executed = 0
            self.messages_processed = 0
            self.command_metrics.clear()
            
            self.logger.info("Bot statistics reset")
    
    async def _update_status(self, status: ConnectionStatus) -> None:
        """
        Update the connection status.
        
        Args:
            status: New connection status
        """
        async with self._lock:
            old_status = self.current_status
            self.current_status = status
            
            if old_status != status:
                self.logger.info(
                    f"Connection status changed: {old_status.value} -> {status.value}",
                    old_status=old_status.value,
                    new_status=status.value
                )
    
    def _calculate_success_rate(self) -> float:
        """
        Calculate overall command success rate.
        
        Returns:
            Success rate as a percentage (0-100)
        """
        total_success = sum(
            metrics.success_count 
            for metrics in self.command_metrics.values()
        )
        total_executions = sum(
            metrics.execution_count 
            for metrics in self.command_metrics.values()
        )
        
        if total_executions == 0:
            return 100.0
        
        return (total_success / total_executions) * 100
    
    async def export_metrics(self) -> Dict[str, any]:
        """
        Export all metrics for external monitoring.
        
        Returns:
            Dictionary with all metrics data
        """
        async with self._lock:
            stats = await self.get_stats()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "bot_stats": {
                    "status": stats.status.value,
                    "ping_ms": stats.ping,
                    "uptime_ms": stats.uptime,
                    "commands_executed": stats.commands_executed,
                    "messages_processed": stats.messages_processed,
                    "start_time": stats.start_time.isoformat(),
                    "last_activity": stats.last_activity.isoformat(),
                },
                "command_metrics": {
                    name: {
                        "execution_count": metrics.execution_count,
                        "total_execution_time": metrics.total_execution_time,
                        "average_execution_time": metrics.average_execution_time,
                        "min_execution_time": metrics.min_execution_time,
                        "max_execution_time": metrics.max_execution_time,
                        "success_count": metrics.success_count,
                        "error_count": metrics.error_count,
                        "last_executed": (
                            metrics.last_executed.isoformat() 
                            if metrics.last_executed else None
                        ),
                    }
                    for name, metrics in self.command_metrics.items()
                },
                "performance_summary": await self.get_performance_summary(),
            }
