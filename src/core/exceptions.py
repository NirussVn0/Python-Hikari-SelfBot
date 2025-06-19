from typing import Any, Dict, Optional


class DiscordSelfBotError(Exception):
    def __init__(
        self, message: str, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}

    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message='{self.message}', error_code='{self.error_code}', context={self.context})"


class CommandError(DiscordSelfBotError):
    def __init__(
        self,
        message: str,
        command_name: Optional[str] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, error_code, context)
        self.command_name = command_name
        if command_name:
            self.context["command_name"] = command_name


class ConfigurationError(DiscordSelfBotError):
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, error_code, context)
        self.config_key = config_key
        if config_key:
            self.context["config_key"] = config_key


class ValidationError(DiscordSelfBotError):
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, error_code, context)
        self.field_name = field_name
        self.field_value = field_value

        if field_name:
            self.context["field_name"] = field_name

        if field_name and "token" in field_name.lower() and field_value:
            self.context["field_value"] = self._mask_sensitive_value(str(field_value))
        elif field_value is not None:
            self.context["field_value"] = field_value

    @staticmethod
    def _mask_sensitive_value(value: str) -> str:
        if len(value) <= 10:
            return "*" * len(value)
        return f"{value[:3]}...{value[-3:]}"


class ConnectionError(DiscordSelfBotError):
    def __init__(
        self,
        message: str,
        connection_type: Optional[str] = None,
        retry_count: Optional[int] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, error_code, context)
        self.connection_type = connection_type
        self.retry_count = retry_count

        if connection_type:
            self.context["connection_type"] = connection_type
        if retry_count is not None:
            self.context["retry_count"] = retry_count


class RateLimitError(DiscordSelfBotError):
    def __init__(
        self,
        message: str,
        retry_after: Optional[float] = None,
        limit_type: Optional[str] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, error_code, context)
        self.retry_after = retry_after
        self.limit_type = limit_type

        if retry_after is not None:
            self.context["retry_after"] = retry_after
        if limit_type:
            self.context["limit_type"] = limit_type


class PermissionError(DiscordSelfBotError):
    def __init__(
        self,
        message: str,
        required_permission: Optional[str] = None,
        user_id: Optional[str] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, error_code, context)
        self.required_permission = required_permission
        self.user_id = user_id

        if required_permission:
            self.context["required_permission"] = required_permission
        if user_id:
            self.context["user_id"] = user_id
