"""
Tests for the Tool base class and ToolRegistry.

This module tests the Tool abstract class and ToolRegistry to ensure proper
abstraction, registration, and tool management functionality.
"""

import pytest
from typing import Any

from agent_framework.tools import Tool, ToolRegistry


class ConcreteTool(Tool):
    """A concrete implementation of Tool for testing purposes."""

    def execute(self, **kwargs) -> Any:
        """Execute a simple task by returning the kwargs."""
        return {"executed": True, "params": kwargs}


class CalculatorTool(Tool):
    """A calculator tool for testing arithmetic operations."""

    def execute(self, operation: str, a: float, b: float) -> float:
        """Execute arithmetic operations."""
        if operation == "add":
            return a + b
        elif operation == "subtract":
            return a - b
        elif operation == "multiply":
            return a * b
        elif operation == "divide":
            if b == 0:
                raise ValueError("Cannot divide by zero")
            return a / b
        else:
            raise ValueError(f"Unknown operation: {operation}")


class TestToolAbstraction:
    """Test suite for Tool abstract class behavior."""

    def test_cannot_instantiate_abstract_tool(self):
        """Test that Tool cannot be instantiated directly."""
        with pytest.raises(TypeError) as exc_info:
            Tool(name="test", description="test tool")

        assert "abstract" in str(exc_info.value).lower()

    def test_can_instantiate_concrete_tool(self):
        """Test that a concrete implementation can be instantiated."""
        tool = ConcreteTool(
            name="test_tool",
            description="A test tool"
        )
        assert tool is not None
        assert isinstance(tool, Tool)

    def test_tool_initialization(self):
        """Test that tool initializes with correct attributes."""
        schema = {"type": "object", "properties": {"param": {"type": "string"}}}
        tool = ConcreteTool(
            name="test_tool",
            description="A test tool",
            parameters_schema=schema
        )

        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
        assert tool.parameters_schema == schema

    def test_tool_initialization_without_schema(self):
        """Test that tool initializes with empty schema when none provided."""
        tool = ConcreteTool(name="test_tool", description="A test tool")

        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
        assert tool.parameters_schema == {}

    def test_execute_method(self):
        """Test that execute method works in concrete implementation."""
        tool = ConcreteTool(name="test_tool", description="A test tool")
        result = tool.execute(param1="value1", param2="value2")

        assert result["executed"] is True
        assert result["params"]["param1"] == "value1"
        assert result["params"]["param2"] == "value2"

    def test_tool_repr(self):
        """Test the __repr__ method."""
        tool = ConcreteTool(name="test_tool", description="A test tool")
        repr_str = repr(tool)

        assert "ConcreteTool" in repr_str
        assert "test_tool" in repr_str

    def test_tool_str(self):
        """Test the __str__ method."""
        tool = ConcreteTool(name="test_tool", description="A test tool")
        str_repr = str(tool)

        assert str_repr == "Tool: test_tool - A test tool"

    def test_abstract_execute_required(self):
        """Test that execute method must be implemented."""
        class IncompleteTool(Tool):
            pass

        with pytest.raises(TypeError):
            IncompleteTool(name="incomplete", description="incomplete tool")


