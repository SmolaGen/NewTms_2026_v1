#!/usr/bin/env python3
"""
Custom Tools Example

This example demonstrates how to create custom tools and integrate them
with agents. It shows tool registration, parameter validation, and execution.
"""

import sys
from pathlib import Path
import json

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from agent_framework.agent import Agent
from agent_framework.tools import Tool, ToolRegistry
from agent_framework.logging import AgentLogger, LogLevel


# Custom Tool 1: Calculator
class CalculatorTool(Tool):
    """A tool that performs basic arithmetic operations."""

    def execute(self, **kwargs) -> float:
        """
        Execute arithmetic operation.

        Args:
            **kwargs: Must include 'operation' and 'operands'

        Returns:
            Numeric result of the operation
        """
        operation = kwargs.get("operation")
        operands = kwargs.get("operands", [])

        if operation == "add":
            return sum(operands)
        elif operation == "multiply":
            result = 1
            for num in operands:
                result *= num
            return result
        elif operation == "subtract":
            if len(operands) < 2:
                return 0
            result = operands[0]
            for num in operands[1:]:
                result -= num
            return result
        elif operation == "divide":
            if len(operands) < 2:
                return 0
            result = operands[0]
            for num in operands[1:]:
                if num == 0:
                    raise ValueError("Cannot divide by zero")
                result /= num
            return result
        else:
            raise ValueError(f"Unknown operation: {operation}")


# Custom Tool 2: String Formatter
class StringFormatterTool(Tool):
    """A tool that formats strings in various ways."""

    def execute(self, **kwargs) -> str:
        """
        Execute string formatting.

        Args:
            **kwargs: Must include 'text' and 'format_type'

        Returns:
            Formatted string
        """
        text = kwargs.get("text", "")
        format_type = kwargs.get("format_type", "none")

        if format_type == "uppercase":
            return text.upper()
        elif format_type == "lowercase":
            return text.lower()
        elif format_type == "title":
            return text.title()
        elif format_type == "reverse":
            return text[::-1]
        elif format_type == "snake_case":
            return text.lower().replace(" ", "_")
        else:
            return text


# Custom Tool 3: JSON Validator
class JSONValidatorTool(Tool):
    """A tool that validates and pretty-prints JSON."""

    def execute(self, **kwargs) -> dict:
        """
        Validate and format JSON.

        Args:
            **kwargs: Must include 'json_string'

        Returns:
            Dictionary with validation results
        """
        json_string = kwargs.get("json_string", "")

        try:
            parsed = json.loads(json_string)
            pretty = json.dumps(parsed, indent=2)
            return {
                "valid": True,
                "parsed": parsed,
                "pretty": pretty
            }
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "error": str(e),
                "position": e.pos
            }


# Agent that uses custom tools
class ToolAssistantAgent(Agent):
    """An agent that assists users by executing various tools."""

    def execute(self, task: str, **kwargs) -> dict:
        """
        Execute a task using available tools.

        Args:
            task: The task to perform (tool name)
            **kwargs: Parameters to pass to the tool

        Returns:
            Dictionary with execution results
        """
        self._log("info", f"Executing task with tool: {task}", task=task)

        if not self.has_tool(task):
            available = ", ".join(self.list_tools())
            return {
                "success": False,
                "error": f"Unknown tool: {task}. Available: {available}"
            }

        try:
            result = self.execute_tool(task, **kwargs)
            return {
                "success": True,
                "tool": task,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "tool": task,
                "error": str(e)
            }

    def process_context(self, context: dict) -> dict:
        """Process context for tool execution."""
        return {
            "tool": context.get("tool", ""),
            "parameters": context.get("parameters", {})
        }

    def format_response(self, result: any) -> str:
        """Format tool execution results."""
        if isinstance(result, dict):
            if not result.get("success", False):
                return f"Error: {result.get('error', 'Unknown error')}"

            tool = result.get("tool", "unknown")
            value = result.get("result")

            if isinstance(value, dict) and "pretty" in value:
                return f"Tool '{tool}' result:\n{value['pretty']}"

            return f"Tool '{tool}' result: {value}"

        return str(result)


