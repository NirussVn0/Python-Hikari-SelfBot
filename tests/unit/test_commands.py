"""
Unit tests for command implementations.

This module contains comprehensive unit tests for all command classes,
including the PingCommand and HelpCommand implementations.
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch
import discord

from src.discord_selfbot.commands.ping_command import PingCommand
from src.discord_selfbot.commands.help_command import HelpCommand
from src.discord_selfbot.core.types import CommandConfig, CommandExecutionResult
from src.discord_selfbot.core.exceptions import CommandError
from tests.conftest import assert_command_result, create_test_message


class TestPingCommand:
    """Test cases for PingCommand."""
    
    @pytest.fixture
    def ping_command(self, mock_discord_client):
        """Create a PingCommand instance for testing."""
        return PingCommand(mock_discord_client)
    
    def test_ping_command_properties(self, ping_command):
        """Test PingCommand basic properties."""
        assert ping_command.name == "ping"
        assert ping_command.description == "Responds with pong and WebSocket latency information"
        assert ping_command.trigger == ".ping"
        assert ping_command.config.enabled is True
        assert ping_command.config.cooldown == 1000
    
    @pytest_asyncio.fixture
    async def test_ping_command_execute_success(self, ping_command):
        """Test successful ping command execution."""
        message = create_test_message(".ping")
        
        result = await ping_command.execute(message)
        
        assert_command_result(result, success=True)
        assert result.latency == 50.0  # From mock client
        assert "pong" in result.response
        assert "50ms" in result.response or "50.0ms" in result.response
        assert result.metadata["ws_latency"] == 50.0
        assert result.metadata["connection_quality"] in ["excellent", "good", "fair", "poor"]
        
        # Verify message was edited
        message.edit.assert_called_once()
    
    @pytest_asyncio.fixture
    async def test_ping_command_websocket_error(self, ping_command):
        """Test ping command with WebSocket error."""
        # Remove WebSocket from client
        ping_command.client.ws = None
        message = create_test_message(".ping")
        
        with pytest.raises(CommandError) as exc_info:
            await ping_command.execute_command(message)
        
        assert exc_info.value.error_code == "NO_WEBSOCKET"
        assert "WebSocket connection not available" in str(exc_info.value)
    
    def test_ping_command_assess_connection_quality(self, ping_command):
        """Test connection quality assessment."""
        assert ping_command._assess_connection_quality(25.0) == "excellent"
        assert ping_command._assess_connection_quality(75.0) == "good"
        assert ping_command._assess_connection_quality(150.0) == "fair"
        assert ping_command._assess_connection_quality(250.0) == "poor"
    
    def test_ping_command_get_quality_emoji(self, ping_command):
        """Test quality emoji selection."""
        assert ping_command._get_quality_emoji("excellent") == "🟢"
        assert ping_command._get_quality_emoji("good") == "🟡"
        assert ping_command._get_quality_emoji("fair") == "🟠"
        assert ping_command._get_quality_emoji("poor") == "🔴"
        assert ping_command._get_quality_emoji("unknown") == "⚪"
    
    def test_ping_command_format_response(self, ping_command):
        """Test response formatting."""
        response = ping_command._format_response(45.5)
        assert "🟢" in response  # Excellent quality
        assert "pong" in response
        assert "45.5ms" in response
        
        response = ping_command._format_response(250.0)
        assert "🔴" in response  # Poor quality
        assert "pong" in response
        assert "250ms" in response
        assert "(slow connection)" in response
    
    def test_ping_command_get_latency_stats(self, ping_command):
        """Test latency statistics retrieval."""
        stats = ping_command.get_latency_stats()
        
        assert stats is not None
        assert stats["latency_ms"] == 50.0
        assert stats["quality"] == "excellent"
        assert stats["client_ready"] is True
        assert stats["websocket_available"] is True
    
    def test_ping_command_get_latency_stats_no_websocket(self, ping_command):
        """Test latency statistics with no WebSocket."""
        ping_command.client.ws = None
        stats = ping_command.get_latency_stats()
        
        assert stats is not None
        assert stats["latency_ms"] is None
        assert stats["quality"] == "unknown"
        assert stats["websocket_available"] is False


class TestHelpCommand:
    """Test cases for HelpCommand."""
    
    @pytest.fixture
    def help_command(self, command_registry):
        """Create a HelpCommand instance for testing."""
        return HelpCommand(command_registry)
    
    def test_help_command_properties(self, help_command):
        """Test HelpCommand basic properties."""
        assert help_command.name == "help"
        assert "Shows available commands" in help_command.description
        assert help_command.trigger == ".help"
        assert help_command.config.enabled is True
        assert help_command.config.cooldown == 2000
    
    @pytest_asyncio.fixture
    async def test_help_command_execute_no_commands(self, help_command):
        """Test help command with no registered commands."""
        message = create_test_message(".help")
        
        result = await help_command.execute(message)
        
        assert_command_result(result, success=True)
        assert "No commands available" in result.response
        message.edit.assert_called_once()
    
    @pytest_asyncio.fixture
    async def test_help_command_execute_with_commands(self, help_command, mock_commands):
        """Test help command with registered commands."""
        # Register mock commands
        for command in mock_commands:
            await help_command.command_registry.register(command)
        
        message = create_test_message(".help")
        result = await help_command.execute(message)
        
        assert_command_result(result, success=True)
        assert "Discord Self-Bot Commands" in result.response
        assert "Statistics" in result.response
        assert ".ping" in result.response
        assert ".help" in result.response
        assert result.metadata["total_commands"] == 3
        message.edit.assert_called_once()
    
    @pytest_asyncio.fixture
    async def test_help_command_detailed_help(self, help_command, mock_commands):
        """Test detailed help for specific command."""
        # Register mock commands
        for command in mock_commands:
            await help_command.command_registry.register(command)
        
        message = create_test_message(".help ping")
        result = await help_command.execute(message)
        
        assert_command_result(result, success=True)
        assert "Help for `.ping`" in result.response
        assert "Name: ping" in result.response
        assert "Configuration" in result.response
        assert result.metadata["specific_command"] == "ping"
        message.edit.assert_called_once()
    
    @pytest_asyncio.fixture
    async def test_help_command_detailed_help_not_found(self, help_command):
        """Test detailed help for non-existent command."""
        message = create_test_message(".help nonexistent")
        result = await help_command.execute(message)
        
        assert_command_result(result, success=True)
        assert "Command not found" in result.response
        assert "nonexistent" in result.response
        message.edit.assert_called_once()
    
    def test_help_command_parse_arguments(self, help_command):
        """Test argument parsing."""
        args = help_command._parse_arguments(".help ping")
        assert args == ["ping"]
        
        args = help_command._parse_arguments(".help")
        assert args == []
        
        args = help_command._parse_arguments(".help ping test")
        assert args == ["ping", "test"]
    
    def test_help_command_categorize_single_command(self, help_command):
        """Test command categorization."""
        ping_command = Mock()
        ping_command.name = "ping"
        assert help_command._categorize_single_command(ping_command) == "Utility"
        
        fun_command = Mock()
        fun_command.name = "joke"
        assert help_command._categorize_single_command(fun_command) == "Fun"
        
        other_command = Mock()
        other_command.name = "custom"
        assert help_command._categorize_single_command(other_command) == "Other"
    
    def test_help_command_get_category_emoji(self, help_command):
        """Test category emoji selection."""
        assert help_command._get_category_emoji("Utility") == "🔧"
        assert help_command._get_category_emoji("Fun") == "🎉"
        assert help_command._get_category_emoji("Information") == "ℹ️"
        assert help_command._get_category_emoji("Moderation") == "🛡️"
        assert help_command._get_category_emoji("Other") == "📦"
        assert help_command._get_category_emoji("Unknown") == "📦"
    
    def test_help_command_get_status_emoji(self, help_command):
        """Test status emoji selection."""
        enabled_command = Mock()
        enabled_command.get_config.return_value = CommandConfig(enabled=True)
        assert help_command._get_status_emoji(enabled_command) == "✅"
        
        disabled_command = Mock()
        disabled_command.get_config.return_value = CommandConfig(enabled=False)
        assert help_command._get_status_emoji(disabled_command) == "❌"
    
    @pytest_asyncio.fixture
    async def test_help_command_find_command(self, help_command, mock_commands):
        """Test command finding by name or trigger."""
        # Register mock commands
        for command in mock_commands:
            await help_command.command_registry.register(command)
        
        # Find by trigger
        command = await help_command._find_command(".ping")
        assert command is not None
        assert command.name == "ping"
        
        # Find by name
        command = await help_command._find_command("ping")
        assert command is not None
        assert command.name == "ping"
        
        # Find non-existent
        command = await help_command._find_command("nonexistent")
        assert command is None
    
    @pytest_asyncio.fixture
    async def test_help_command_categorize_commands(self, help_command, mock_commands):
        """Test command categorization."""
        categorized = await help_command._categorize_commands(mock_commands)
        
        assert "Utility" in categorized
        assert len(categorized["Utility"]) == 2  # ping and help
        assert any(cmd.name == "ping" for cmd in categorized["Utility"])
        assert any(cmd.name == "help" for cmd in categorized["Utility"])
        
        # Test command should be in Other category
        assert "Other" in categorized
        assert any(cmd.name == "test" for cmd in categorized["Other"])


# Integration tests for command interactions
class TestCommandIntegration:
    """Integration tests for command interactions."""
    
    @pytest_asyncio.fixture
    async def test_commands_with_registry(self, mock_discord_client, command_registry):
        """Test commands working with registry."""
        # Create commands
        ping_command = PingCommand(mock_discord_client)
        help_command = HelpCommand(command_registry)
        
        # Register commands
        await command_registry.register(ping_command)
        await command_registry.register(help_command)
        
        # Test ping command
        ping_message = create_test_message(".ping")
        ping_result = await ping_command.execute(ping_message)
        assert_command_result(ping_result, success=True)
        
        # Test help command
        help_message = create_test_message(".help")
        help_result = await help_command.execute(help_message)
        assert_command_result(help_result, success=True)
        assert ".ping" in help_result.response
        
        # Test detailed help for ping
        detailed_help_message = create_test_message(".help ping")
        detailed_result = await help_command.execute(detailed_help_message)
        assert_command_result(detailed_result, success=True)
        assert "Help for `.ping`" in detailed_result.response