class TestToolRegistry:
    """Test suite for ToolRegistry functionality."""

    def test_registry_initialization(self):
        """Test that registry initializes empty."""
        registry = ToolRegistry()

        assert len(registry) == 0
        assert registry.list_tools() == []

    def test_register_tool(self):
        """Test registering a tool."""
        registry = ToolRegistry()
        tool = ConcreteTool(name="test_tool", description="A test tool")

        registry.register(tool)

        assert len(registry) == 1
        assert registry.has_tool("test_tool")
        assert "test_tool" in registry.list_tools()

    def test_register_multiple_tools(self):
        """Test registering multiple tools."""
        registry = ToolRegistry()
        tool1 = ConcreteTool(name="tool1", description="First tool")
        tool2 = ConcreteTool(name="tool2", description="Second tool")

        registry.register(tool1)
        registry.register(tool2)

        assert len(registry) == 2
        assert registry.has_tool("tool1")
        assert registry.has_tool("tool2")
        assert registry.list_tools() == ["tool1", "tool2"]

    def test_register_duplicate_tool_raises_error(self):
        """Test that registering a tool with duplicate name raises error."""
        registry = ToolRegistry()
        tool1 = ConcreteTool(name="duplicate", description="First")
        tool2 = ConcreteTool(name="duplicate", description="Second")

        registry.register(tool1)

        with pytest.raises(ValueError) as exc_info:
            registry.register(tool2)

        assert "already registered" in str(exc_info.value)
        assert len(registry) == 1

    def test_register_non_tool_raises_error(self):
        """Test that registering a non-Tool object raises error."""
        registry = ToolRegistry()

        with pytest.raises(TypeError) as exc_info:
            registry.register("not a tool")

        assert "Expected Tool instance" in str(exc_info.value)

    def test_unregister_tool(self):
        """Test unregistering a tool."""
        registry = ToolRegistry()
        tool = ConcreteTool(name="test_tool", description="A test tool")

        registry.register(tool)
        assert len(registry) == 1

        registry.unregister("test_tool")
        assert len(registry) == 0
        assert not registry.has_tool("test_tool")

    def test_unregister_nonexistent_tool_raises_error(self):
        """Test that unregistering a non-existent tool raises error."""
        registry = ToolRegistry()

        with pytest.raises(KeyError) as exc_info:
            registry.unregister("nonexistent")

        assert "not found" in str(exc_info.value)

    def test_get_tool(self):
        """Test retrieving a tool by name."""
        registry = ToolRegistry()
        tool = ConcreteTool(name="test_tool", description="A test tool")

        registry.register(tool)
        retrieved = registry.get_tool("test_tool")

        assert retrieved is tool
        assert retrieved.name == "test_tool"

    def test_get_nonexistent_tool_raises_error(self):
        """Test that getting a non-existent tool raises error."""
        registry = ToolRegistry()

        with pytest.raises(KeyError) as exc_info:
            registry.get_tool("nonexistent")

        assert "not found" in str(exc_info.value)

    def test_has_tool(self):
        """Test checking if a tool exists."""
        registry = ToolRegistry()
        tool = ConcreteTool(name="test_tool", description="A test tool")

        assert not registry.has_tool("test_tool")

        registry.register(tool)
        assert registry.has_tool("test_tool")

        registry.unregister("test_tool")
        assert not registry.has_tool("test_tool")

    def test_list_tools_sorted(self):
        """Test that list_tools returns alphabetically sorted names."""
        registry = ToolRegistry()
        registry.register(ConcreteTool(name="zebra", description="Z"))
        registry.register(ConcreteTool(name="alpha", description="A"))
        registry.register(ConcreteTool(name="beta", description="B"))

        tools = registry.list_tools()
        assert tools == ["alpha", "beta", "zebra"]

    def test_execute_tool(self):
        """Test executing a tool through the registry."""
        registry = ToolRegistry()
        tool = CalculatorTool(
            name="calculator",
            description="Performs calculations"
        )
        registry.register(tool)

        result = registry.execute_tool("calculator", operation="add", a=5, b=3)
        assert result == 8

        result = registry.execute_tool("calculator", operation="multiply", a=4, b=7)
        assert result == 28

    def test_execute_nonexistent_tool_raises_error(self):
        """Test that executing a non-existent tool raises error."""
        registry = ToolRegistry()

        with pytest.raises(KeyError) as exc_info:
            registry.execute_tool("nonexistent")

        assert "not found" in str(exc_info.value)

    def test_clear_registry(self):
        """Test clearing all tools from the registry."""
        registry = ToolRegistry()
        registry.register(ConcreteTool(name="tool1", description="First"))
        registry.register(ConcreteTool(name="tool2", description="Second"))

        assert len(registry) == 2

        registry.clear()

        assert len(registry) == 0
        assert registry.list_tools() == []

    def test_registry_repr(self):
        """Test the __repr__ method."""
        registry = ToolRegistry()
        registry.register(ConcreteTool(name="tool1", description="First"))

        repr_str = repr(registry)
        assert "ToolRegistry" in repr_str
        assert "tools=1" in repr_str

    def test_registry_str(self):
        """Test the __str__ method."""
        registry = ToolRegistry()

        # Empty registry
        str_repr = str(registry)
        assert "0 tool(s)" in str_repr
        assert "none" in str_repr

        # Registry with tools
        registry.register(ConcreteTool(name="tool1", description="First"))
        registry.register(ConcreteTool(name="tool2", description="Second"))
        str_repr = str(registry)

        assert "2 tool(s)" in str_repr
        assert "tool1" in str_repr
        assert "tool2" in str_repr


