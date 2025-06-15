"""
Type definitions and data classes for the Discord self-bot.

This module contains all the core type definitions, data classes, and enums
used throughout the application. It provides type safety and clear contracts
for data structures.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ConnectionStatus(Enum):
    """Discord client connection status enumeration."""
    
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


@dataclass
class CommandExecutionResult:
    """
    Result of command execution containing success status and metadata.
    
    This dataclass encapsulates the result of executing a Discord command,
    including success status, response message, error information, and
    performance metrics.
    
    Attributes:
        success: Whether the command executed successfully
        response: The response message sent to Discord (optional)
        error: Error message if execution failed (optional)
        latency: WebSocket latency in milliseconds (optional)
        response_time: Time taken to process the command in milliseconds (optional)
        metadata: Additional metadata about the execution (optional)
    """
    
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    latency: Optional[float] = None
    response_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate the result after initialization."""
        if self.metadata is None:
            self.metadata = {}


@dataclass
class CommandConfig:
    """
    Configuration options for Discord commands.
    
    This dataclass defines the configuration parameters that can be set
    for individual commands, including enablement, cooldowns, permissions,
    and aliases.
    
    Attributes:
        enabled: Whether the command is enabled
        cooldown: Cooldown period in milliseconds (optional)
        permissions: Required permissions for future use (optional)
        aliases: Command aliases (optional)
    """
    
    enabled: bool = True
    cooldown: Optional[int] = None
    permissions: List[str] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Validate the configuration after initialization."""
        if self.permissions is None:
            self.permissions = []
        if self.aliases is None:
            self.aliases = []
        if self.cooldown is not None and self.cooldown < 0:
            raise ValueError("Cooldown must be non-negative")


@dataclass
class BotStats:
    """
    Bot statistics and monitoring information.
    
    This dataclass contains comprehensive statistics about the bot's
    operation, including connection status, performance metrics,
    and activity counters.
    
    Attributes:
        status: Current connection status
        ping: Current WebSocket ping in milliseconds
        uptime: Bot uptime in milliseconds
        commands_executed: Number of commands executed
        messages_processed: Number of messages processed
        last_activity: Timestamp of last activity
        start_time: Bot start timestamp
        memory_usage: Current memory usage in MB (optional)
        cpu_usage: Current CPU usage percentage (optional)
    """
    
    status: ConnectionStatus
    ping: float
    uptime: float
    commands_executed: int
    messages_processed: int
    last_activity: datetime
    start_time: datetime
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    
    def __post_init__(self) -> None:
        """Validate the stats after initialization."""
        if self.ping < 0:
            raise ValueError("Ping must be non-negative")
        if self.uptime < 0:
            raise ValueError("Uptime must be non-negative")
        if self.commands_executed < 0:
            raise ValueError("Commands executed must be non-negative")
        if self.messages_processed < 0:
            raise ValueError("Messages processed must be non-negative")


@dataclass
class TokenInfo:
    """
    Discord token information and validation result.
    
    This dataclass contains information about a Discord token,
    including validation status and extracted metadata.
    
    Attributes:
        token: The Discord token (masked for security)
        is_valid: Whether the token is valid
        user_id: Extracted user ID (optional)
        username: Username associated with the token (optional)
        discriminator: User discriminator (optional)
        verified: Whether the account is verified (optional)
        mfa_enabled: Whether MFA is enabled (optional)
        error_message: Error message if validation failed (optional)
    """
    
    token: str
    is_valid: bool
    user_id: Optional[str] = None
    username: Optional[str] = None
    discriminator: Optional[str] = None
    verified: Optional[bool] = None
    mfa_enabled: Optional[bool] = None
    error_message: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Mask the token for security after initialization."""
        if len(self.token) > 10:
            # Mask the token for security, showing only first and last few characters
            self.token = f"{self.token[:6]}...{self.token[-4:]}"


@dataclass
class CommandMetrics:
    """
    Performance metrics for command execution.
    
    This dataclass tracks detailed performance metrics for command
    execution, useful for monitoring and optimization.
    
    Attributes:
        command_name: Name of the command
        execution_count: Number of times executed
        total_execution_time: Total execution time in milliseconds
        average_execution_time: Average execution time in milliseconds
        min_execution_time: Minimum execution time in milliseconds
        max_execution_time: Maximum execution time in milliseconds
        success_count: Number of successful executions
        error_count: Number of failed executions
        last_executed: Timestamp of last execution
    """
    
    command_name: str
    execution_count: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    min_execution_time: float = float('inf')
    max_execution_time: float = 0.0
    success_count: int = 0
    error_count: int = 0
    last_executed: Optional[datetime] = None
    
    def update_metrics(self, execution_time: float, success: bool) -> None:
        """
        Update metrics with new execution data.
        
        Args:
            execution_time: Time taken for the execution in milliseconds
            success: Whether the execution was successful
        """
        self.execution_count += 1
        self.total_execution_time += execution_time
        self.average_execution_time = self.total_execution_time / self.execution_count
        self.min_execution_time = min(self.min_execution_time, execution_time)
        self.max_execution_time = max(self.max_execution_time, execution_time)
        self.last_executed = datetime.now()
        
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
