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
    from agent_framework.context import ContextManager


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
        context_manager: Optional context manager for multi-file context handling.
    """

    def __init__(
        self,
        name: str,
        config: Optional[Dict[str, Any]] = None,
        tool_registry: Optional["ToolRegistry"] = None,
        context_manager: Optional["ContextManager"] = None
    ):
        """
        Initialize the agent with a name and optional configuration.

        Args:
            name: A human-readable name for this agent instance.
            config: Optional dictionary of configuration parameters.
            tool_registry: Optional tool registry for managing agent tools.
            context_manager: Optional context manager for multi-file context handling.
        """
        self.name = name
        self.config = config or {}
        self.tool_registry = tool_registry
        self.context_manager = context_manager
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

    def add_context_file(
        self,
        file_path: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a file to the agent's context manager.

        This is a convenience method that delegates to the context manager's
        add_file method.

        Args:
            file_path: Path to the file (used as unique identifier).
            content: The file's content as a string.
            metadata: Optional dictionary of additional metadata.

        Raises:
            RuntimeError: If the agent doesn't have a context manager.
            ValueError: If file_path is empty or content is None.
        """
        if self.context_manager is None:
            raise RuntimeError(
                f"Agent '{self.name}' has no context manager. "
                "Initialize with a ContextManager to use context management."
            )
        self.context_manager.add_file(file_path, content, metadata)

    def get_context_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a file from the agent's context manager.

        This is a convenience method that delegates to the context manager's
        get_file method.

        Args:
            file_path: Path to the file to retrieve.

        Returns:
            Dictionary containing 'content', 'metadata', and 'size' keys,
            or None if the file is not found or agent has no context manager.
        """
        if self.context_manager is None:
            return None
        return self.context_manager.get_file(file_path)

    def has_context_file(self, file_path: str) -> bool:
        """
        Check if a file is in the agent's context manager.

        Args:
            file_path: Path to the file to check.

        Returns:
            True if the file exists, False otherwise.
            Returns False if the agent doesn't have a context manager.
        """
        if self.context_manager is None:
            return False
        return self.context_manager.has_file(file_path)

    def list_context_files(self) -> List[str]:
        """
        Get a list of all files in the agent's context.

        Returns:
            List of file paths in alphabetical order.
            Returns an empty list if the agent doesn't have a context manager.
        """
        if self.context_manager is None:
            return []
        return self.context_manager.list_files()

    def search_context(self, query: str, max_results: int = 10) -> List[str]:
        """
        Search for files in the agent's context.

        This is a convenience method that delegates to the context manager's
        search method.

        Args:
            query: The search string to look for.
            max_results: Maximum number of results to return.

        Returns:
            List of file paths that match the query.
            Returns empty list if the agent doesn't have a context manager.

        Raises:
            ValueError: If query is empty (when context manager exists).
        """
        if self.context_manager is None:
            return []
        return self.context_manager.search(query, max_results)

    def get_context_window(
        self,
        token_limit: Optional[int] = None,
        anchor_file: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get a subset of context files that fit within a token budget.

        This is a convenience method that delegates to the context manager's
        get_context_window method.

        Args:
            token_limit: Maximum number of tokens to include.
            anchor_file: Optional file path to use as anchor for prioritization.

        Returns:
            List of dictionaries with 'file_path', 'content', and 'metadata'.
            Returns empty list if the agent doesn't have a context manager.

        Raises:
            ValueError: If token_limit is less than or equal to 0 (when context manager exists).
        """
        if self.context_manager is None:
            return []
        return self.context_manager.get_context_window(token_limit=token_limit, anchor_file=anchor_file)