class TestToolExecution:
    """Test suite for tool execution scenarios."""

    def test_tool_with_required_parameters(self):
        """Test tool execution with required parameters."""
        tool = CalculatorTool(
            name="calculator",
            description="Performs calculations",
            parameters_schema={
                "type": "object",
                "properties": {
                    "operation": {"type": "string"},
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["operation", "a", "b"]
            }
        )

        result = tool.execute(operation="add", a=10, b=5)
        assert result == 15

    def test_tool_error_handling(self):
        """Test that tool handles execution errors properly."""
        tool = CalculatorTool(name="calculator", description="Performs calculations")

        with pytest.raises(ValueError) as exc_info:
            tool.execute(operation="divide", a=10, b=0)

        assert "Cannot divide by zero" in str(exc_info.value)

    def test_tool_execution_through_registry(self):
        """Test complete workflow of registering and executing tools."""
        registry = ToolRegistry()

        # Register multiple tools
        calc_tool = CalculatorTool(name="calc", description="Calculator")
        test_tool = ConcreteTool(name="test", description="Test tool")

        registry.register(calc_tool)
        registry.register(test_tool)

        # Execute calculator tool
        result = registry.execute_tool("calc", operation="subtract", a=20, b=8)
        assert result == 12

        # Execute test tool
        result = registry.execute_tool("test", x=1, y=2)
        assert result["executed"] is True
        assert result["params"] == {"x": 1, "y": 2}


class TestToolDecorator:
    """Test suite for the @tool decorator functionality."""

    def test_tool_decorator(self):
        """Test that @tool decorator automatically registers tools."""
        from agent_framework.tools import tool

        # Create a fresh registry for this test
        test_registry = ToolRegistry()

        # Use decorator with custom registry
        @tool(registry=test_registry, name="decorated_tool", description="A decorated tool")
        class DecoratedTool(Tool):
            def execute(self, **kwargs) -> Any:
                return {"decorated": True, "params": kwargs}

        # Verify tool is registered
        assert test_registry.has_tool("decorated_tool")
        assert len(test_registry) == 1

        # Verify we can retrieve and execute the tool
        result = test_registry.execute_tool("decorated_tool", test_param="value")
        assert result["decorated"] is True
        assert result["params"]["test_param"] == "value"

        # Verify the class itself is still usable
        manual_instance = DecoratedTool(
            name="manual",
            description="Manual instance"
        )
        assert manual_instance.execute(x=1)["decorated"] is True


def test_tool_tracing():
    """Test that tool execution is properly traced with logger."""
    from agent_framework.logging import AgentLogger
    import json

    # Create logger with DEBUG level to capture all logs
    logger = AgentLogger(name="test_logger", level="DEBUG", format="json")

    # Create registry with logger
    registry = ToolRegistry(logger=logger)

    # Create and register tools
    calc_tool = CalculatorTool(name="calculator", description="Performs calculations")
    registry.register(calc_tool)

    # Test successful execution tracing
    result = registry.execute_tool("calculator", operation="add", a=5, b=3)
    assert result == 8

    # Parse logs
    logs = logger.get_logs()
    log_lines = [line for line in logs.strip().split('\n') if line]

    # Should have 2 log entries: start and complete
    assert len(log_lines) >= 2

    # Parse JSON logs
    log_entries = [json.loads(line) for line in log_lines]

    # Check start log
    start_log = log_entries[0]
    assert start_log["level"] == "DEBUG"
    assert "Executing tool: calculator" in start_log["message"]
    assert start_log["extra"]["action"] == "execute_tool_start"
    assert start_log["extra"]["tool_name"] == "calculator"
    assert start_log["extra"]["parameters"]["operation"] == "add"
    assert start_log["extra"]["parameters"]["a"] == 5
    assert start_log["extra"]["parameters"]["b"] == 3

    # Check completion log
    complete_log = log_entries[1]
    assert complete_log["level"] == "DEBUG"
    assert "Tool execution completed: calculator" in complete_log["message"]
    assert complete_log["extra"]["action"] == "execute_tool_complete"
    assert complete_log["extra"]["tool_name"] == "calculator"
    assert "execution_time" in complete_log["extra"]
    assert complete_log["extra"]["execution_time"] >= 0
    assert complete_log["extra"]["success"] is True

    # Clear logs for error test
    logger.clear_logs()

    # Test error tracing
    with pytest.raises(ValueError) as exc_info:
        registry.execute_tool("calculator", operation="divide", a=10, b=0)

    assert "Cannot divide by zero" in str(exc_info.value)

    # Parse error logs
    logs = logger.get_logs()
    log_lines = [line for line in logs.strip().split('\n') if line]

    # Should have 2 log entries: start and error
    assert len(log_lines) >= 2

    log_entries = [json.loads(line) for line in log_lines]

    # Check start log
    start_log = log_entries[0]
    assert start_log["extra"]["action"] == "execute_tool_start"

    # Check error log
    error_log = log_entries[1]
    assert error_log["level"] == "ERROR"
    assert "Tool execution failed: calculator" in error_log["message"]
    assert error_log["extra"]["action"] == "execute_tool_error"
    assert error_log["extra"]["tool_name"] == "calculator"
    assert "execution_time" in error_log["extra"]
    assert error_log["extra"]["execution_time"] >= 0
    assert error_log["extra"]["success"] is False
    assert "Cannot divide by zero" in error_log["extra"]["error"]
    assert error_log["extra"]["error_type"] == "ValueError"

    # Test registry without logger (no tracing)
    registry_no_logger = ToolRegistry()
    calc_tool_no_logger = CalculatorTool(name="calc2", description="Calculator without logger")
    registry_no_logger.register(calc_tool_no_logger)

    # Should execute normally without errors even without logger
    result = registry_no_logger.execute_tool("calc2", operation="add", a=1, b=2)
    assert result == 3
