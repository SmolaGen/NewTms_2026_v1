"""
Tool base class and registry for the extensible AI agent framework.

This module provides the Tool abstract class and ToolRegistry for managing
agent capabilities. Tools are modular, reusable components that agents can
execute to perform specific actions.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type, TYPE_CHECKING
import time

if TYPE_CHECKING:
    from agent_framework.logging import AgentLogger

try:
    import jsonschema
    from jsonschema import ValidationError as JsonSchemaValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    JsonSchemaValidationError = Exception


class ValidationError(Exception):
    """Raised when tool parameter validation fails."""
    pass


class Tool(ABC):
    """
    Abstract base class for all tools in the framework.

    Tools are discrete capabilities that agents can use to perform actions.
    Each tool has a name, description, parameter schema, and execute method.

    Attributes:
        name: A unique identifier for the tool.
        description: A human-readable description of what the tool does.
        parameters_schema: JSON schema defining the expected parameters.
        logger: Optional logger for tracing tool execution.
    """

    def __init__(
        self,
        name: str,
        description: str,
        parameters_schema: Optional[Dict[str, Any]] = None,
        logger: Optional["AgentLogger"] = None
    ):
        """
        Initialize the tool with metadata.

        Args:
            name: A unique identifier for this tool.
            description: A human-readable description of the tool's purpose.
            parameters_schema: Optional JSON schema defining expected parameters.
            logger: Optional logger for tracing tool execution.
        """
        self.name = name
        self.description = description
        self.parameters_schema = parameters_schema or {}
        self.logger = logger

    def _log(self, level: str, message: str, **extra) -> None:
        """
        Internal helper to safely log messages if logger is available.

        Args:
            level: Log level (debug, info, warning, error, critical).
            message: The message to log.
            **extra: Additional context to include in the log.
        """
        if self.logger is not None:
            log_method = getattr(self.logger, level.lower(), None)
            if log_method is not None:
                log_method(message, tool=self.name, **extra)

    def validate_parameters(self, **kwargs) -> None:
        """
        Validate parameters against the tool's parameter schema.

        Args:
            **kwargs: Keyword arguments to validate.

        Raises:
            ValueError: If jsonschema is not available and schema is defined.
            ValidationError: If parameters don't match the schema.
        """
        if not self.parameters_schema:
            # No schema defined, skip validation
            return

        if not JSONSCHEMA_AVAILABLE:
            raise ValueError(
                "jsonschema library is required for parameter validation but not installed"
            )

        try:
            jsonschema.validate(instance=kwargs, schema=self.parameters_schema)
        except JsonSchemaValidationError as e:
            # Re-raise with a more descriptive message
            raise ValidationError(
                f"Parameter validation failed for tool '{self.name}': {e.message}"
            ) from e

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

    Attributes:
        logger: Optional logger for tracing tool registry operations.
    """

    def __init__(self, logger: Optional["AgentLogger"] = None):
        """
        Initialize an empty tool registry.

        Args:
            logger: Optional logger for tracing tool registry operations.
        """
        self._tools: Dict[str, Tool] = {}
        self.logger = logger

    def _log(self, level: str, message: str, **extra) -> None:
        """
        Internal helper to safely log messages if logger is available.

        Args:
            level: Log level (debug, info, warning, error, critical).
            message: The message to log.
            **extra: Additional context to include in the log.
        """
        if self.logger is not None:
            log_method = getattr(self.logger, level.lower(), None)
            if log_method is not None:
                log_method(message, component="ToolRegistry", **extra)

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
        Execute a tool by name with parameter validation and tracing.

        This is a convenience method that retrieves a tool, validates
        its parameters, executes it, and traces the execution (inputs,
        outputs, timing, and errors).

        Args:
            tool_name: The name of the tool to execute.
            **kwargs: Keyword arguments to pass to the tool's execute method.

        Returns:
            The result of the tool's execution.

        Raises:
            KeyError: If the tool is not found in the registry.
            ValidationError: If parameters don't match the tool's schema.
        """
        # Log tool execution start with inputs
        self._log("debug", f"Executing tool: {tool_name}",
                  action="execute_tool_start",
                  tool_name=tool_name,
                  parameters=kwargs)

        # Get and validate tool
        tool = self.get_tool(tool_name)
        tool.validate_parameters(**kwargs)

        # Execute with timing and error handling
        start_time = time.time()
        error_occurred = False
        error_message = None
        result = None

        try:
            result = tool.execute(**kwargs)
            execution_time = time.time() - start_time

            # Log successful execution
            self._log("debug", f"Tool execution completed: {tool_name}",
                      action="execute_tool_complete",
                      tool_name=tool_name,
                      execution_time=execution_time,
                      success=True)

            return result

        except Exception as e:
            error_occurred = True
            error_message = str(e)
            execution_time = time.time() - start_time

            # Log error
            self._log("error", f"Tool execution failed: {tool_name}",
                      action="execute_tool_error",
                      tool_name=tool_name,
                      execution_time=execution_time,
                      error=error_message,
                      error_type=type(e).__name__,
                      success=False)

            # Re-raise the exception
            raise

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


def tool(
    registry: ToolRegistry,
    name: str,
    description: str,
    parameters_schema: Optional[Dict[str, Any]] = None
) -> Callable[[Type[Tool]], Type[Tool]]:
    """
    Decorator for automatic tool registration.

    This decorator simplifies tool creation by automatically registering
    a tool instance to a registry when the class is defined. The decorated
    class can still be instantiated manually if needed.

    Args:
        registry: The ToolRegistry to register the tool with.
        name: A unique identifier for the tool.
        description: A human-readable description of the tool's purpose.
        parameters_schema: Optional JSON schema defining expected parameters.

    Returns:
        A decorator function that registers the tool and returns the class.

    Example:
        >>> registry = ToolRegistry()
        >>> @tool(registry=registry, name="my_tool", description="Does something")
        ... class MyTool(Tool):
        ...     def execute(self, **kwargs):
        ...         return "result"
        >>> registry.has_tool("my_tool")
        True
    """
    def decorator(tool_class: Type[Tool]) -> Type[Tool]:
        """
        Inner decorator that wraps the tool class.

        Args:
            tool_class: The Tool class to register.

        Returns:
            The original tool class, unmodified.
        """
        # Create an instance of the tool with the provided metadata
        tool_instance = tool_class(
            name=name,
            description=description,
            parameters_schema=parameters_schema
        )

        # Register the instance with the registry
        registry.register(tool_instance)

        # Return the original class so it can still be used
        return tool_class

    return decorator
