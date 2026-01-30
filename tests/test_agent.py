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
