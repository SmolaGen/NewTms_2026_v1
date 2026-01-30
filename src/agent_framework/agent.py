"""
Base Agent abstract class for the extensible AI agent framework.

This module provides the foundational Agent class that all custom agents
must inherit from. It defines the core interface for agent behavior including
execution, context processing, and response formatting.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from agent_framework.tools import Tool, ToolRegistry


class Agent(ABC):
    """
    Abstract base class for all AI agents in the framework.

    This class defines the core interface that all agents must implement.
    Subclasses should override the abstract methods to provide specific
    agent behavior for different use cases.

    Attributes:
        name: A human-readable name for the agent instance.
        config: Optional configuration dictionary for agent-specific settings.
        tool_registry: Optional tool registry for managing agent capabilities.
    """

    def __init__(
        self,
        name: str,
        config: Optional[Dict[str, Any]] = None,
        tool_registry: Optional["ToolRegistry"] = None
    ):
        """
        Initialize the agent with a name and optional configuration.

        Args:
            name: A human-readable name for this agent instance.
            config: Optional dictionary of configuration parameters.
            tool_registry: Optional tool registry for managing agent tools.
        """
        self.name = name
        self.config = config or {}
        self.tool_registry = tool_registry
        self._initialized = False

    @abstractmethod
    def execute(self, task: str, **kwargs) -> Any:
        """
        Execute the primary task for this agent.

        This is the main entry point for agent execution. Subclasses must
        implement this method to define their core behavior.

        Args:
            task: The task description or instruction for the agent to execute.
            **kwargs: Additional keyword arguments specific to the agent type.

        Returns:
            The result of the agent's execution. Type depends on the agent.

        Raises:
            NotImplementedError: If the subclass doesn't implement this method.
        """
        pass

    @abstractmethod
    def process_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and transform context information for the agent.

        This method handles context preparation, filtering, and transformation
        to make it suitable for the agent's execution. This is where multi-file
        context management and prioritization should occur.

        Args:
            context: Raw context dictionary containing relevant information.

        Returns:
            Processed context dictionary ready for agent execution.

        Raises:
            NotImplementedError: If the subclass doesn't implement this method.
        """
        pass

    @abstractmethod
    def format_response(self, result: Any) -> str:
        """
        Format the agent's execution result into a human-readable response.

        This method transforms the raw execution result into a formatted
        string suitable for presentation to users or downstream systems.

        Args:
            result: The raw result from the agent's execution.

        Returns:
            A formatted string representation of the result.

        Raises:
            NotImplementedError: If the subclass doesn't implement this method.
        """
        pass

    def __repr__(self) -> str:
        """Return a string representation of the agent."""
        return f"{self.__class__.__name__}(name='{self.name}')"

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"Agent: {self.name}"

    def initialize(self) -> None:
        """
        Initialize the agent and prepare it for execution.

        This method sets up the agent's state and resources. It should be called
        before the agent starts executing tasks. The method is idempotent - calling
        it multiple times has no additional effect after the first call.

        Subclasses can override this method to add custom initialization logic,
        but should call super().initialize() to ensure proper base initialization.

        Raises:
            RuntimeError: If initialization fails.
        """
        if not self._initialized:
            self._initialized = True

    def cleanup(self) -> None:
        """
        Clean up the agent's resources and reset its state.

        This method should be called when the agent is no longer needed to ensure
        proper resource cleanup. It is idempotent - calling it multiple times is safe.

        Subclasses can override this method to add custom cleanup logic,
        but should call super().cleanup() to ensure proper base cleanup.
        """
        if self._initialized:
            self._initialized = False

    def register_tool(self, tool: "Tool") -> None:
        """
        Register a tool with the agent's tool registry.

        This is a convenience method that delegates to the tool registry's
        register method.

        Args:
            tool: The Tool instance to register.

        Raises:
            RuntimeError: If the agent doesn't have a tool registry.
            ValueError: If a tool with the same name is already registered.
            TypeError: If the provided object is not a Tool instance.
        """
        if self.tool_registry is None:
            raise RuntimeError(
                f"Agent '{self.name}' has no tool registry. "
                "Initialize with a ToolRegistry to use tools."
            )
        self.tool_registry.register(tool)

    def has_tool(self, tool_name: str) -> bool:
        """
        Check if a tool is registered with the agent.

        Args:
            tool_name: The name of the tool to check.

        Returns:
            True if the tool is registered, False otherwise.
            Returns False if the agent doesn't have a tool registry.
        """
        if self.tool_registry is None:
            return False
        return self.tool_registry.has_tool(tool_name)

    def list_tools(self) -> List[str]:
        """
        Get a list of all tools available to the agent.

        Returns:
            A list of tool names in alphabetical order.
            Returns an empty list if the agent doesn't have a tool registry.
        """
        if self.tool_registry is None:
            return []
        return self.tool_registry.list_tools()

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Execute a tool by name with parameter validation.

        This is a convenience method that delegates to the tool registry's
        execute_tool method.

        Args:
            tool_name: The name of the tool to execute.
            **kwargs: Keyword arguments to pass to the tool's execute method.

        Returns:
            The result of the tool's execution.

        Raises:
            RuntimeError: If the agent doesn't have a tool registry.
            KeyError: If the tool is not found in the registry.
            ValidationError: If parameters don't match the tool's schema.
        """
        if self.tool_registry is None:
            raise RuntimeError(
                f"Agent '{self.name}' has no tool registry. "
                "Initialize with a ToolRegistry to use tools."
            )
        return self.tool_registry.execute_tool(tool_name, **kwargs)
