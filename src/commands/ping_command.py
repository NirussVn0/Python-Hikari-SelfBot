"""Ping command implementation with enhanced latency tracking."""

import time
from typing import Optional

import discord

from core.base_command import BaseCommand
from core.types import CommandConfig, CommandExecutionResult
from core.exceptions import CommandError


class PingCommand(BaseCommand):
    """Ping command with enhanced latency tracking and connection quality indicators."""

    def __init__(self, client: discord.Client) -> None:
        super().__init__(
            command_name="ping",
            config=CommandConfig(enabled=True, cooldown=1000)
        )
        self.client = client
    
    @property
    def name(self) -> str:
        return "ping"

    @property
    def description(self) -> str:
        return "Responds with pong and WebSocket latency information"

    @property
    def trigger(self) -> str:
        return ".ping"
    
    async def execute_command(self, message: discord.Message) -> CommandExecutionResult:
        """Execute the ping command with latency measurement."""
        try:
            ws_latency = await self._get_websocket_latency()
            start_time = time.time()

            response = self._format_response(ws_latency)
            await message.edit(response)

            response_time = (time.time() - start_time) * 1000

            self.logger.debug(
                "Ping command executed successfully",
                ws_latency=ws_latency,
                response_time=response_time
            )

            return CommandExecutionResult(
                success=True,
                response=response,
                latency=ws_latency,
                response_time=response_time,
                metadata={
                    "ws_latency": ws_latency,
                    "connection_quality": self._assess_connection_quality(ws_latency),
                    "client_ready": self.client.is_ready(),
                }
            )

        except Exception as error:
            self.logger.error(f"Failed to execute ping command: {error}")
            raise CommandError(
                f"Failed to measure latency: {error}",
                command_name=self.name,
                error_code="LATENCY_MEASUREMENT_FAILED"
            ) from error
    
    async def _get_websocket_latency(self) -> float:
        try:
            if not self.client.ws:
                raise CommandError(
                    "WebSocket connection not available",
                    command_name=self.name,
                    error_code="NO_WEBSOCKET"
                )
            
            # Get latency from Discord client
            latency_seconds = self.client.ws.latency
            latency_ms = latency_seconds * 1000
            
            # Validate latency value
            if latency_ms < 0:
                raise CommandError(
                    "Invalid latency value received",
                    command_name=self.name,
                    error_code="INVALID_LATENCY"
                )
            
            return round(latency_ms, 2)
            
        except AttributeError as e:
            raise CommandError(
                "WebSocket latency not available",
                command_name=self.name,
                error_code="LATENCY_UNAVAILABLE"
            ) from e
    
    def _format_response(self, latency: float) -> str:
        # Get connection quality assessment
        quality = self._assess_connection_quality(latency)
        emoji = self._get_quality_emoji(quality)
        
        # Format latency with appropriate precision
        if latency < 10:
            latency_str = f"{latency:.1f}ms"
        else:
            latency_str = f"{int(latency)}ms"
        
        # Create response with quality indicator
        response = f"{emoji} pong {latency_str}"
        
        # Add quality description for very poor connections
        if quality == "poor":
            response += " (slow connection)"
        elif quality == "excellent":
            response += " (excellent)"
        
        return response
    
    def _assess_connection_quality(self, latency: float) -> str:
        if latency < 50:
            return "excellent"
        elif latency < 100:
            return "good"
        elif latency < 200:
            return "fair"
        else:
            return "poor"
    
    def _get_quality_emoji(self, quality: str) -> str:
        quality_emojis = {
            "excellent": "🟢",
            "good": "🟡", 
            "fair": "🟠",
            "poor": "🔴"
        }
        return quality_emojis.get(quality, "⚪")
    
    def get_latency_stats(self) -> Optional[dict]:
        try:
            if not self.client.ws:
                return None
            
            latency = self.client.ws.latency * 1000
            
            return {
                "latency_ms": round(latency, 2),
                "quality": self._assess_connection_quality(latency),
                "client_ready": self.client.is_ready(),
                "websocket_available": True,
            }
            
        except (AttributeError, TypeError):
            return {
                "latency_ms": None,
                "quality": "unknown",
                "client_ready": False,
                "websocket_available": False,
            }
    
    def __str__(self) -> str:
        """Return string representation of the ping command."""
        return f"PingCommand(trigger='{self.trigger}', enabled={self.config.enabled})"
    
    def __repr__(self) -> str:
        """Return detailed representation of the ping command."""
        return (
            f"PingCommand("
            f"name='{self.name}', "
            f"trigger='{self.trigger}', "
            f"enabled={self.config.enabled}, "
            f"cooldown={self.config.cooldown}, "
            f"client_ready={self.client.is_ready() if self.client else False})"
        )
