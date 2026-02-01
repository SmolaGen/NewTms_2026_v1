#!/usr/bin/env python3
"""
Simple Agent Example

This example demonstrates the basic usage of the AI Agent framework.
It creates a simple agent that processes text tasks and maintains state.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from agent_framework.agent import Agent
from agent_framework.logging import AgentLogger, LogLevel


class SimpleTextAgent(Agent):
    """
    A simple agent that processes text and performs basic operations.

    This agent demonstrates the core Agent interface implementation
    including initialization, task execution, context processing, and
    response formatting.
    """

    def execute(self, task: str, **kwargs) -> dict:
        """
        Execute a text processing task.

        Args:
            task: The task description (e.g., "count_words", "reverse", "uppercase")
            **kwargs: Additional parameters like 'text' to process

        Returns:
            Dictionary with the result and metadata
        """
        self._log("info", f"Executing task: {task}", task=task)

        text = kwargs.get("text", "")

        if task == "count_words":
            result = len(text.split())
            return {
                "task": task,
                "result": result,
                "unit": "words"
            }
        elif task == "reverse":
            result = text[::-1]
            return {
                "task": task,
                "result": result
            }
        elif task == "uppercase":
            result = text.upper()
            return {
                "task": task,
                "result": result
            }
        else:
            return {
                "task": task,
                "result": None,
                "error": f"Unknown task: {task}"
            }

    def process_context(self, context: dict) -> dict:
        """
        Process and validate context information.

        Args:
            context: Raw context dictionary

        Returns:
            Processed context ready for execution
        """
        processed = {
            "text": context.get("text", ""),
            "metadata": {
                "source": context.get("source", "unknown"),
                "timestamp": context.get("timestamp", "N/A")
            }
        }

        self._log("debug", "Context processed",
                 text_length=len(processed["text"]))

        return processed

    def format_response(self, result: any) -> str:
        """
        Format the execution result into a human-readable string.

        Args:
            result: The raw result from execute()

        Returns:
            Formatted string representation
        """
        if isinstance(result, dict):
            if "error" in result:
                return f"Error: {result['error']}"

            task = result.get("task", "unknown")
            value = result.get("result", "N/A")

            if task == "count_words":
                unit = result.get("unit", "")
                return f"Word count: {value} {unit}"
            elif task in ["reverse", "uppercase"]:
                return f"Result: {value}"
            else:
                return f"Task '{task}' completed: {value}"

        return str(result)


def main():
    """Main function demonstrating agent usage."""
    print("=" * 60)
    print("Simple Agent Example")
    print("=" * 60)
    print()

    # Create a logger for debugging
    logger = AgentLogger(
        name="simple_agent",
        level=LogLevel.INFO,
        format="text"
    )

    # Create the agent
    agent = SimpleTextAgent(
        name="TextProcessor",
        config={"version": "1.0"},
        logger=logger
    )

    # Initialize the agent
    agent.initialize()
    print(f"Agent initialized: {agent}\n")

    # Example 1: Count words
    print("Example 1: Count words")
    print("-" * 40)
    context = {
        "text": "The quick brown fox jumps over the lazy dog",
        "source": "example",
        "timestamp": "2024-01-01"
    }
    processed_context = agent.process_context(context)
    result = agent.execute("count_words", text=processed_context["text"])
    response = agent.format_response(result)
    print(f"Input: {context['text']}")
    print(f"Output: {response}\n")

    # Example 2: Reverse text
    print("Example 2: Reverse text")
    print("-" * 40)
    text = "Hello, World!"
    result = agent.execute("reverse", text=text)
    response = agent.format_response(result)
    print(f"Input: {text}")
    print(f"Output: {response}\n")

    # Example 3: Uppercase text
    print("Example 3: Uppercase text")
    print("-" * 40)
    text = "make me loud"
    result = agent.execute("uppercase", text=text)
    response = agent.format_response(result)
    print(f"Input: {text}")
    print(f"Output: {response}\n")

    # Example 4: Unknown task (error handling)
    print("Example 4: Error handling")
    print("-" * 40)
    result = agent.execute("unknown_task", text="test")
    response = agent.format_response(result)
    print(f"Output: {response}\n")

    # Show agent logs
    print("Agent Logs")
    print("-" * 40)
    print(logger.get_logs())

    # Cleanup
    agent.cleanup()
    print("Agent cleaned up successfully")
    print()
    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
