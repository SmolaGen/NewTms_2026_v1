"""
Base Agent abstract class for the extensible AI agent framework.

This module provides the foundational Agent class that all custom agents
must inherit from. It defines the core interface for agent behavior including
execution, context processing, and response formatting.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class Agent(ABC):
    """
    Abstract base class for all AI agents in the framework.

    This class defines the core interface that all agents must implement.
    Subclasses should override the abstract methods to provide specific
    agent behavior for different use cases.

    Attributes:
        name: A human-readable name for the agent instance.
        config: Optional configuration dictionary for agent-specific settings.
    """

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent with a name and optional configuration.

        Args:
            name: A human-readable name for this agent instance.
            config: Optional dictionary of configuration parameters.
        """
        self.name = name
        self.config = config or {}
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
