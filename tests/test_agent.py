"""
Tests for the base Agent abstract class.

This module tests the Agent base class to ensure proper abstraction,
initialization, and interface compliance.
"""

import pytest
from typing import Any, Dict

from agent_framework.agent import Agent


class ConcreteAgent(Agent):
    """A concrete implementation of Agent for testing purposes."""

    def execute(self, task: str, **kwargs) -> Any:
        """Execute a simple task by returning it."""
        return f"Executing: {task}"

    def process_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process context by adding a processed flag."""
        processed = context.copy()
        processed["_processed"] = True
        return processed

    def format_response(self, result: Any) -> str:
        """Format the result as a string."""
        return f"Response: {result}"


class TestAgentAbstraction:
    """Test suite for Agent abstract class behavior."""

    def test_cannot_instantiate_abstract_agent(self):
        """Test that Agent cannot be instantiated directly."""
        with pytest.raises(TypeError) as exc_info:
            Agent(name="test")

        assert "abstract" in str(exc_info.value).lower()

    def test_can_instantiate_concrete_agent(self):
        """Test that a concrete implementation can be instantiated."""
        agent = ConcreteAgent(name="test_agent")
        assert agent is not None
        assert isinstance(agent, Agent)

    def test_agent_initialization(self):
        """Test that agent initializes with correct attributes."""
        agent = ConcreteAgent(name="test_agent", config={"key": "value"})

        assert agent.name == "test_agent"
        assert agent.config == {"key": "value"}
        assert agent._initialized is False

    def test_agent_initialization_without_config(self):
        """Test that agent initializes with empty config when none provided."""
        agent = ConcreteAgent(name="test_agent")

        assert agent.name == "test_agent"
        assert agent.config == {}

    def test_execute_method(self):
        """Test that execute method works in concrete implementation."""
        agent = ConcreteAgent(name="test_agent")
        result = agent.execute("test task")

        assert result == "Executing: test task"

    def test_process_context_method(self):
        """Test that process_context method works in concrete implementation."""
        agent = ConcreteAgent(name="test_agent")
        context = {"file": "test.py", "content": "code"}
        processed = agent.process_context(context)

        assert processed["file"] == "test.py"
        assert processed["content"] == "code"
        assert processed["_processed"] is True

    def test_format_response_method(self):
        """Test that format_response method works in concrete implementation."""
        agent = ConcreteAgent(name="test_agent")
        formatted = agent.format_response("test result")

        assert formatted == "Response: test result"

    def test_agent_repr(self):
        """Test the __repr__ method."""
        agent = ConcreteAgent(name="test_agent")
        repr_str = repr(agent)

        assert "ConcreteAgent" in repr_str
        assert "test_agent" in repr_str

    def test_agent_str(self):
        """Test the __str__ method."""
        agent = ConcreteAgent(name="test_agent")
        str_repr = str(agent)

        assert str_repr == "Agent: test_agent"

    def test_abstract_methods_required(self):
        """Test that all abstract methods must be implemented."""
        # Class missing execute method
        class IncompleteAgent1(Agent):
            def process_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
                return context

            def format_response(self, result: Any) -> str:
                return str(result)

        with pytest.raises(TypeError):
            IncompleteAgent1(name="incomplete")

        # Class missing process_context method
        class IncompleteAgent2(Agent):
            def execute(self, task: str, **kwargs) -> Any:
                return task

            def format_response(self, result: Any) -> str:
                return str(result)

        with pytest.raises(TypeError):
            IncompleteAgent2(name="incomplete")

        # Class missing format_response method
        class IncompleteAgent3(Agent):
            def execute(self, task: str, **kwargs) -> Any:
                return task

            def process_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
                return context

        with pytest.raises(TypeError):
            IncompleteAgent3(name="incomplete")

    def test_agent_lifecycle(self):
        """Test agent lifecycle methods (initialize, cleanup)."""
        agent = ConcreteAgent(name="lifecycle_agent")

        # Initially not initialized
        assert agent._initialized is False

        # Initialize the agent
        agent.initialize()
        assert agent._initialized is True

        # Initialize is idempotent
        agent.initialize()
        assert agent._initialized is True

        # Cleanup the agent
        agent.cleanup()
        assert agent._initialized is False

        # Cleanup is idempotent
        agent.cleanup()
        assert agent._initialized is False

        # Can re-initialize after cleanup
        agent.initialize()
        assert agent._initialized is True


class TestAgentWithTools:
    """Test suite for Agent integration with tool system."""

    def test_agent_with_tools(self):
        """Test that agents can be initialized with a tool registry."""
        from agent_framework.tools import ToolRegistry, Tool

        # Create a simple tool for testing
        class TestTool(Tool):
            def execute(self, **kwargs):
                return f"Tool executed with {kwargs}"

        # Create a tool registry and register the tool
        registry = ToolRegistry()
        tool = TestTool(name="test_tool", description="A test tool")
        registry.register(tool)

        # Create an agent with the tool registry
        agent = ConcreteAgent(name="tool_agent", tool_registry=registry)

        # Verify the agent has the tool registry
        assert agent.tool_registry is registry
        assert agent.has_tool("test_tool")
        assert agent.list_tools() == ["test_tool"]

        # Verify the agent can execute tools
        result = agent.execute_tool("test_tool", param="value")
        assert "Tool executed" in result
        assert "param" in result

    def test_agent_without_tools(self):
        """Test that agents work without a tool registry."""
        agent = ConcreteAgent(name="simple_agent")

        # Verify the agent has no tool registry
        assert agent.tool_registry is None
        assert agent.list_tools() == []
        assert not agent.has_tool("anything")

    def test_agent_register_tool(self):
        """Test that agents can register tools to their registry."""
        from agent_framework.tools import ToolRegistry, Tool

        class AnotherTool(Tool):
            def execute(self, **kwargs):
                return "executed"

        registry = ToolRegistry()
        agent = ConcreteAgent(name="agent", tool_registry=registry)

        # Register a new tool through the agent
        tool = AnotherTool(name="another_tool", description="Another test tool")
        agent.register_tool(tool)

        # Verify the tool is registered
        assert agent.has_tool("another_tool")
        assert "another_tool" in agent.list_tools()

    def test_agent_execute_tool_without_registry_raises_error(self):
        """Test that executing a tool without a registry raises an error."""
        agent = ConcreteAgent(name="no_tools")

        with pytest.raises(RuntimeError) as exc_info:
            agent.execute_tool("nonexistent")

        assert "No tool registry" in str(exc_info.value)

    def test_agent_register_tool_without_registry_raises_error(self):
        """Test that registering a tool without a registry raises an error."""
        from agent_framework.tools import Tool

        class SomeTool(Tool):
            def execute(self, **kwargs):
                return "result"

        agent = ConcreteAgent(name="no_tools")
        tool = SomeTool(name="some_tool", description="Some tool")

        with pytest.raises(RuntimeError) as exc_info:
            agent.register_tool(tool)

        assert "No tool registry" in str(exc_info.value)
