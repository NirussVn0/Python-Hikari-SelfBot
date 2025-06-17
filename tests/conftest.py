
import asyncio
import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from typing import Dict, Any

import discord

from src.discord_selfbot.config.settings import Settings
from src.discord_selfbot.core.types import CommandConfig, CommandExecutionResult
from src.discord_selfbot.services.command_registry import CommandRegistry
from src.discord_selfbot.services.bot_stats import BotStatsService
from src.discord_selfbot.services.discord_service import DiscordService


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings with safe defaults."""
    return Settings(
        discord_token="test_token_" + "x" * 50,
        environment="testing",
        debug=True,
        log_level="DEBUG",
        max_concurrent_commands=5,
        command_timeout=10.0,
        global_rate_limit=100,
        user_rate_limit=20,
        reconnect_attempts=3,
        heartbeat_timeout=30.0,
        enable_metrics=True,
        enable_stats=True,
        enable_rich_logging=False,  # Disable for tests
    )


@pytest.fixture
def mock_discord_client():
    """Create a mock Discord client for testing."""
    client = Mock(spec=discord.Client)
    client.user = Mock()
    client.user.id = 123456789
    client.user.name = "TestBot"
    client.user.discriminator = "0001"
    
    # Mock WebSocket
    client.ws = Mock()
    client.ws.latency = 0.05  # 50ms
    
    # Mock methods
    client.is_ready.return_value = True
    client.is_closed.return_value = False
    client.login = AsyncMock()
    client.connect = AsyncMock()
    client.close = AsyncMock()
    
    return client


@pytest.fixture
def mock_discord_message():
    """Create a mock Discord message for testing."""
    message = Mock(spec=discord.Message)
    message.id = 987654321
    message.content = ".test"
    message.author = Mock()
    message.author.id = 123456789
    message.author.name = "TestUser"
    message.author.discriminator = "0001"
    message.channel = Mock()
    message.channel.id = 555666777
    message.guild = Mock()
    message.guild.id = 888999000
    message.edit = AsyncMock()
    
    return message


@pytest.fixture
async def command_registry():
    """Create a command registry for testing."""
    return CommandRegistry()


@pytest.fixture
async def bot_stats_service(mock_discord_client):
    """Create a bot stats service for testing."""
    return BotStatsService(mock_discord_client)


@pytest.fixture
async def discord_service(test_settings, command_registry, bot_stats_service):
    """Create a Discord service for testing."""
    service = DiscordService(
        settings=test_settings,
        command_registry=command_registry,
        bot_stats=bot_stats_service
    )
    # Replace the client with our mock
    service.client = mock_discord_client
    return service


@pytest.fixture
def sample_command_config():
    """Create a sample command configuration."""
    return CommandConfig(
        enabled=True,
        cooldown=1000,
        permissions=[],
        aliases=["test_alias"]
    )


@pytest.fixture
def sample_command_result():
    """Create a sample command execution result."""
    return CommandExecutionResult(
        success=True,
        response="Test response",
        latency=50.0,
        response_time=100.0,
        metadata={"test": "data"}
    )


@pytest.fixture
def mock_command():
    """Create a mock command for testing."""
    command = Mock()
    command.name = "test"
    command.description = "Test command"
    command.trigger = ".test"
    command.execute = AsyncMock(return_value=CommandExecutionResult(
        success=True,
        response="Test executed",
        response_time=50.0
    ))
    command.get_config.return_value = CommandConfig(enabled=True)
    return command


@pytest.fixture
def test_token_valid():
    """Valid test token format."""
    return "mfa.test_token_" + "x" * 70


@pytest.fixture
def test_token_invalid():
    """Invalid test token format."""
    return "invalid_token"


@pytest.fixture
def mock_aiohttp_session():
    """Create a mock aiohttp session for testing."""
    session = AsyncMock()
    response = AsyncMock()
    response.status = 200
    response.json = AsyncMock(return_value={
        "id": "123456789",
        "username": "TestUser",
        "discriminator": "0001",
        "verified": True,
        "mfa_enabled": True
    })
    session.get.return_value.__aenter__.return_value = response
    return session


class MockCommand:
    """Mock command class for testing."""
    
    def __init__(self, name: str, trigger: str, enabled: bool = True):
        self.name = name
        self.trigger = trigger
        self.description = f"Test command {name}"
        self._config = CommandConfig(enabled=enabled)
        self.execute_count = 0
    
    async def execute(self, message) -> CommandExecutionResult:
        """Mock execute method."""
        self.execute_count += 1
        return CommandExecutionResult(
            success=True,
            response=f"Executed {self.name}",
            response_time=50.0,
            metadata={"execute_count": self.execute_count}
        )
    
    def get_config(self) -> CommandConfig:
        """Get command configuration."""
        return self._config


@pytest.fixture
def mock_commands():
    """Create a list of mock commands for testing."""
    return [
        MockCommand("ping", ".ping"),
        MockCommand("help", ".help"),
        MockCommand("test", ".test", enabled=False),
    ]


# Async fixtures
@pytest_asyncio.fixture
async def async_command_registry():
    """Create an async command registry fixture."""
    registry = CommandRegistry()
    yield registry
    await registry.clear()


@pytest_asyncio.fixture
async def populated_command_registry(async_command_registry, mock_commands):
    """Create a command registry populated with test commands."""
    for command in mock_commands:
        await async_command_registry.register(command)
    return async_command_registry


# Test data fixtures
@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "id": "123456789",
        "username": "TestUser",
        "discriminator": "0001",
        "avatar": "test_avatar_hash",
        "verified": True,
        "mfa_enabled": True,
        "email": "test@example.com",
        "phone": "+1234567890"
    }


@pytest.fixture
def test_metrics_data():
    """Sample metrics data for testing."""
    return {
        "command_name": "test",
        "execution_count": 10,
        "total_execution_time": 500.0,
        "average_execution_time": 50.0,
        "min_execution_time": 25.0,
        "max_execution_time": 100.0,
        "success_count": 9,
        "error_count": 1
    }


# Utility functions for tests
def assert_command_result(result: CommandExecutionResult, success: bool = True):
    """Assert command result properties."""
    assert result.success == success
    assert result.response_time is not None
    assert result.response_time >= 0
    if success:
        assert result.response is not None
        assert result.error is None
    else:
        assert result.error is not None


def create_test_message(content: str = ".test", user_id: int = 123456789):
    """Create a test Discord message."""
    message = Mock(spec=discord.Message)
    message.content = content
    message.author = Mock()
    message.author.id = user_id
    message.edit = AsyncMock()
    return message


# Markers for different test types
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.slow = pytest.mark.slow
