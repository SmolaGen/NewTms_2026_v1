"""
Tests for the AgentLogger structured logging system.

This module tests the AgentLogger class to ensure proper logging functionality,
including configurable levels, multiple output formats, and filtering capabilities.
"""

import json
import pytest
from io import StringIO

from agent_framework.logging import AgentLogger, LogLevel, LogFormat


class TestLogLevel:
    """Test suite for LogLevel enumeration."""

    def test_log_level_values(self):
        """Test that log levels have correct numeric values."""
        assert LogLevel.DEBUG.value == 10
        assert LogLevel.INFO.value == 20
        assert LogLevel.WARNING.value == 30
        assert LogLevel.ERROR.value == 40
        assert LogLevel.CRITICAL.value == 50

    def test_log_level_ordering(self):
        """Test that log levels are correctly ordered."""
        assert LogLevel.DEBUG.value < LogLevel.INFO.value
        assert LogLevel.INFO.value < LogLevel.WARNING.value
        assert LogLevel.WARNING.value < LogLevel.ERROR.value
        assert LogLevel.ERROR.value < LogLevel.CRITICAL.value


class TestLogFormat:
    """Test suite for LogFormat enumeration."""

    def test_log_format_values(self):
        """Test that log formats have correct string values."""
        assert LogFormat.TEXT.value == "text"
        assert LogFormat.JSON.value == "json"


class TestAgentLoggerInitialization:
    """Test suite for AgentLogger initialization."""

    def test_basic_initialization(self):
        """Test basic logger initialization."""
        logger = AgentLogger(name="test_logger")

        assert logger.name == "test_logger"
        assert logger._level == LogLevel.INFO
        assert logger._format == LogFormat.TEXT
        assert logger._buffer is not None
        assert logger._output is None

    def test_initialization_with_level_enum(self):
        """Test initialization with LogLevel enum."""
        logger = AgentLogger(name="test", level=LogLevel.DEBUG)
        assert logger._level == LogLevel.DEBUG

    def test_initialization_with_level_string(self):
        """Test initialization with level as string."""
        logger = AgentLogger(name="test", level="DEBUG")
        assert logger._level == LogLevel.DEBUG

        logger2 = AgentLogger(name="test", level="error")
        assert logger2._level == LogLevel.ERROR

    def test_initialization_with_format_enum(self):
        """Test initialization with LogFormat enum."""
        logger = AgentLogger(name="test", format=LogFormat.JSON)
        assert logger._format == LogFormat.JSON

    def test_initialization_with_format_string(self):
        """Test initialization with format as string."""
        logger = AgentLogger(name="test", format="json")
        assert logger._format == LogFormat.JSON

        logger2 = AgentLogger(name="test", format="TEXT")
        assert logger2._format == LogFormat.TEXT

    def test_initialization_with_custom_output(self):
        """Test initialization with custom output stream."""
        output = StringIO()
        logger = AgentLogger(name="test", output=output)

        assert logger._output is output
        assert logger._buffer is None

    def test_invalid_level_string(self):
        """Test that invalid level string raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            AgentLogger(name="test", level="INVALID")

        assert "Invalid log level" in str(exc_info.value)

    def test_invalid_level_type(self):
        """Test that invalid level type raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            AgentLogger(name="test", level=123)

        assert "must be LogLevel or string" in str(exc_info.value)

    def test_invalid_format_string(self):
        """Test that invalid format string raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            AgentLogger(name="test", format="invalid")

        assert "Invalid log format" in str(exc_info.value)

    def test_invalid_format_type(self):
        """Test that invalid format type raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            AgentLogger(name="test", format=123)

        assert "must be LogFormat or string" in str(exc_info.value)


