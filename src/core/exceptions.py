"""
Custom exception hierarchy for the Discord self-bot.

This module defines a comprehensive exception hierarchy that provides
clear error handling and debugging capabilities throughout the application.
All exceptions inherit from a base exception class for consistent handling.
"""

from typing import Any, Dict, Optional


class DiscordSelfBotError(Exception):
    """
    Base exception class for all Discord self-bot related errors.
    
    This is the root exception class that all other custom exceptions
    inherit from. It provides common functionality for error handling
    and debugging.
    
    Attributes:
        message: Human-readable error message
        error_code: Optional error code for programmatic handling
        context: Additional context information about the error
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the base exception.
        
        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
            context: Additional context information about the error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
    
    def __str__(self) -> str:
        """Return a string representation of the error."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message
    
    def __repr__(self) -> str:
        """Return a detailed representation of the error."""
        return (
            f"{self.__class__.__name__}("
            f"message='{self.message}', "
            f"error_code='{self.error_code}', "
            f"context={self.context})"
        )


class CommandError(DiscordSelfBotError):
    """
    Exception raised when command execution fails.
    
    This exception is raised when a command encounters an error during
    execution, such as invalid parameters, permission issues, or
    internal command logic failures.
    """
    
    def __init__(
        self,
        message: str,
        command_name: Optional[str] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the command error.
        
        Args:
            message: Human-readable error message
            command_name: Name of the command that failed
            error_code: Optional error code for programmatic handling
            context: Additional context information about the error
        """
        super().__init__(message, error_code, context)
        self.command_name = command_name
        if command_name:
            self.context["command_name"] = command_name


class ConfigurationError(DiscordSelfBotError):
    """
    Exception raised when configuration is invalid or missing.
    
    This exception is raised when there are issues with the bot's
    configuration, such as missing environment variables, invalid
    settings, or configuration validation failures.
    """
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the configuration error.
        
        Args:
            message: Human-readable error message
            config_key: Configuration key that caused the error
            error_code: Optional error code for programmatic handling
            context: Additional context information about the error
        """
        super().__init__(message, error_code, context)
        self.config_key = config_key
        if config_key:
            self.context["config_key"] = config_key


class ValidationError(DiscordSelfBotError):
    """
    Exception raised when data validation fails.
    
    This exception is raised when input data fails validation,
    such as invalid token formats, malformed messages, or
    data that doesn't meet expected criteria.
    """
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the validation error.
        
        Args:
            message: Human-readable error message
            field_name: Name of the field that failed validation
            field_value: Value that failed validation (will be masked if sensitive)
            error_code: Optional error code for programmatic handling
            context: Additional context information about the error
        """
        super().__init__(message, error_code, context)
        self.field_name = field_name
        self.field_value = field_value
        
        if field_name:
            self.context["field_name"] = field_name
        
        # Mask sensitive values
        if field_name and "token" in field_name.lower() and field_value:
            self.context["field_value"] = self._mask_sensitive_value(str(field_value))
        elif field_value is not None:
            self.context["field_value"] = field_value
    
    @staticmethod
    def _mask_sensitive_value(value: str) -> str:
        """
        Mask sensitive values for logging.
        
        Args:
            value: The value to mask
            
        Returns:
            Masked value showing only first and last few characters
        """
        if len(value) <= 10:
            return "*" * len(value)
        return f"{value[:3]}...{value[-3:]}"


class ConnectionError(DiscordSelfBotError):
    """
    Exception raised when Discord connection fails.
    
    This exception is raised when there are issues connecting to
    Discord, such as network problems, authentication failures,
    or Discord API issues.
    """
    
    def __init__(
        self,
        message: str,
        connection_type: Optional[str] = None,
        retry_count: Optional[int] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the connection error.
        
        Args:
            message: Human-readable error message
            connection_type: Type of connection that failed
            retry_count: Number of retry attempts made
            error_code: Optional error code for programmatic handling
            context: Additional context information about the error
        """
        super().__init__(message, error_code, context)
        self.connection_type = connection_type
        self.retry_count = retry_count
        
        if connection_type:
            self.context["connection_type"] = connection_type
        if retry_count is not None:
            self.context["retry_count"] = retry_count


class RateLimitError(DiscordSelfBotError):
    """
    Exception raised when rate limits are exceeded.
    
    This exception is raised when the bot hits Discord's rate limits
    or internal rate limiting mechanisms.
    """
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[float] = None,
        limit_type: Optional[str] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the rate limit error.
        
        Args:
            message: Human-readable error message
            retry_after: Time to wait before retrying (in seconds)
            limit_type: Type of rate limit that was hit
            error_code: Optional error code for programmatic handling
            context: Additional context information about the error
        """
        super().__init__(message, error_code, context)
        self.retry_after = retry_after
        self.limit_type = limit_type
        
        if retry_after is not None:
            self.context["retry_after"] = retry_after
        if limit_type:
            self.context["limit_type"] = limit_type


class PermissionError(DiscordSelfBotError):
    """
    Exception raised when permission checks fail.
    
    This exception is raised when a user or bot lacks the necessary
    permissions to perform an action.
    """
    
    def __init__(
        self,
        message: str,
        required_permission: Optional[str] = None,
        user_id: Optional[str] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the permission error.
        
        Args:
            message: Human-readable error message
            required_permission: Permission that was required
            user_id: ID of the user who lacked permission
            error_code: Optional error code for programmatic handling
            context: Additional context information about the error
        """
        super().__init__(message, error_code, context)
        self.required_permission = required_permission
        self.user_id = user_id
        
        if required_permission:
            self.context["required_permission"] = required_permission
        if user_id:
            self.context["user_id"] = user_id
