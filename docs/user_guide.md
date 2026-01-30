# User Guide

Welcome to the Extensible AI Agent Framework! This guide will help you get started building custom AI agents with proper abstractions, context management, and tool integration capabilities.

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Building Your First Agent](#building-your-first-agent)
- [Working with Tools](#working-with-tools)
- [Managing Context](#managing-context)
- [Logging and Debugging](#logging-and-debugging)
- [Advanced Topics](#advanced-topics)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Introduction

The Extensible AI Agent Framework addresses fundamental limitations that competing tools (GitHub Copilot, Cursor, Windsurf) struggle with - inconsistent code quality and limited context awareness. This framework provides:

- **Modular Architecture**: Build specialized agents with a clean, extensible design
- **Context Management**: Efficiently handle multi-file codebases (100+ files)
- **Tool System**: Add capabilities to agents through reusable tools
- **Comprehensive Logging**: Debug and monitor agent behavior with structured logging
- **Performance Optimized**: Benchmarked for context processing efficiency

### Who This Framework Is For

- Developers building AI-powered code analysis tools
- Teams creating custom AI assistants for specific domains
- Researchers experimenting with multi-file reasoning systems
- Anyone needing reliable, context-aware AI agents

---

## Installation

### Basic Installation

```bash
pip install -e .
```

### Development Installation

For development with testing and formatting tools:

```bash
pip install -e ".[dev]"
```

### Requirements

- Python 3.8 or higher
- Optional: `jsonschema` for tool parameter validation (recommended)

---

## Quick Start

Here's a minimal example to get you started:

```python
from agent_framework import Agent
from agent_framework.logging import AgentLogger

class SimpleAgent(Agent):
    """A simple agent that processes text."""

    def execute(self, task: str, **kwargs) -> dict:
        """Execute a task."""
        text = kwargs.get("text", "")
        return {"result": text.upper()}

    def process_context(self, context: dict) -> dict:
        """Process context information."""
        return {"text": context.get("text", "")}

    def format_response(self, result: any) -> str:
        """Format the result."""
        return f"Result: {result.get('result', 'N/A')}"

# Create and use the agent
logger = AgentLogger("my-agent")
agent = SimpleAgent("simple-agent", logger=logger)
agent.initialize()

result = agent.execute("uppercase", text="hello world")
print(agent.format_response(result))  # Output: Result: HELLO WORLD

agent.cleanup()
```

---

## Core Concepts

### 1. Agent

The `Agent` class is the foundation of the framework. Every custom agent must inherit from `Agent` and implement three abstract methods:

- **`execute(task, **kwargs)`**: The main entry point for agent execution
- **`process_context(context)`**: Transform and prepare context information
- **`format_response(result)`**: Format execution results for presentation

Agents also support:
- Lifecycle management (`initialize()`, `cleanup()`)
- Tool integration
- Context management
- Structured logging

### 2. Tools

Tools are modular capabilities that agents can use. Each tool:
- Has a unique name and description
- Defines expected parameters using JSON schema
- Implements an `execute()` method
- Can be registered with a `ToolRegistry`

Tools enable:
- Code reuse across agents
- Parameter validation
- Execution tracing and logging

### 3. Context Manager

The `ContextManager` handles multi-file context efficiently:
- Stores and indexes file content
- Tracks relationships between files
- Provides search capabilities
- Manages memory with LRU eviction
- Supports context window management for token budgets

### 4. Logger

The `AgentLogger` provides structured logging:
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Output formats (text and JSON)
- Filtering by level and attributes
- Introspection into agent behavior

---

## Building Your First Agent

Let's build a more complete agent that analyzes code:

```python
from agent_framework import Agent
from agent_framework.logging import AgentLogger, LogLevel

class CodeAnalyzer(Agent):
    """Agent that analyzes code structure and complexity."""

    def execute(self, task: str, **kwargs) -> dict:
        """
        Execute code analysis tasks.

        Supported tasks:
        - count_lines: Count lines of code
        - find_functions: Extract function definitions
        - complexity: Estimate code complexity
        """
        code = kwargs.get("code", "")

        if task == "count_lines":
            lines = code.split("\n")
            return {
                "total_lines": len(lines),
                "non_empty": len([l for l in lines if l.strip()])
            }

        elif task == "find_functions":
            import re
            functions = re.findall(r'def\s+(\w+)\s*\(', code)
            return {"functions": functions, "count": len(functions)}

        elif task == "complexity":
            # Simple complexity estimate based on conditionals and loops
            import re
            keywords = len(re.findall(r'\b(if|for|while|try)\b', code))
            return {"complexity_score": keywords, "level": "low" if keywords < 5 else "medium"}

        else:
            raise ValueError(f"Unknown task: {task}")

    def process_context(self, context: dict) -> dict:
        """Validate and prepare context."""
        if "code" not in context:
            raise ValueError("Context must contain 'code' field")

        return {
            "code": context["code"],
            "filename": context.get("filename", "unknown"),
            "language": context.get("language", "python")
        }

    def format_response(self, result: any) -> str:
        """Format analysis results."""
        lines = []
        for key, value in result.items():
            lines.append(f"{key}: {value}")
        return "\n".join(lines)

# Example usage
if __name__ == "__main__":
    logger = AgentLogger("code-analyzer", level=LogLevel.INFO)
    analyzer = CodeAnalyzer("analyzer", logger=logger)
    analyzer.initialize()

    sample_code = """
def hello(name):
    if name:
        print(f"Hello, {name}!")
    else:
        print("Hello, World!")

def goodbye():
    print("Goodbye!")
"""

    # Count lines
    result = analyzer.execute("count_lines", code=sample_code)
    print("Line Count:")
    print(analyzer.format_response(result))
    print()

    # Find functions
    result = analyzer.execute("find_functions", code=sample_code)
    print("Functions Found:")
    print(analyzer.format_response(result))
    print()

    # Estimate complexity
    result = analyzer.execute("complexity", code=sample_code)
    print("Complexity:")
    print(analyzer.format_response(result))

    analyzer.cleanup()
```

---

## Working with Tools

Tools make your agents more modular and reusable. Here's how to create and use them:

### Creating a Tool

```python
from agent_framework.tools import Tool

class CalculatorTool(Tool):
    """Tool for basic arithmetic operations."""

    def __init__(self):
        super().__init__(
            name="calculator",
            description="Performs basic arithmetic operations",
            parameters_schema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"]
                    },
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["operation", "a", "b"]
            }
        )

    def execute(self, **kwargs) -> float:
        """Execute the calculation."""
        op = kwargs["operation"]
        a = kwargs["a"]
        b = kwargs["b"]

        if op == "add":
            return a + b
        elif op == "subtract":
            return a - b
        elif op == "multiply":
            return a * b
        elif op == "divide":
            if b == 0:
                raise ValueError("Cannot divide by zero")
            return a / b
```

### Using Tools with Agents

```python
from agent_framework import Agent
from agent_framework.tools import ToolRegistry

class MathAgent(Agent):
    """Agent that performs mathematical operations."""

    def execute(self, task: str, **kwargs) -> any:
        """Execute using available tools."""
        # Use the calculator tool
        if self.has_tool("calculator"):
            return self.execute_tool("calculator", **kwargs)
        else:
            raise RuntimeError("Calculator tool not available")

    def process_context(self, context: dict) -> dict:
        return context

    def format_response(self, result: any) -> str:
        return f"Result: {result}"

# Create agent with tools
registry = ToolRegistry()
calculator = CalculatorTool()
registry.register(calculator)

agent = MathAgent("math-agent", tool_registry=registry)
agent.initialize()

# Perform calculation
result = agent.execute("calculate", operation="add", a=5, b=3)
print(agent.format_response(result))  # Output: Result: 8

agent.cleanup()
```

### Using the @tool Decorator

For automatic registration:

```python
from agent_framework.tools import Tool, ToolRegistry, tool

registry = ToolRegistry()

@tool(
    registry=registry,
    name="greeter",
    description="Generates greeting messages"
)
class GreeterTool(Tool):
    def execute(self, **kwargs) -> str:
        name = kwargs.get("name", "World")
        return f"Hello, {name}!"

# Tool is automatically registered!
print(registry.list_tools())  # Output: ['greeter']
```

---

## Managing Context

The `ContextManager` helps agents maintain awareness across multiple files:

### Basic Context Usage

```python
from agent_framework import Agent
from agent_framework.context import ContextManager

# Create context manager
context = ContextManager(max_files=100)

# Add files
context.add_file(
    "src/main.py",
    content="def main():\n    print('Hello')\n",
    metadata={"language": "python", "size": 1024}
)

context.add_file(
    "src/utils.py",
    content="def helper():\n    pass\n",
    metadata={"language": "python"}
)

# Search for files
results = context.search("main", max_results=5)
print(results)  # Output: ['src/main.py']

# Retrieve file
file_data = context.get_file("src/main.py")
print(file_data["content"])
print(file_data["metadata"])

# Check file existence
if context.has_file("src/main.py"):
    print("File exists!")

# List all files
all_files = context.list_files()
print(all_files)  # Output: ['src/main.py', 'src/utils.py']
```

### Relationship Tracking

The context manager automatically tracks imports and allows explicit relationship management:

```python
# Automatic Python import tracking
context.add_file(
    "app.py",
    content="import utils\nfrom models import User\n"
)

# Get related files
related = context.get_related_files("app.py", max_results=5)
# Returns files that app.py imports

# Add explicit relationships
context.add_relationship(
    "app.py",
    "config.py",
    relationship_type="depends_on"
)

# Get relationships of specific type
relationships = context.get_relationships("app.py")
# Returns: {"imports": [...], "depends_on": ["config.py"]}
```

### Context Window Management

For managing token budgets (e.g., LLM context limits):

```python
# Get files within a token budget
window = context.get_context_window(
    token_limit=4000,
    anchor_file="src/main.py"  # Prioritize this file
)

# Returns list of files that fit within token budget
for file_entry in window:
    print(f"{file_entry['file_path']}: {len(file_entry['content'])} chars")
```

### Agent with Context

```python
from agent_framework import Agent
from agent_framework.context import ContextManager

class CodebaseAgent(Agent):
    """Agent that works with entire codebases."""

    def execute(self, task: str, **kwargs) -> dict:
        """Execute tasks across multiple files."""
        if task == "find_related":
            file_path = kwargs.get("file_path")
            related = self.context_manager.get_related_files(file_path)
            return {"related_files": related}

        elif task == "search":
            query = kwargs.get("query")
            results = self.search_context(query, max_results=10)
            return {"search_results": results}

        return {}

    def process_context(self, context: dict) -> dict:
        return context

    def format_response(self, result: any) -> str:
        return str(result)

# Create agent with context
context_mgr = ContextManager(max_files=100)
agent = CodebaseAgent("codebase-agent", context_manager=context_mgr)
agent.initialize()

# Add files to context
agent.add_context_file("main.py", "import utils\n")
agent.add_context_file("utils.py", "def helper(): pass\n")

# Search context
result = agent.execute("search", query="helper")
print(result)

agent.cleanup()
```

---

## Logging and Debugging

Structured logging helps you understand and debug agent behavior:

### Basic Logging

```python
from agent_framework.logging import AgentLogger, LogLevel, LogFormat

# Create logger with text output
logger = AgentLogger(
    name="my-agent",
    level=LogLevel.DEBUG,
    format=LogFormat.TEXT
)

# Log messages
logger.debug("Debug information", extra_field="value")
logger.info("Agent started")
logger.warning("Potential issue detected")
logger.error("An error occurred", error_code=500)
logger.critical("Critical failure!")

# Get log output
logs = logger.get_logs()
print(logs)
```

### JSON Logging

For structured output that's easy to parse:

```python
from agent_framework.logging import AgentLogger, LogFormat

logger = AgentLogger(
    name="my-agent",
    format=LogFormat.JSON
)

logger.info("User action", user_id=123, action="login")

# Output (JSON):
# {"timestamp": "2024-01-30T...", "level": "INFO", "name": "my-agent",
#  "message": "User action", "user_id": 123, "action": "login"}
```

### Logging with Agents

```python
from agent_framework import Agent
from agent_framework.logging import AgentLogger, LogLevel

logger = AgentLogger("my-agent", level=LogLevel.DEBUG)
agent = MyAgent("agent", logger=logger)

# Agent lifecycle is automatically logged
agent.initialize()  # Logs: "Agent initialized"

# Tool execution is automatically traced
agent.execute_tool("my-tool", param="value")
# Logs: tool name, parameters, execution time, success/failure

# Context operations are logged
agent.add_context_file("file.py", "content")
# Logs: file addition, file path, size

agent.cleanup()  # Logs: "Agent cleanup"

# Review logs
print(logger.get_logs())
```

### Filtering Logs

```python
logger = AgentLogger("my-agent")

# Log with context attributes
logger.info("Task started", task_id="123", user="alice")
logger.info("Task completed", task_id="123", user="alice")
logger.info("Task started", task_id="456", user="bob")

# Filter by attributes
task_123_logs = logger.filter_logs(task_id="123")
# Returns only logs with task_id="123"

alice_logs = logger.filter_logs(user="alice")
# Returns only logs from alice
```

---

## Advanced Topics

### Custom Tool Validation

Implement custom validation logic beyond JSON schema:

```python
from agent_framework.tools import Tool, ValidationError

class CustomTool(Tool):
    def validate_parameters(self, **kwargs):
        # Call parent validation first
        super().validate_parameters(**kwargs)

        # Add custom validation
        value = kwargs.get("value", 0)
        if value < 0:
            raise ValidationError("Value must be non-negative")

    def execute(self, **kwargs):
        value = kwargs["value"]
        return value * 2
```

### Context Search with Boosting

Prioritize certain files in search results:

```python
# Add files with different relevance
context.add_file("important.py", "key functionality", metadata={"priority": "high"})
context.add_file("helper.py", "utility functions", metadata={"priority": "low"})

# Search returns results ordered by relevance
# Files with relationships to anchor file are boosted
results = context.get_related_files("important.py", max_results=10)
```

### Performance Optimization

For large codebases (100+ files):

```python
# Use appropriate max_files limit
context = ContextManager(max_files=1000)

# LRU eviction automatically manages memory
# Frequently accessed files stay in cache

# Use context windows for token budgets
window = context.get_context_window(
    token_limit=8000,
    anchor_file="src/main.py"
)
# Returns prioritized subset within token limit
```

### Combining Tools and Context

Build powerful agents that use both:

```python
class SmartAgent(Agent):
    def execute(self, task: str, **kwargs):
        # Search context for relevant files
        query = kwargs.get("query", "")
        relevant_files = self.search_context(query, max_results=5)

        # Use tool to analyze each file
        results = []
        for file_path in relevant_files:
            file_data = self.get_context_file(file_path)
            analysis = self.execute_tool(
                "analyzer",
                code=file_data["content"]
            )
            results.append({
                "file": file_path,
                "analysis": analysis
            })

        return {"results": results}

    def process_context(self, context: dict):
        return context

    def format_response(self, result: any) -> str:
        return str(result)
```

---

## Best Practices

### 1. Agent Design

- **Single Responsibility**: Each agent should have a clear, focused purpose
- **Implement All Methods**: Always implement `execute()`, `process_context()`, and `format_response()`
- **Use Lifecycle Methods**: Call `initialize()` before use and `cleanup()` when done
- **Validate Inputs**: Check parameters in `process_context()` before execution

### 2. Tool Development

- **Use JSON Schema**: Define clear parameter schemas for validation
- **Handle Errors**: Raise descriptive exceptions when operations fail
- **Keep Tools Focused**: Each tool should do one thing well
- **Document Parameters**: Use clear descriptions in schemas

### 3. Context Management

- **Set Appropriate Limits**: Choose `max_files` based on your use case
- **Use Relationships**: Leverage import tracking and explicit relationships
- **Context Windows**: Use token limits for LLM integration
- **Add Metadata**: Include useful metadata (language, size, priority)

### 4. Logging

- **Use Appropriate Levels**: DEBUG for detailed info, INFO for key events, ERROR for failures
- **Add Context**: Include relevant attributes (user_id, task_id, file_path)
- **Choose Format**: TEXT for human reading, JSON for parsing
- **Review Logs**: Regularly check logs to understand agent behavior

### 5. Performance

- **Benchmark**: Use the included benchmark suite to measure performance
- **Monitor Memory**: Watch context manager size with large codebases
- **Optimize Search**: Use specific queries rather than broad searches
- **Batch Operations**: Add multiple files at once when possible

---

## Troubleshooting

### Common Issues

#### "Tool not found in registry"

**Problem**: Trying to execute a tool that wasn't registered.

**Solution**:
```python
# Ensure tool is registered before use
registry = ToolRegistry()
tool = MyTool()
registry.register(tool)

agent = MyAgent("agent", tool_registry=registry)
```

#### "Agent has no context manager"

**Problem**: Calling context methods without a context manager.

**Solution**:
```python
# Initialize agent with context manager
context = ContextManager()
agent = MyAgent("agent", context_manager=context)
```

#### "Parameter validation failed"

**Problem**: Tool parameters don't match the schema.

**Solution**:
```python
# Check the tool's parameter schema
tool = registry.get_tool("my-tool")
print(tool.parameters_schema)

# Ensure parameters match
result = registry.execute_tool("my-tool", required_param="value")
```

#### "LRU eviction happening too frequently"

**Problem**: Context manager's `max_files` limit is too low.

**Solution**:
```python
# Increase max_files limit
context = ContextManager(max_files=500)  # Increased from default 100
```

#### "Memory usage too high"

**Problem**: Context manager storing too many large files.

**Solution**:
```python
# Reduce max_files or use context windows
context = ContextManager(max_files=100)

# Or use context windows to get subset
window = context.get_context_window(token_limit=4000)
```

### Getting Help

1. **Check API Documentation**: See [API Documentation](api.md) for detailed method signatures
2. **Review Examples**: Look at `examples/` directory for working code
3. **Run Tests**: Execute `pytest tests/ -v` to ensure everything works
4. **Check Benchmarks**: Run `python benchmarks/run_all.py` to validate performance
5. **Enable Debug Logging**: Use `LogLevel.DEBUG` to see detailed execution traces

---

## Next Steps

Now that you understand the basics, you can:

1. **Explore Examples**: Check out `examples/` for more complex use cases
2. **Read Architecture**: See [Architecture Overview](architecture.md) for design details
3. **Review API Docs**: Dive into [API Documentation](api.md) for complete reference
4. **Run Benchmarks**: Execute performance tests to understand framework capabilities
5. **Build Your Agent**: Start implementing your custom agent!

---

## Additional Resources

- [API Documentation](api.md) - Complete API reference
- [Architecture Overview](architecture.md) - Framework design and internals
- [Examples](../examples/) - Working code examples
- [Tests](../tests/) - Comprehensive test suite
- [Benchmarks](../benchmarks/) - Performance benchmarks

Happy building! 🚀