class TestAgentLoggerConfiguration:
    """Test suite for logger configuration methods."""

    def test_set_level_with_enum(self):
        """Test setting log level with enum."""
        logger = AgentLogger(name="test", level=LogLevel.INFO)
        logger.set_level(LogLevel.DEBUG)
        assert logger._level == LogLevel.DEBUG

    def test_set_level_with_string(self):
        """Test setting log level with string."""
        logger = AgentLogger(name="test")
        logger.set_level("WARNING")
        assert logger._level == LogLevel.WARNING

    def test_set_level_invalid(self):
        """Test that invalid level raises ValueError."""
        logger = AgentLogger(name="test")
        with pytest.raises(ValueError):
            logger.set_level("INVALID")

    def test_set_format_with_enum(self):
        """Test setting format with enum."""
        logger = AgentLogger(name="test", format=LogFormat.TEXT)
        logger.set_format(LogFormat.JSON)
        assert logger._format == LogFormat.JSON

    def test_set_format_with_string(self):
        """Test setting format with string."""
        logger = AgentLogger(name="test")
        logger.set_format("json")
        assert logger._format == LogFormat.JSON

    def test_set_format_invalid(self):
        """Test that invalid format raises ValueError."""
        logger = AgentLogger(name="test")
        with pytest.raises(ValueError):
            logger.set_format("invalid")


class TestAgentLoggerFiltering:
    """Test suite for log filtering functionality."""

    def test_add_filter(self):
        """Test adding a filter."""
        logger = AgentLogger(name="test")
        logger.add_filter("component", "tool_system")

        assert "component" in logger._filters
        assert logger._filters["component"] == "tool_system"

    def test_remove_filter(self):
        """Test removing a filter."""
        logger = AgentLogger(name="test")
        logger.add_filter("component", "tool_system")
        logger.remove_filter("component")

        assert "component" not in logger._filters

    def test_remove_nonexistent_filter(self):
        """Test that removing nonexistent filter raises KeyError."""
        logger = AgentLogger(name="test")

        with pytest.raises(KeyError) as exc_info:
            logger.remove_filter("nonexistent")

        assert "not found" in str(exc_info.value)

    def test_clear_filters(self):
        """Test clearing all filters."""
        logger = AgentLogger(name="test")
        logger.add_filter("component", "tool_system")
        logger.add_filter("agent", "test_agent")
        logger.clear_filters()

        assert len(logger._filters) == 0

    def test_filter_matching_message(self):
        """Test that messages matching filters are logged."""
        logger = AgentLogger(name="test", level=LogLevel.DEBUG)
        logger.add_filter("component", "tool_system")

        logger.info("Test message", component="tool_system")
        logs = logger.get_logs()

        assert "Test message" in logs

    def test_filter_non_matching_message(self):
        """Test that messages not matching filters are filtered out."""
        logger = AgentLogger(name="test", level=LogLevel.DEBUG)
        logger.add_filter("component", "tool_system")

        logger.info("Test message", component="context_manager")
        logs = logger.get_logs()

        assert "Test message" not in logs

    def test_filter_message_without_extra(self):
        """Test that messages without extra context are filtered when filters are set."""
        logger = AgentLogger(name="test", level=LogLevel.DEBUG)
        logger.add_filter("component", "tool_system")

        logger.info("Test message")
        logs = logger.get_logs()

        assert "Test message" not in logs


class TestAgentLoggerLogging:
    """Test suite for logging functionality."""

    def test_log_method_with_enum(self):
        """Test logging with LogLevel enum."""
        logger = AgentLogger(name="test")
        logger.log(LogLevel.INFO, "Test message")

        logs = logger.get_logs()
        assert "Test message" in logs
        assert "[INFO]" in logs

    def test_log_method_with_string(self):
        """Test logging with level as string."""
        logger = AgentLogger(name="test")
        logger.log("INFO", "Test message")

        logs = logger.get_logs()
        assert "Test message" in logs

    def test_debug_method(self):
        """Test debug logging method."""
        logger = AgentLogger(name="test", level=LogLevel.DEBUG)
        logger.debug("Debug message")

        logs = logger.get_logs()
        assert "Debug message" in logs
        assert "[DEBUG]" in logs

    def test_info_method(self):
        """Test info logging method."""
        logger = AgentLogger(name="test")
        logger.info("Info message")

        logs = logger.get_logs()
        assert "Info message" in logs
        assert "[INFO]" in logs

    def test_warning_method(self):
        """Test warning logging method."""
        logger = AgentLogger(name="test")
        logger.warning("Warning message")

        logs = logger.get_logs()
        assert "Warning message" in logs
        assert "[WARNING]" in logs

    def test_error_method(self):
        """Test error logging method."""
        logger = AgentLogger(name="test")
        logger.error("Error message")

        logs = logger.get_logs()
        assert "Error message" in logs
        assert "[ERROR]" in logs

    def test_critical_method(self):
        """Test critical logging method."""
        logger = AgentLogger(name="test")
        logger.critical("Critical message")

        logs = logger.get_logs()
        assert "Critical message" in logs
        assert "[CRITICAL]" in logs

    def test_log_with_extra_context(self):
        """Test logging with extra context."""
        logger = AgentLogger(name="test")
        logger.info("Test message", component="tool_system", action="execute")

        logs = logger.get_logs()
        assert "Test message" in logs
        assert "component=tool_system" in logs
        assert "action=execute" in logs


