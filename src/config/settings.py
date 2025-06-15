"""
Application settings and configuration management.

This module provides comprehensive configuration management using Pydantic
for validation and type safety. It handles environment variables, default
values, and configuration validation.
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings

from core.exceptions import ConfigurationError


class Settings(BaseSettings):
    """
    Application settings with validation and type safety.
    
    This class uses Pydantic to provide type-safe configuration management
    with automatic validation and environment variable loading.
    
    All settings can be overridden via environment variables with the
    DISCORD_SELFBOT_ prefix.
    """
    
    # Discord Configuration
    discord_token: str = Field(
        ...,
        description="Discord user token for authentication",
        min_length=50,
        max_length=100,
    )
    
    # Application Configuration
    environment: str = Field(
        default="development",
        description="Application environment (development, production, testing)",
    )
    
    debug: bool = Field(
        default=False,
        description="Enable debug mode with verbose logging",
    )
    
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    
    # Performance Configuration
    max_concurrent_commands: int = Field(
        default=10,
        description="Maximum number of concurrent command executions",
        ge=1,
        le=100,
    )
    
    command_timeout: float = Field(
        default=30.0,
        description="Command execution timeout in seconds",
        ge=1.0,
        le=300.0,
    )
    
    # Rate Limiting Configuration
    global_rate_limit: int = Field(
        default=50,
        description="Global rate limit (commands per minute)",
        ge=1,
        le=1000,
    )
    
    user_rate_limit: int = Field(
        default=10,
        description="Per-user rate limit (commands per minute)",
        ge=1,
        le=100,
    )
    
    # Discord Client Configuration
    reconnect_attempts: int = Field(
        default=5,
        description="Number of reconnection attempts",
        ge=0,
        le=20,
    )
    
    heartbeat_timeout: float = Field(
        default=60.0,
        description="Heartbeat timeout in seconds",
        ge=10.0,
        le=300.0,
    )
    
    # Security Configuration
    allowed_users: List[str] = Field(
        default_factory=list,
        description="List of allowed user IDs (empty = allow all)",
    )
    
    blocked_users: List[str] = Field(
        default_factory=list,
        description="List of blocked user IDs",
    )
    
    # Feature Flags
    enable_metrics: bool = Field(
        default=True,
        description="Enable performance metrics collection",
    )
    
    enable_stats: bool = Field(
        default=True,
        description="Enable bot statistics tracking",
    )
    
    enable_rich_logging: bool = Field(
        default=True,
        description="Enable rich console output",
    )
    
    # Optional Configuration
    webhook_url: Optional[str] = Field(
        default=None,
        description="Optional webhook URL for notifications",
    )
    
    status_message: Optional[str] = Field(
        default=None,
        description="Custom status message for the bot",
    )
    
    class Config:
        """Pydantic configuration."""
        
        env_prefix = "DISCORD_SELFBOT_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        validate_assignment = True
        extra = "forbid"  # Prevent unknown configuration keys
    
    @validator("discord_token")
    def validate_discord_token(cls, v: str) -> str:
        """
        Validate Discord token format.
        
        Args:
            v: The token value
            
        Returns:
            The validated token
            
        Raises:
            ConfigurationError: If token format is invalid
        """
        if not v:
            raise ConfigurationError(
                "Discord token is required",
                config_key="discord_token",
                error_code="MISSING_TOKEN"
            )
        
        # Basic format validation
        if len(v) < 50:
            raise ConfigurationError(
                "Discord token appears to be too short",
                config_key="discord_token",
                error_code="INVALID_TOKEN_LENGTH"
            )
        
        # Check for common token format patterns
        if not any(char.isdigit() for char in v):
            raise ConfigurationError(
                "Discord token format appears invalid (no digits)",
                config_key="discord_token",
                error_code="INVALID_TOKEN_FORMAT"
            )
        
        return v
    
    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """
        Validate environment setting.
        
        Args:
            v: The environment value
            
        Returns:
            The validated environment
            
        Raises:
            ConfigurationError: If environment is invalid
        """
        valid_environments = {"development", "production", "testing"}
        if v.lower() not in valid_environments:
            raise ConfigurationError(
                f"Invalid environment '{v}'. Must be one of: {valid_environments}",
                config_key="environment",
                error_code="INVALID_ENVIRONMENT"
            )
        return v.lower()
    
    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """
        Validate log level setting.
        
        Args:
            v: The log level value
            
        Returns:
            The validated log level
            
        Raises:
            ConfigurationError: If log level is invalid
        """
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ConfigurationError(
                f"Invalid log level '{v}'. Must be one of: {valid_levels}",
                config_key="log_level",
                error_code="INVALID_LOG_LEVEL"
            )
        return v.upper()
    
    @validator("allowed_users", "blocked_users")
    def validate_user_lists(cls, v: List[str]) -> List[str]:
        """
        Validate user ID lists.
        
        Args:
            v: The user ID list
            
        Returns:
            The validated user ID list
            
        Raises:
            ConfigurationError: If user IDs are invalid
        """
        for user_id in v:
            if not user_id.isdigit():
                raise ConfigurationError(
                    f"Invalid user ID '{user_id}'. Must be numeric.",
                    config_key="user_lists",
                    error_code="INVALID_USER_ID"
                )
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == "testing"
    
    def get_effective_log_level(self) -> str:
        """
        Get the effective log level based on environment and debug settings.
        
        Returns:
            The effective log level
        """
        if self.debug or self.is_development:
            return "DEBUG"
        return self.log_level
    
    def validate_configuration(self) -> None:
        """
        Perform additional configuration validation.
        
        This method performs cross-field validation and checks for
        configuration conflicts.
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Check for conflicting user lists
        allowed_set = set(self.allowed_users)
        blocked_set = set(self.blocked_users)
        
        if allowed_set & blocked_set:
            conflicting_users = allowed_set & blocked_set
            raise ConfigurationError(
                f"Users cannot be both allowed and blocked: {conflicting_users}",
                error_code="CONFLICTING_USER_LISTS"
            )
        
        # Validate webhook URL if provided
        if self.webhook_url and not self.webhook_url.startswith(("http://", "https://")):
            raise ConfigurationError(
                "Webhook URL must start with http:// or https://",
                config_key="webhook_url",
                error_code="INVALID_WEBHOOK_URL"
            )


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching.
    
    This function creates and caches the settings instance to ensure
    consistent configuration throughout the application.
    
    Returns:
        Settings: The application settings instance
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    try:
        settings = Settings()
        settings.validate_configuration()
        return settings
    except Exception as e:
        if isinstance(e, ConfigurationError):
            raise
        raise ConfigurationError(
            f"Failed to load configuration: {e}",
            error_code="CONFIG_LOAD_FAILED"
        ) from e
