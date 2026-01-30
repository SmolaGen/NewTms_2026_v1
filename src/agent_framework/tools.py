"""
Tool base class and registry for the extensible AI agent framework.

This module provides the Tool abstract class and ToolRegistry for managing
agent capabilities. Tools are modular, reusable components that agents can
execute to perform specific actions.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class Tool(ABC):
    """
    Abstract base class for all tools in the framework.

    Tools are discrete capabilities that agents can use to perform actions.
    Each tool has a name, description, parameter schema, and execute method.

    Attributes:
        name: A unique identifier for the tool.
        description: A human-readable description of what the tool does.
        parameters_schema: JSON schema defining the expected parameters.
    """

    def __init__(
        self,
        name: str,
        description: str,
        parameters_schema: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the tool with metadata.

        Args:
            name: A unique identifier for this tool.
            description: A human-readable description of the tool's purpose.
            parameters_schema: Optional JSON schema defining expected parameters.
        """
        self.name = name
        self.description = description
        self.parameters_schema = parameters_schema or {}

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        Execute the tool's primary action.

        This is the main entry point for tool execution. Subclasses must
        implement this method to define their specific behavior.

        Args:
            **kwargs: Keyword arguments matching the tool's parameter schema.

        Returns:
            The result of the tool's execution. Type depends on the tool.

        Raises:
            NotImplementedError: If the subclass doesn't implement this method.
        """
        pass

    def __repr__(self) -> str:
        """Return a string representation of the tool."""
        return f"{self.__class__.__name__}(name='{self.name}')"

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"Tool: {self.name} - {self.description}"


class ToolRegistry:
    """
    Registry for managing available tools.

    The ToolRegistry maintains a collection of tools and provides methods
    for registration, retrieval, and execution. It ensures tool names are
    unique and provides a centralized access point for all agent tools.
    """

    def __init__(self):
        """Initialize an empty tool registry."""
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """
        Register a tool in the registry.

        Args:
            tool: The Tool instance to register.

        Raises:
            ValueError: If a tool with the same name is already registered.
            TypeError: If the provided object is not a Tool instance.
        """
        if not isinstance(tool, Tool):
            raise TypeError(f"Expected Tool instance, got {type(tool).__name__}")

        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")

        self._tools[tool.name] = tool

    def unregister(self, tool_name: str) -> None:
        """
        Remove a tool from the registry.

        Args:
            tool_name: The name of the tool to remove.

        Raises:
            KeyError: If the tool is not found in the registry.
        """
        if tool_name not in self._tools:
            raise KeyError(f"Tool '{tool_name}' not found in registry")

        del self._tools[tool_name]

    def get_tool(self, tool_name: str) -> Tool:
        """
        Retrieve a tool by name.

        Args:
            tool_name: The name of the tool to retrieve.

        Returns:
            The Tool instance.

        Raises:
            KeyError: If the tool is not found in the registry.
        """
        if tool_name not in self._tools:
            raise KeyError(f"Tool '{tool_name}' not found in registry")

        return self._tools[tool_name]

    def list_tools(self) -> List[str]:
        """
        Get a list of all registered tool names.

        Returns:
            A list of tool names in alphabetical order.
        """
        return sorted(self._tools.keys())

    def has_tool(self, tool_name: str) -> bool:
        """
        Check if a tool is registered.

        Args:
            tool_name: The name of the tool to check.

        Returns:
            True if the tool is registered, False otherwise.
        """
        return tool_name in self._tools

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Execute a tool by name.

        This is a convenience method that retrieves and executes a tool
        in a single call.

        Args:
            tool_name: The name of the tool to execute.
            **kwargs: Keyword arguments to pass to the tool's execute method.

        Returns:
            The result of the tool's execution.

        Raises:
            KeyError: If the tool is not found in the registry.
        """
        tool = self.get_tool(tool_name)
        return tool.execute(**kwargs)

    def clear(self) -> None:
        """Remove all tools from the registry."""
        self._tools.clear()

    def __len__(self) -> int:
        """Return the number of registered tools."""
        return len(self._tools)

    def __repr__(self) -> str:
        """Return a string representation of the registry."""
        return f"ToolRegistry(tools={len(self._tools)})"

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        tool_list = ", ".join(self.list_tools()) if self._tools else "none"
        return f"ToolRegistry with {len(self._tools)} tool(s): {tool_list}"