class TestAgentLoggerLevelFiltering:
    """Test suite for log level filtering."""

    def test_debug_not_logged_at_info_level(self):
        """Test that DEBUG messages are filtered at INFO level."""
        logger = AgentLogger(name="test", level=LogLevel.INFO)
        logger.debug("Debug message")

        logs = logger.get_logs()
        assert "Debug message" not in logs

    def test_info_logged_at_info_level(self):
        """Test that INFO messages are logged at INFO level."""
        logger = AgentLogger(name="test", level=LogLevel.INFO)
        logger.info("Info message")

        logs = logger.get_logs()
        assert "Info message" in logs

    def test_warning_logged_at_info_level(self):
        """Test that WARNING messages are logged at INFO level."""
        logger = AgentLogger(name="test", level=LogLevel.INFO)
        logger.warning("Warning message")

        logs = logger.get_logs()
        assert "Warning message" in logs

    def test_error_logged_at_warning_level(self):
        """Test that ERROR messages are logged at WARNING level."""
        logger = AgentLogger(name="test", level=LogLevel.WARNING)
        logger.error("Error message")

        logs = logger.get_logs()
        assert "Error message" in logs

    def test_info_not_logged_at_error_level(self):
        """Test that INFO messages are filtered at ERROR level."""
        logger = AgentLogger(name="test", level=LogLevel.ERROR)
        logger.info("Info message")
        logger.warning("Warning message")

        logs = logger.get_logs()
        assert "Info message" not in logs
        assert "Warning message" not in logs


class TestAgentLoggerTextFormat:
    """Test suite for text output format."""

    def test_text_format_structure(self):
        """Test that text format has correct structure."""
        logger = AgentLogger(name="test_logger", format=LogFormat.TEXT)
        logger.info("Test message")

        logs = logger.get_logs()
        assert "test_logger" in logs
        assert "[INFO]" in logs
        assert "Test message" in logs
        # Should contain ISO timestamp with Z suffix
        assert "Z" in logs

    def test_text_format_with_extra(self):
        """Test text format with extra context."""
        logger = AgentLogger(name="test", format=LogFormat.TEXT)
        logger.info("Test", component="test_comp", value=42)

        logs = logger.get_logs()
        assert "component=test_comp" in logs
        assert "value=42" in logs


class TestAgentLoggerJsonFormat:
    """Test suite for JSON output format."""

    def test_json_format_structure(self):
        """Test that JSON format produces valid JSON."""
        logger = AgentLogger(name="test_logger", format=LogFormat.JSON)
        logger.info("Test message")

        logs = logger.get_logs()
        log_entry = json.loads(logs.strip())

        assert log_entry["logger"] == "test_logger"
        assert log_entry["level"] == "INFO"
        assert log_entry["message"] == "Test message"
        assert "timestamp" in log_entry
        assert log_entry["timestamp"].endswith("Z")

    def test_json_format_with_extra(self):
        """Test JSON format with extra context."""
        logger = AgentLogger(name="test", format=LogFormat.JSON)
        logger.info("Test message", component="test_comp", value=42)

        logs = logger.get_logs()
        log_entry = json.loads(logs.strip())

        assert "extra" in log_entry
        assert log_entry["extra"]["component"] == "test_comp"
        assert log_entry["extra"]["value"] == 42

    def test_json_format_without_extra(self):
        """Test JSON format without extra context."""
        logger = AgentLogger(name="test", format=LogFormat.JSON)
        logger.info("Test message")

        logs = logger.get_logs()
        log_entry = json.loads(logs.strip())

        assert "extra" not in log_entry