def main():
    """Main function demonstrating custom tools."""
    print("=" * 60)
    print("Custom Tools Example")
    print("=" * 60)
    print()

    # Create logger and tool registry
    logger = AgentLogger(
        name="tool_assistant",
        level=LogLevel.INFO,
        format="text"
    )

    tool_registry = ToolRegistry(logger=logger)

    # Register custom tools
    print("Registering custom tools...")
    print("-" * 40)

    calculator = CalculatorTool(
        name="calculator",
        description="Performs arithmetic operations",
        parameters_schema={
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"]
                },
                "operands": {
                    "type": "array",
                    "items": {"type": "number"}
                }
            },
            "required": ["operation", "operands"]
        },
        logger=logger
    )
    tool_registry.register(calculator)
    print(f"✓ Registered: {calculator.name}")

    formatter = StringFormatterTool(
        name="formatter",
        description="Formats strings in various ways",
        parameters_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "format_type": {
                    "type": "string",
                    "enum": ["uppercase", "lowercase", "title", "reverse", "snake_case"]
                }
            },
            "required": ["text", "format_type"]
        },
        logger=logger
    )
    tool_registry.register(formatter)
    print(f"✓ Registered: {formatter.name}")

    validator = JSONValidatorTool(
        name="json_validator",
        description="Validates and formats JSON",
        parameters_schema={
            "type": "object",
            "properties": {
                "json_string": {"type": "string"}
            },
            "required": ["json_string"]
        },
        logger=logger
    )
    tool_registry.register(validator)
    print(f"✓ Registered: {validator.name}")
    print()

    # Create agent with tools
    agent = ToolAssistantAgent(
        name="ToolAssistant",
        config={"version": "1.0"},
        tool_registry=tool_registry,
        logger=logger
    )

    agent.initialize()
    print(f"Agent initialized with {len(agent.list_tools())} tools\n")

    # Example 1: Calculator - Addition
    print("Example 1: Calculator - Addition")
    print("-" * 40)
    result = agent.execute(
        "calculator",
        operation="add",
        operands=[10, 20, 30]
    )
    response = agent.format_response(result)
    print(f"Input: add(10, 20, 30)")
    print(f"Output: {response}\n")

    # Example 2: Calculator - Division
    print("Example 2: Calculator - Division")
    print("-" * 40)
    result = agent.execute(
        "calculator",
        operation="divide",
        operands=[100, 5, 2]
    )
    response = agent.format_response(result)
    print(f"Input: divide(100, 5, 2)")
    print(f"Output: {response}\n")

    # Example 3: String Formatter - Title Case
    print("Example 3: String Formatter - Title Case")
    print("-" * 40)
    result = agent.execute(
        "formatter",
        text="hello world from the agent framework",
        format_type="title"
    )
    response = agent.format_response(result)
    print(f"Input: 'hello world from the agent framework'")
    print(f"Output: {response}\n")

    # Example 4: String Formatter - Snake Case
    print("Example 4: String Formatter - Snake Case")
    print("-" * 40)
    result = agent.execute(
        "formatter",
        text="Convert This To Snake Case",
        format_type="snake_case"
    )
    response = agent.format_response(result)
    print(f"Input: 'Convert This To Snake Case'")
    print(f"Output: {response}\n")

    # Example 5: JSON Validator - Valid JSON
    print("Example 5: JSON Validator - Valid JSON")
    print("-" * 40)
    json_input = '{"name": "Agent", "version": 1.0, "active": true}'
    result = agent.execute(
        "json_validator",
        json_string=json_input
    )
    response = agent.format_response(result)
    print(f"Input: {json_input}")
    print(f"Output: {response}\n")

    # Example 6: JSON Validator - Invalid JSON
    print("Example 6: JSON Validator - Invalid JSON")
    print("-" * 40)
    invalid_json = '{"name": "Agent", "version": 1.0, "active": true'  # Missing closing brace
    result = agent.execute(
        "json_validator",
        json_string=invalid_json
    )
    response = agent.format_response(result)
    print(f"Input: {invalid_json}")
    print(f"Output: {response}\n")

    # Example 7: Error handling - Unknown tool
    print("Example 7: Error Handling - Unknown Tool")
    print("-" * 40)
    result = agent.execute("nonexistent_tool", param="value")
    response = agent.format_response(result)
    print(f"Output: {response}\n")

    # Show tool registry statistics
    print("Tool Registry Statistics")
    print("-" * 40)
    print(f"Total tools: {len(tool_registry)}")
    print(f"Available tools: {', '.join(tool_registry.list_tools())}")
    print()

    # Cleanup
    agent.cleanup()
    print("Agent cleaned up successfully")
    print()
    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
