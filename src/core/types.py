from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ConnectionStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


@dataclass
class CommandExecutionResult:
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    latency: Optional[float] = None
    response_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


@dataclass
class CommandConfig:
    enabled: bool = True
    cooldown: int = 0
    permissions: Optional[List[str]] = None
    aliases: Optional[List[str]] = None

    def __post_init__(self) -> None:
        if self.permissions is None:
            self.permissions = []
        if self.aliases is None:
            self.aliases = []
        if self.cooldown is not None and self.cooldown < 0:
            raise ValueError("Cooldown must be non-negative")


@dataclass
class BotStats:
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
    token: str
    is_valid: bool
    user_id: Optional[str] = None
    username: Optional[str] = None
    discriminator: Optional[str] = None
    verified: Optional[bool] = None
    mfa_enabled: Optional[bool] = None
    error_message: Optional[str] = None

    def __post_init__(self) -> None:
        if len(self.token) > 10:
            self.token = f"{self.token[:6]}...{self.token[-4:]}"


@dataclass
class CommandMetrics:
    command_name: str
    execution_count: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    min_execution_time: float = float("inf")
    max_execution_time: float = 0.0
    success_count: int = 0
    error_count: int = 0
    last_executed: Optional[datetime] = None

    def update_metrics(self, execution_time: float, success: bool) -> None:
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