class TestAgentLoggerOutput:
    """Test suite for output management."""

    def test_custom_output_stream(self):
        """Test logging to custom output stream."""
        output = StringIO()
        logger = AgentLogger(name="test", output=output)
        logger.info("Test message")

        output_value = output.getvalue()
        assert "Test message" in output_value

    def test_get_logs_with_custom_output_raises(self):
        """Test that get_logs raises error with custom output."""
        output = StringIO()
        logger = AgentLogger(name="test", output=output)

        with pytest.raises(RuntimeError) as exc_info:
            logger.get_logs()

        assert "custom output stream" in str(exc_info.value)

    def test_clear_logs_with_custom_output_raises(self):
        """Test that clear_logs raises error with custom output."""
        output = StringIO()
        logger = AgentLogger(name="test", output=output)

        with pytest.raises(RuntimeError) as exc_info:
            logger.clear_logs()

        assert "custom output stream" in str(exc_info.value)

    def test_clear_logs(self):
        """Test clearing logs."""
        logger = AgentLogger(name="test")
        logger.info("Message 1")
        logger.info("Message 2")

        logs = logger.get_logs()
        assert "Message 1" in logs
        assert "Message 2" in logs

        logger.clear_logs()
        logs = logger.get_logs()
        assert logs == ""

    def test_get_log_count(self):
        """Test getting log count."""
        logger = AgentLogger(name="test")

        assert logger.get_log_count() == 0

        logger.info("Message 1")
        assert logger.get_log_count() == 1

        logger.warning("Message 2")
        logger.error("Message 3")
        assert logger.get_log_count() == 3

    def test_log_count_with_filtering(self):
        """Test that log count only includes logged messages."""
        logger = AgentLogger(name="test", level=LogLevel.WARNING)

        logger.debug("Debug")  # Not logged
        logger.info("Info")    # Not logged
        logger.warning("Warning")  # Logged
        logger.error("Error")  # Logged

        assert logger.get_log_count() == 2

    def test_clear_logs_resets_count(self):
        """Test that clearing logs resets the count."""
        logger = AgentLogger(name="test")
        logger.info("Message 1")
        logger.info("Message 2")

        assert logger.get_log_count() == 2

        logger.clear_logs()
        assert logger.get_log_count() == 0


class TestAgentLoggerRepresentation:
    """Test suite for string representations."""

    def test_repr(self):
        """Test __repr__ method."""
        logger = AgentLogger(name="test_logger", level=LogLevel.DEBUG, format=LogFormat.JSON)
        repr_str = repr(logger)

        assert "AgentLogger" in repr_str
        assert "test_logger" in repr_str
        assert "DEBUG" in repr_str
        assert "json" in repr_str

    def test_str(self):
        """Test __str__ method."""
        logger = AgentLogger(name="test_logger")
        logger.info("Message 1")
        logger.info("Message 2")

        str_repr = str(logger)

        assert "test_logger" in str_repr
        assert "INFO" in str_repr
        assert "2 messages" in str_repr


class TestAgentLoggerIntegration:
    """Integration tests for AgentLogger."""

    def test_multiple_loggers_independent(self):
        """Test that multiple loggers are independent."""
        logger1 = AgentLogger(name="logger1")
        logger2 = AgentLogger(name="logger2")

        logger1.info("Message from logger1")
        logger2.warning("Message from logger2")

        logs1 = logger1.get_logs()
        logs2 = logger2.get_logs()

        assert "Message from logger1" in logs1
        assert "Message from logger2" not in logs1

        assert "Message from logger2" in logs2
        assert "Message from logger1" not in logs2

    def test_level_and_filter_combination(self):
        """Test combining level filtering and context filtering."""
        logger = AgentLogger(name="test", level=LogLevel.WARNING)
        logger.add_filter("component", "tool_system")

        # Should not log: wrong level
        logger.info("Info message", component="tool_system")

        # Should not log: wrong component
        logger.warning("Warning 1", component="context")

        # Should log: correct level and component
        logger.warning("Warning 2", component="tool_system")

        # Should log: correct level and component
        logger.error("Error message", component="tool_system")

        logs = logger.get_logs()

        assert "Info message" not in logs
        assert "Warning 1" not in logs
        assert "Warning 2" in logs
        assert "Error message" in logs

    def test_format_switching(self):
        """Test switching between formats."""
        logger = AgentLogger(name="test", format=LogFormat.TEXT)
        logger.info("Text message")

        logger.set_format(LogFormat.JSON)
        logger.info("JSON message")

        logs = logger.get_logs()

        # First message should be in text format
        assert "[INFO]" in logs

        # Second message should be in JSON format
        assert '"message": "JSON message"' in logs
