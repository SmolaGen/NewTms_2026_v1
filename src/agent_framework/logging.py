"""
Structured logging system for the extensible AI agent framework.

This module provides a comprehensive logging system with configurable levels,
multiple output formats (JSON and text), and filtering capabilities for
debugging and monitoring agent behavior.
"""

import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from io import StringIO


class LogLevel(Enum):
    """Log level enumeration for structured logging."""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class LogFormat(Enum):
    """Output format enumeration for log messages."""
    TEXT = "text"
    JSON = "json"


class AgentLogger:
    """
    Structured logger for AI agents with configurable levels and formats.

    This logger provides a centralized logging system that supports multiple
    log levels, output formats (text and JSON), and filtering by component
    or log level. It's designed specifically for debugging and monitoring
    agent behavior, tool execution, and context operations.

    Attributes:
        name: Name of the logger instance (typically the agent or component name).
        level: Minimum log level to output (messages below this are filtered).
        format: Output format (TEXT or JSON).
        output: Optional output stream (defaults to internal buffer).
    """

    def __init__(
        self,
        name: str,
        level: Union[LogLevel, str] = LogLevel.INFO,
        format: Union[LogFormat, str] = LogFormat.TEXT,
        output: Optional[Any] = None
    ):
        """
        Initialize the logger with configuration.

        Args:
            name: Name for this logger instance.
            level: Minimum log level to output (LogLevel enum or string like "INFO").
            format: Output format (LogFormat enum or string like "json").
            output: Optional output stream (file-like object). If None, uses internal buffer.

        Raises:
            ValueError: If level or format string is invalid.
        """
        self.name = name
        self._level = self._parse_level(level)
        self._format = self._parse_format(format)
        self._output = output
        self._buffer = StringIO() if output is None else None
        self._log_count = 0
        self._filters: Dict[str, Any] = {}

    def _parse_level(self, level: Union[LogLevel, str]) -> LogLevel:
        """
        Parse log level from string or enum.

        Args:
            level: LogLevel enum or string representation.

        Returns:
            LogLevel enum value.

        Raises:
            ValueError: If string doesn't match a valid log level.
        """
        if isinstance(level, LogLevel):
            return level

        if isinstance(level, str):
            level_upper = level.upper()
            for log_level in LogLevel:
                if log_level.name == level_upper:
                    return log_level
            raise ValueError(
                f"Invalid log level: '{level}'. "
                f"Valid levels are: {', '.join(l.name for l in LogLevel)}"
            )

        raise ValueError(f"Level must be LogLevel or string, got {type(level).__name__}")

    def _parse_format(self, format: Union[LogFormat, str]) -> LogFormat:
        """
        Parse log format from string or enum.

        Args:
            format: LogFormat enum or string representation.

        Returns:
            LogFormat enum value.

        Raises:
            ValueError: If string doesn't match a valid format.
        """
        if isinstance(format, LogFormat):
            return format

        if isinstance(format, str):
            format_lower = format.lower()
            for log_format in LogFormat:
                if log_format.value == format_lower:
                    return log_format
            raise ValueError(
                f"Invalid log format: '{format}'. "
                f"Valid formats are: {', '.join(f.value for f in LogFormat)}"
            )

        raise ValueError(f"Format must be LogFormat or string, got {type(format).__name__}")

    def set_level(self, level: Union[LogLevel, str]) -> None:
        """
        Set the minimum log level.

        Args:
            level: New log level (LogLevel enum or string).

        Raises:
            ValueError: If level is invalid.
        """
        self._level = self._parse_level(level)

    def set_format(self, format: Union[LogFormat, str]) -> None:
        """
        Set the output format.

        Args:
            format: New format (LogFormat enum or string).

        Raises:
            ValueError: If format is invalid.
        """
        self._format = self._parse_format(format)

    def add_filter(self, key: str, value: Any) -> None:
        """
        Add a filter to only log messages matching certain criteria.

        Filters are applied as key-value pairs in the extra context.
        Only messages with matching extra context will be logged.

        Args:
            key: The context key to filter on.
            value: The value that must match.
        """
        self._filters[key] = value

    def remove_filter(self, key: str) -> None:
        """
        Remove a filter.

        Args:
            key: The filter key to remove.

        Raises:
            KeyError: If the filter key doesn't exist.
        """
        if key not in self._filters:
            raise KeyError(f"Filter '{key}' not found")
        del self._filters[key]

    def clear_filters(self) -> None:
        """Remove all filters."""
        self._filters.clear()

    def _should_log(self, level: LogLevel, extra: Optional[Dict[str, Any]]) -> bool:
        """
        Check if a message should be logged based on level and filters.

        Args:
            level: Log level of the message.
            extra: Extra context dictionary.

        Returns:
            True if the message should be logged, False otherwise.
        """
        # Check log level
        if level.value < self._level.value:
            return False

        # Check filters
        if self._filters and extra:
            for key, value in self._filters.items():
                if key not in extra or extra[key] != value:
                    return False
        elif self._filters and not extra:
            # Filters are set but no extra context provided
            return False

        return True

    def _format_message(
        self,
        level: LogLevel,
        message: str,
        extra: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format a log message according to the configured format.

        Args:
            level: Log level.
            message: Log message.
            extra: Optional extra context.

        Returns:
            Formatted log message string.
        """
        timestamp = datetime.utcnow().isoformat() + 'Z'

        if self._format == LogFormat.JSON:
            log_entry = {
                "timestamp": timestamp,
                "logger": self.name,
                "level": level.name,
                "message": message
            }
            if extra:
                log_entry["extra"] = extra
            return json.dumps(log_entry)
        else:
            # TEXT format
            extra_str = ""
            if extra:
                extra_items = [f"{k}={v}" for k, v in extra.items()]
                extra_str = f" [{', '.join(extra_items)}]"
            return f"{timestamp} [{level.name}] {self.name}: {message}{extra_str}"

    def _write(self, formatted_message: str) -> None:
        """
        Write formatted message to output.

        Args:
            formatted_message: The formatted log message.
        """
        if self._output:
            self._output.write(formatted_message + '\n')
            # Flush if the output stream supports it
            if hasattr(self._output, 'flush'):
                self._output.flush()
        else:
            self._buffer.write(formatted_message + '\n')

        self._log_count += 1

    def log(
        self,
        level: Union[LogLevel, str],
        message: str,
        **extra
    ) -> None:
        """
        Log a message at the specified level with optional extra context.

        Args:
            level: Log level (LogLevel enum or string).
            message: The log message.
            **extra: Additional context as keyword arguments.

        Raises:
            ValueError: If level is invalid.
        """
        log_level = self._parse_level(level)

        extra_dict = extra if extra else None

        if not self._should_log(log_level, extra_dict):
            return

        formatted = self._format_message(log_level, message, extra_dict)
        self._write(formatted)

    def debug(self, message: str, **extra) -> None:
        """
        Log a DEBUG level message.

        Args:
            message: The log message.
            **extra: Additional context as keyword arguments.
        """
        self.log(LogLevel.DEBUG, message, **extra)

    def info(self, message: str, **extra) -> None:
        """
        Log an INFO level message.

        Args:
            message: The log message.
            **extra: Additional context as keyword arguments.
        """
        self.log(LogLevel.INFO, message, **extra)

    def warning(self, message: str, **extra) -> None:
        """
        Log a WARNING level message.

        Args:
            message: The log message.
            **extra: Additional context as keyword arguments.
        """
        self.log(LogLevel.WARNING, message, **extra)

    def error(self, message: str, **extra) -> None:
        """
        Log an ERROR level message.

        Args:
            message: The log message.
            **extra: Additional context as keyword arguments.
        """
        self.log(LogLevel.ERROR, message, **extra)

    def critical(self, message: str, **extra) -> None:
        """
        Log a CRITICAL level message.

        Args:
            message: The log message.
            **extra: Additional context as keyword arguments.
        """
        self.log(LogLevel.CRITICAL, message, **extra)

    def get_logs(self) -> str:
        """
        Get all logs from the internal buffer.

        This only works if the logger was initialized without a custom output stream.

        Returns:
            All logged messages as a string.

        Raises:
            RuntimeError: If logger was initialized with a custom output stream.
        """
        if self._buffer is None:
            raise RuntimeError(
                "Cannot get logs when using custom output stream. "
                "Initialize logger without 'output' parameter to use internal buffer."
            )
        return self._buffer.getvalue()

    def clear_logs(self) -> None:
        """
        Clear the internal log buffer.

        This only works if the logger was initialized without a custom output stream.

        Raises:
            RuntimeError: If logger was initialized with a custom output stream.
        """
        if self._buffer is None:
            raise RuntimeError(
                "Cannot clear logs when using custom output stream. "
                "Initialize logger without 'output' parameter to use internal buffer."
            )
        self._buffer = StringIO()
        self._log_count = 0

    def get_log_count(self) -> int:
        """
        Get the total number of messages logged.

        Returns:
            The count of logged messages.
        """
        return self._log_count

    def __repr__(self) -> str:
        """Return a string representation of the logger."""
        return (
            f"AgentLogger(name='{self.name}', level={self._level.name}, "
            f"format={self._format.value})"
        )

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"AgentLogger '{self.name}' [{self._level.name}] ({self._log_count} messages)"
