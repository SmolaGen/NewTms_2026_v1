# API Documentation

This document provides comprehensive API documentation for all public classes and functions in the Extensible AI Agent Framework.

## Table of Contents

- [Agent Module](#agent-module)
  - [Agent](#agent)
- [Tools Module](#tools-module)
  - [Tool](#tool)
  - [ToolRegistry](#toolregistry)
  - [ValidationError](#validationerror)
  - [tool (decorator)](#tool-decorator)
- [Context Module](#context-module)
  - [ContextManager](#contextmanager)
- [Logging Module](#logging-module)
  - [AgentLogger](#agentlogger)
  - [LogLevel](#loglevel)
  - [LogFormat](#logformat)
- [Roadmap Module](#roadmap-module)
  - [RoadmapGenerator](#roadmapgenerator)
  - [Roadmap](#roadmap)
  - [Feature](#feature)
  - [Milestone](#milestone)
  - [Phase](#phase)
  - [MoSCoWPriority](#moscowpriority)
  - [FeatureStatus](#featurestatus)

---

## Agent Module

The `agent` module provides the foundational `Agent` abstract class that all custom agents must inherit from.

### Agent

```python
from agent_framework import Agent
```

Abstract base class for all AI agents in the framework. This class defines the core interface that all agents must implement.

#### Constructor

```python
Agent(
    name: str,
    config: Optional[Dict[str, Any]] = None,
    tool_registry: Optional[ToolRegistry] = None,
    context_manager: Optional[ContextManager] = None,
    logger: Optional[AgentLogger] = None
)
```

**Parameters:**
- `name` (str): A human-readable name for the agent instance
- `config` (Optional[Dict[str, Any]]): Optional configuration dictionary for agent-specific settings
- `tool_registry` (Optional[ToolRegistry]): Optional tool registry for managing agent capabilities
- `context_manager` (Optional[ContextManager]): Optional context manager for multi-file context handling
- `logger` (Optional[AgentLogger]): Optional logger for introspection and debugging

**Attributes:**
- `name` (str): The agent's name
- `config` (Dict[str, Any]): Configuration parameters
- `tool_registry` (Optional[ToolRegistry]): Tool registry instance
- `context_manager` (Optional[ContextManager]): Context manager instance
- `logger` (Optional[AgentLogger]): Logger instance

#### Abstract Methods

These methods **must** be implemented by subclasses:

##### execute

```python
def execute(task: str, **kwargs) -> Any
```

Execute the primary task for this agent. This is the main entry point for agent execution.

**Parameters:**
- `task` (str): The task description or instruction for the agent to execute
- `**kwargs`: Additional keyword arguments specific to the agent type

**Returns:**
- `Any`: The result of the agent's execution (type depends on the agent implementation)

**Raises:**
- `NotImplementedError`: If the subclass doesn't implement this method

##### process_context

```python
def process_context(context: Dict[str, Any]) -> Dict[str, Any]
```

Process and transform context information for the agent. This method handles context preparation, filtering, and transformation.

**Parameters:**
- `context` (Dict[str, Any]): Raw context dictionary containing relevant information

**Returns:**
- `Dict[str, Any]`: Processed context dictionary ready for agent execution

**Raises:**
- `NotImplementedError`: If the subclass doesn't implement this method

##### format_response

```python
def format_response(result: Any) -> str
```

Format the agent's execution result into a human-readable response.

**Parameters:**
- `result` (Any): The raw result from the agent's execution

**Returns:**
- `str`: A formatted string representation of the result

**Raises:**
- `NotImplementedError`: If the subclass doesn't implement this method

#### Methods

##### initialize

```python
def initialize() -> None
```

Initialize the agent and prepare it for execution. This method sets up the agent's state and resources. It should be called before the agent starts executing tasks. The method is idempotent - calling it multiple times has no additional effect after the first call.

Subclasses can override this method to add custom initialization logic, but should call `super().initialize()` to ensure proper base initialization.

**Raises:**
- `RuntimeError`: If initialization fails

##### cleanup

```python
def cleanup() -> None
```

Clean up the agent's resources and reset its state. This method should be called when the agent is no longer needed to ensure proper resource cleanup. It is idempotent - calling it multiple times is safe.

Subclasses can override this method to add custom cleanup logic, but should call `super().cleanup()` to ensure proper base cleanup.

##### register_tool

```python
def register_tool(tool: Tool) -> None
```

Register a tool with the agent's tool registry. This is a convenience method that delegates to the tool registry's register method.

**Parameters:**
- `tool` (Tool): The Tool instance to register

**Raises:**
- `RuntimeError`: If the agent doesn't have a tool registry
- `ValueError`: If a tool with the same name is already registered
- `TypeError`: If the provided object is not a Tool instance

##### has_tool

```python
def has_tool(tool_name: str) -> bool
```

Check if a tool is registered with the agent.

**Parameters:**
- `tool_name` (str): The name of the tool to check

**Returns:**
- `bool`: True if the tool is registered, False otherwise

**Raises:**
- `RuntimeError`: If the agent doesn't have a tool registry

##### get_tool

```python
def get_tool(tool_name: str) -> Tool
```

Get a registered tool by name.

**Parameters:**
- `tool_name` (str): The name of the tool to retrieve

**Returns:**
- `Tool`: The requested tool instance

**Raises:**
- `RuntimeError`: If the agent doesn't have a tool registry
- `KeyError`: If the tool is not found

##### execute_tool

```python
def execute_tool(tool_name: str, **kwargs) -> Any
```

Execute a registered tool by name. This is a convenience method that combines tool retrieval and execution.

**Parameters:**
- `tool_name` (str): The name of the tool to execute
- `**kwargs`: Parameters to pass to the tool's execute method

**Returns:**
- `Any`: The result from the tool's execution

**Raises:**
- `RuntimeError`: If the agent doesn't have a tool registry
- `KeyError`: If the tool is not found
- `ValidationError`: If tool parameters fail validation

##### list_tools

```python
def list_tools() -> List[str]
```

Get a list of all registered tool names.

**Returns:**
- `List[str]`: List of tool names

**Raises:**
- `RuntimeError`: If the agent doesn't have a tool registry

##### add_context

```python
def add_context(file_path: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None
```

Add a file to the agent's context manager. This is a convenience method that delegates to the context manager's add_file method.

**Parameters:**
- `file_path` (str): Path to the file
- `content` (str): The file's content
- `metadata` (Optional[Dict[str, Any]]): Optional metadata about the file

**Raises:**
- `RuntimeError`: If the agent doesn't have a context manager

##### get_context

```python
def get_context(file_path: str) -> Optional[Dict[str, Any]]
```

Retrieve a file from the agent's context manager.

**Parameters:**
- `file_path` (str): Path to the file to retrieve

**Returns:**
- `Optional[Dict[str, Any]]`: File data or None if not found

**Raises:**
- `RuntimeError`: If the agent doesn't have a context manager

##### search_context

```python
def search_context(query: str, max_results: int = 10) -> List[str]
```

Search for files in the context manager.

**Parameters:**
- `query` (str): Search query string
- `max_results` (int): Maximum number of results to return (default: 10)

**Returns:**
- `List[str]`: List of matching file paths

**Raises:**
- `RuntimeError`: If the agent doesn't have a context manager

#### Example Usage

```python
from agent_framework import Agent
from typing import Any, Dict

class MyCustomAgent(Agent):
    """A custom agent implementation."""

    def execute(self, task: str, **kwargs) -> Any:
        # Process the task
        result = f"Processed: {task}"
        return result

    def process_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Filter and transform context
        return {k: v for k, v in context.items() if k.startswith("relevant_")}

    def format_response(self, result: Any) -> str:
        # Format the result for display
        return f"Agent Response: {result}"

# Create and use the agent
agent = MyCustomAgent(name="my-agent")
agent.initialize()
result = agent.execute("Do something useful")
response = agent.format_response(result)
agent.cleanup()
```

---

## Tools Module

The `tools` module provides the `Tool` abstract class and `ToolRegistry` for managing agent capabilities.

### Tool

```python
from agent_framework import Tool
```

Abstract base class for all tools in the framework. Tools are discrete capabilities that agents can use to perform actions.

#### Constructor

```python
Tool(
    name: str,
    description: str,
    parameters_schema: Optional[Dict[str, Any]] = None,
    logger: Optional[AgentLogger] = None
)
```

**Parameters:**
- `name` (str): A unique identifier for the tool
- `description` (str): A human-readable description of what the tool does
- `parameters_schema` (Optional[Dict[str, Any]]): JSON schema defining the expected parameters
- `logger` (Optional[AgentLogger]): Optional logger for tracing tool execution

**Attributes:**
- `name` (str): The tool's unique identifier
- `description` (str): Description of the tool's purpose
- `parameters_schema` (Dict[str, Any]): JSON schema for parameter validation
- `logger` (Optional[AgentLogger]): Logger instance

#### Abstract Methods

##### execute

```python
def execute(**kwargs) -> Any
```

Execute the tool's primary action. This is the main entry point for tool execution.

**Parameters:**
- `**kwargs`: Keyword arguments matching the tool's parameter schema

**Returns:**
- `Any`: The result of the tool's execution (type depends on the tool)

**Raises:**
- `NotImplementedError`: If the subclass doesn't implement this method

#### Methods

##### validate_parameters

```python
def validate_parameters(**kwargs) -> None
```

Validate parameters against the tool's parameter schema.

**Parameters:**
- `**kwargs`: Keyword arguments to validate

**Raises:**
- `ValueError`: If jsonschema library is not available and schema is defined
- `ValidationError`: If parameters don't match the schema

#### Example Usage

```python
from agent_framework import Tool

class CalculatorTool(Tool):
    """A simple calculator tool."""

    def __init__(self):
        schema = {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": ["add", "subtract"]},
                "a": {"type": "number"},
                "b": {"type": "number"}
            },
            "required": ["operation", "a", "b"]
        }
        super().__init__(
            name="calculator",
            description="Performs basic arithmetic operations",
            parameters_schema=schema
        )

    def execute(self, **kwargs) -> float:
        self.validate_parameters(**kwargs)
        op = kwargs["operation"]
        a = kwargs["a"]
        b = kwargs["b"]

        if op == "add":
            return a + b
        elif op == "subtract":
            return a - b

# Use the tool
calc = CalculatorTool()
result = calc.execute(operation="add", a=5, b=3)  # Returns 8
```

### ToolRegistry

```python
from agent_framework import ToolRegistry
```

Registry for managing available tools. The ToolRegistry maintains a collection of tools and provides methods for registration, retrieval, and execution.

#### Constructor

```python
ToolRegistry(logger: Optional[AgentLogger] = None)
```

**Parameters:**
- `logger` (Optional[AgentLogger]): Optional logger for tracing tool registry operations

#### Methods

##### register

```python
def register(tool: Tool) -> None
```

Register a tool in the registry.

**Parameters:**
- `tool` (Tool): The Tool instance to register

**Raises:**
- `ValueError`: If a tool with the same name is already registered
- `TypeError`: If the provided object is not a Tool instance

##### unregister

```python
def unregister(tool_name: str) -> None
```

Remove a tool from the registry.

**Parameters:**
- `tool_name` (str): The name of the tool to remove

**Raises:**
- `KeyError`: If the tool is not found in the registry

##### get

```python
def get(tool_name: str) -> Tool
```

Retrieve a tool by name.

**Parameters:**
- `tool_name` (str): The name of the tool to retrieve

**Returns:**
- `Tool`: The requested tool instance

**Raises:**
- `KeyError`: If the tool is not found

##### has

```python
def has(tool_name: str) -> bool
```

Check if a tool is registered.

**Parameters:**
- `tool_name` (str): The name of the tool to check

**Returns:**
- `bool`: True if the tool is registered, False otherwise

##### list_tools

```python
def list_tools() -> List[str]
```

Get a list of all registered tool names.

**Returns:**
- `List[str]`: List of tool names in registration order

##### execute

```python
def execute(tool_name: str, **kwargs) -> Any
```

Execute a tool by name.

**Parameters:**
- `tool_name` (str): The name of the tool to execute
- `**kwargs`: Parameters to pass to the tool's execute method

**Returns:**
- `Any`: The result from the tool's execution

**Raises:**
- `KeyError`: If the tool is not found
- `ValidationError`: If tool parameters fail validation

##### clear

```python
def clear() -> None
```

Remove all tools from the registry.

##### get_tool_info

```python
def get_tool_info(tool_name: str) -> Dict[str, Any]
```

Get information about a tool.

**Parameters:**
- `tool_name` (str): The name of the tool

**Returns:**
- `Dict[str, Any]`: Dictionary containing tool metadata (name, description, parameters_schema)

**Raises:**
- `KeyError`: If the tool is not found

##### get_all_tool_info

```python
def get_all_tool_info() -> List[Dict[str, Any]]
```

Get information about all registered tools.

**Returns:**
- `List[Dict[str, Any]]`: List of tool metadata dictionaries

#### Example Usage

```python
from agent_framework import ToolRegistry

# Create a registry
registry = ToolRegistry()

# Register tools
registry.register(calculator_tool)
registry.register(file_reader_tool)

# List available tools
tools = registry.list_tools()  # ["calculator", "file_reader"]

# Execute a tool
result = registry.execute("calculator", operation="add", a=10, b=5)

# Get tool information
info = registry.get_tool_info("calculator")
# {"name": "calculator", "description": "...", "parameters_schema": {...}}
```

### ValidationError

```python
from agent_framework import ValidationError
```

Exception raised when tool parameter validation fails. This exception is raised by the `Tool.validate_parameters()` method when parameters don't match the tool's parameter schema.

#### Example

```python
from agent_framework import ValidationError

try:
    tool.execute(invalid_param="value")
except ValidationError as e:
    print(f"Parameter validation failed: {e}")
```

### tool (decorator)

```python
from agent_framework import tool
```

Decorator to convert a function into a Tool instance. This provides a convenient way to create tools from simple functions.

#### Signature

```python
def tool(
    name: str,
    description: str,
    parameters_schema: Optional[Dict[str, Any]] = None,
    logger: Optional[AgentLogger] = None
)
```

**Parameters:**
- `name` (str): Unique identifier for the tool
- `description` (str): Human-readable description
- `parameters_schema` (Optional[Dict[str, Any]]): JSON schema for parameters
- `logger` (Optional[AgentLogger]): Optional logger instance

**Returns:**
- `Callable`: Decorator function that returns a Tool instance

#### Example Usage

```python
from agent_framework import tool

@tool(
    name="greet",
    description="Greets a person by name",
    parameters_schema={
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        },
        "required": ["name"]
    }
)
def greet_tool(name: str) -> str:
    return f"Hello, {name}!"

# The decorator converts the function to a Tool
result = greet_tool.execute(name="Alice")  # "Hello, Alice!"
```

---

## Context Module

The `context` module provides the `ContextManager` class for efficient multi-file context handling and indexing.

### ContextManager

```python
from agent_framework.context import ContextManager
```

Manager for handling multi-file context and relationships. The ContextManager provides efficient storage, retrieval, and indexing of file content for AI agents.

#### Constructor

```python
ContextManager(
    max_files: int = 1000,
    logger: Optional[AgentLogger] = None
)
```

**Parameters:**
- `max_files` (int): Maximum number of files to store in memory (default: 1000). When exceeded, oldest files will be removed (LRU-style)
- `logger` (Optional[AgentLogger]): Optional logger for introspection and debugging

**Attributes:**
- `max_files` (int): Maximum file limit
- `logger` (Optional[AgentLogger]): Logger instance

#### Methods

##### add_file

```python
def add_file(
    file_path: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None
```

Add or update a file in the context manager. This method stores the file content and metadata, updates the search index, and manages the file cache size.

**Parameters:**
- `file_path` (str): Path to the file (used as unique identifier)
- `content` (str): The file's content as a string
- `metadata` (Optional[Dict[str, Any]]): Optional dictionary of additional metadata (e.g., language, size, last_modified)

**Raises:**
- `ValueError`: If file_path is empty or content is None

##### get_file

```python
def get_file(file_path: str) -> Optional[Dict[str, Any]]
```

Retrieve a file's content and metadata.

**Parameters:**
- `file_path` (str): Path to the file to retrieve

**Returns:**
- `Optional[Dict[str, Any]]`: Dictionary containing 'content', 'metadata', and 'size' keys, or None if the file is not found

##### remove_file

```python
def remove_file(file_path: str) -> bool
```

Remove a file from the context manager.

**Parameters:**
- `file_path` (str): Path to the file to remove

**Returns:**
- `bool`: True if the file was removed, False if it wasn't found

##### search

```python
def search(query: str, max_results: int = 10) -> List[str]
```

Search for files containing the query string. This performs a simple token-based search across indexed files. The search is case-insensitive.

**Parameters:**
- `query` (str): The search string to look for
- `max_results` (int): Maximum number of results to return (default: 10)

**Returns:**
- `List[str]`: List of file paths that match the query, ordered by relevance (number of matching tokens)

##### get_related_files

```python
def get_related_files(
    file_path: str,
    relationship_type: Optional[str] = None,
    max_results: int = 10
) -> List[str]
```

Get files related to the specified file.

**Parameters:**
- `file_path` (str): Path to the file
- `relationship_type` (Optional[str]): Type of relationship to filter by (e.g., "import", "imported_by"). If None, returns all related files
- `max_results` (int): Maximum number of results to return (default: 10)

**Returns:**
- `List[str]`: List of related file paths

##### add_relationship

```python
def add_relationship(
    file_path: str,
    related_file: str,
    relationship_type: str
) -> None
```

Manually add a relationship between two files.

**Parameters:**
- `file_path` (str): Source file path
- `related_file` (str): Related file path
- `relationship_type` (str): Type of relationship (e.g., "import", "reference")

**Raises:**
- `ValueError`: If file_path or related_file is empty

##### remove_relationship

```python
def remove_relationship(
    file_path: str,
    related_file: str,
    relationship_type: str
) -> bool
```

Remove a relationship between two files.

**Parameters:**
- `file_path` (str): Source file path
- `related_file` (str): Related file path
- `relationship_type` (str): Type of relationship to remove

**Returns:**
- `bool`: True if the relationship was removed, False if it wasn't found

##### get_all_files

```python
def get_all_files() -> List[str]
```

Get a list of all file paths in the context manager.

**Returns:**
- `List[str]`: List of all file paths, ordered by most recently accessed

##### get_file_count

```python
def get_file_count() -> int
```

Get the number of files currently stored.

**Returns:**
- `int`: Number of files in the context manager

##### clear

```python
def clear() -> None
```

Remove all files from the context manager and reset internal state.

##### get_stats

```python
def get_stats() -> Dict[str, Any]
```

Get statistics about the context manager.

**Returns:**
- `Dict[str, Any]`: Dictionary containing statistics:
  - `file_count` (int): Number of files stored
  - `total_size` (int): Total size of all file contents in bytes
  - `index_size` (int): Number of unique tokens in the search index
  - `relationship_count` (int): Total number of tracked relationships

#### Example Usage

```python
from agent_framework.context import ContextManager

# Create a context manager
context = ContextManager(max_files=100)

# Add files
context.add_file(
    "src/main.py",
    "def main():\n    print('Hello')",
    metadata={"language": "python"}
)

context.add_file(
    "src/utils.py",
    "def helper():\n    pass",
    metadata={"language": "python"}
)

# Search for files
results = context.search("main")  # ["src/main.py"]

# Get file content
file_data = context.get_file("src/main.py")
print(file_data["content"])  # "def main():\n    print('Hello')"

# Get related files
related = context.get_related_files("src/main.py", relationship_type="import")

# Get statistics
stats = context.get_stats()
print(f"Total files: {stats['file_count']}")
```

---

## Logging Module

The `logging` module provides a comprehensive structured logging system with configurable levels, multiple output formats, and filtering capabilities.

### AgentLogger

```python
from agent_framework.logging import AgentLogger
```

Structured logger for AI agents with configurable levels and formats. This logger provides a centralized logging system that supports multiple log levels, output formats (text and JSON), and filtering.

#### Constructor

```python
AgentLogger(
    name: str,
    level: Union[LogLevel, str] = LogLevel.INFO,
    format: Union[LogFormat, str] = LogFormat.TEXT,
    output: Optional[Any] = None
)
```

**Parameters:**
- `name` (str): Name for this logger instance
- `level` (Union[LogLevel, str]): Minimum log level to output (default: LogLevel.INFO). Can be LogLevel enum or string like "INFO"
- `format` (Union[LogFormat, str]): Output format (default: LogFormat.TEXT). Can be LogFormat enum or string like "json"
- `output` (Optional[Any]): Optional output stream (file-like object). If None, uses internal buffer

**Raises:**
- `ValueError`: If level or format string is invalid

**Attributes:**
- `name` (str): The logger's name

#### Methods

##### log

```python
def log(
    level: Union[LogLevel, str],
    message: str,
    **extra
) -> None
```

Log a message at the specified level with optional extra context.

**Parameters:**
- `level` (Union[LogLevel, str]): Log level (LogLevel enum or string)
- `message` (str): The log message
- `**extra`: Additional context as keyword arguments

**Raises:**
- `ValueError`: If level is invalid

##### debug

```python
def debug(message: str, **extra) -> None
```

Log a DEBUG level message.

**Parameters:**
- `message` (str): The log message
- `**extra`: Additional context as keyword arguments

##### info

```python
def info(message: str, **extra) -> None
```

Log an INFO level message.

**Parameters:**
- `message` (str): The log message
- `**extra`: Additional context as keyword arguments

##### warning

```python
def warning(message: str, **extra) -> None
```

Log a WARNING level message.

**Parameters:**
- `message` (str): The log message
- `**extra`: Additional context as keyword arguments

##### error

```python
def error(message: str, **extra) -> None
```

Log an ERROR level message.

**Parameters:**
- `message` (str): The log message
- `**extra`: Additional context as keyword arguments

##### critical

```python
def critical(message: str, **extra) -> None
```

Log a CRITICAL level message.

**Parameters:**
- `message` (str): The log message
- `**extra`: Additional context as keyword arguments

##### set_level

```python
def set_level(level: Union[LogLevel, str]) -> None
```

Set the minimum log level.

**Parameters:**
- `level` (Union[LogLevel, str]): New log level (LogLevel enum or string)

**Raises:**
- `ValueError`: If level is invalid

##### set_format

```python
def set_format(format: Union[LogFormat, str]) -> None
```

Set the output format.

**Parameters:**
- `format` (Union[LogFormat, str]): New format (LogFormat enum or string)

**Raises:**
- `ValueError`: If format is invalid

##### add_filter

```python
def add_filter(key: str, value: Any) -> None
```

Add a filter to only log messages matching certain criteria. Filters are applied as key-value pairs in the extra context.

**Parameters:**
- `key` (str): The context key to filter on
- `value` (Any): The value that must match

##### remove_filter

```python
def remove_filter(key: str) -> None
```

Remove a filter.

**Parameters:**
- `key` (str): The filter key to remove

**Raises:**
- `KeyError`: If the filter key doesn't exist

##### clear_filters

```python
def clear_filters() -> None
```

Remove all filters.

##### get_logs

```python
def get_logs() -> str
```

Get all logs from the internal buffer. This only works if the logger was initialized without a custom output stream.

**Returns:**
- `str`: All logged messages as a string

**Raises:**
- `RuntimeError`: If logger was initialized with a custom output stream

##### clear_logs

```python
def clear_logs() -> None
```

Clear the internal log buffer. This only works if the logger was initialized without a custom output stream.

**Raises:**
- `RuntimeError`: If logger was initialized with a custom output stream

##### get_log_count

```python
def get_log_count() -> int
```

Get the total number of messages logged.

**Returns:**
- `int`: The count of logged messages

#### Example Usage

```python
from agent_framework.logging import AgentLogger, LogLevel, LogFormat

# Create a logger with text format
logger = AgentLogger(
    name="my-agent",
    level=LogLevel.DEBUG,
    format=LogFormat.TEXT
)

# Log messages
logger.info("Agent started", agent_id="123")
logger.debug("Processing context", file_count=10)
logger.error("Failed to load file", file_path="invalid.txt")

# Change log level
logger.set_level(LogLevel.WARNING)

# Add filters
logger.add_filter("component", "tool-execution")
logger.info("This won't show", component="other")
logger.info("This will show", component="tool-execution")

# Get logged messages
logs = logger.get_logs()
print(logs)

# JSON format example
json_logger = AgentLogger(
    name="my-agent",
    level="INFO",
    format="json"
)
json_logger.info("JSON formatted message", action="execute", status="success")
```

### LogLevel

```python
from agent_framework.logging import LogLevel
```

Log level enumeration for structured logging. This enum defines the available log levels.

**Values:**
- `DEBUG` = 10: Detailed diagnostic information
- `INFO` = 20: General informational messages
- `WARNING` = 30: Warning messages for potentially problematic situations
- `ERROR` = 40: Error messages for serious problems
- `CRITICAL` = 50: Critical messages for severe errors

#### Example

```python
from agent_framework.logging import AgentLogger, LogLevel

logger = AgentLogger("my-agent", level=LogLevel.WARNING)
```

### LogFormat

```python
from agent_framework.logging import LogFormat
```

Output format enumeration for log messages. This enum defines the available output formats.

**Values:**
- `TEXT` = "text": Human-readable text format
- `JSON` = "json": Machine-readable JSON format

#### Example

```python
from agent_framework.logging import AgentLogger, LogFormat

# Text format
text_logger = AgentLogger("agent1", format=LogFormat.TEXT)

# JSON format
json_logger = AgentLogger("agent2", format=LogFormat.JSON)
```

---

## Roadmap Module

The `roadmap` module provides the `RoadmapGenerator` agent for creating strategic development roadmaps from codebase analysis, competitive intelligence, and prioritization.

### RoadmapGenerator

```python
from agent_framework.roadmap import RoadmapGenerator
```

An agent that generates strategic roadmaps from codebase analysis. This agent orchestrates multiple components to create comprehensive development roadmaps with feature extraction, MoSCoW prioritization, competitor pain point mapping, milestone generation, and phase organization.

#### Constructor

```python
RoadmapGenerator(
    name: str,
    config: Optional[Dict[str, Any]] = None,
    tool_registry: Optional[ToolRegistry] = None,
    context_manager: Optional[ContextManager] = None,
    logger: Optional[AgentLogger] = None
)
```

**Parameters:**
- `name` (str): A human-readable name for the agent instance
- `config` (Optional[Dict[str, Any]]): Optional configuration dictionary for agent-specific settings
- `tool_registry` (Optional[ToolRegistry]): Optional tool registry for managing agent capabilities
- `context_manager` (Optional[ContextManager]): Optional context manager for multi-file context handling
- `logger` (Optional[AgentLogger]): Optional logger for introspection and debugging

#### Methods

##### generate_roadmap

```python
def generate_roadmap(context: Dict[str, Any] = None) -> Roadmap
```

Generate a complete roadmap from the provided context. This is the main method for creating roadmaps with features, phases, and milestones.

**Parameters:**
- `context` (Optional[Dict[str, Any]]): Optional context dictionary containing:
  - `requirements`: User requirements and priorities
  - `codebase`: Codebase analysis data
  - `competitors`: Competitor information
  - `market`: Market analysis data
  - `constraints`: Technical or business constraints
  - `name`: Roadmap name (default: "Development Roadmap")
  - `description`: Roadmap description

**Returns:**
- `Roadmap`: Complete Roadmap object with features, phases, and milestones (minimum 15 features in 4+ phases)

**Example:**
```python
from agent_framework.roadmap import RoadmapGenerator

# Create generator
rg = RoadmapGenerator(name='roadmap-gen')
rg.initialize()

# Generate basic roadmap
roadmap = rg.generate_roadmap()
print(f"Generated {len(roadmap.features)} features in {len(roadmap.phases)} phases")

# Generate with context
context = {
    "name": "Project Alpha Roadmap",
    "description": "Strategic development plan for Project Alpha",
    "requirements": {
        "feat-custom": {
            "name": "Custom Feature",
            "description": "Project-specific functionality",
            "moscow_priority": "MUST",
            "business_value": 90
        }
    },
    "competitors": [
        {
            "name": "Competitor A",
            "pain_points": [...]
        }
    ]
}

roadmap = rg.generate_roadmap(context)
```

##### analyze_codebase_state

```python
def analyze_codebase_state() -> Dict[str, Any]
```

Analyze the current state of the codebase using the ContextManager. Gathers statistics about files, components, and dependencies.

**Returns:**
- `Dict[str, Any]`: Dictionary with codebase analysis results:
  - `codebase_state['file_count']`: Number of files in context
  - `codebase_state['total_size']`: Total size of all files in bytes
  - `codebase_state['components']`: List of identified components
  - `codebase_state['dependencies']`: List of file dependencies/relationships

**Example:**
```python
from agent_framework.roadmap import RoadmapGenerator
from agent_framework.context import ContextManager

# Create with context manager
context_manager = ContextManager()
rg = RoadmapGenerator(name='rg', context_manager=context_manager)

# Add files to context
context_manager.add_file("src/main.py", "# Main code", {})
context_manager.add_file("src/api.py", "# API code", {})

# Analyze codebase
result = rg.analyze_codebase_state()
print(f"Files: {result['codebase_state']['file_count']}")
print(f"Components: {result['codebase_state']['components']}")
```

##### execute

```python
def execute(task: str, **kwargs) -> Any
```

Execute a specific roadmap generation task. This method allows fine-grained control over individual steps of roadmap generation.

**Parameters:**
- `task` (str): The task type to execute. Supported tasks:
  - `"generate"`: Generate a complete roadmap
  - `"analyze_codebase"`: Analyze current codebase state
  - `"extract_features"`: Extract features from context
  - `"organize_phases"`: Organize features into phases
  - `"map_pain_points"`: Map competitor pain points to features
  - `"create_milestones"`: Create milestones with success metrics
- `**kwargs`: Task-specific parameters

**Returns:**
- `Any`: Task-specific results (Roadmap, dict, list, etc.)

**Example:**
```python
# Extract features only
features = rg.execute("extract_features", context={"requirements": {...}})
print(f"Extracted {len(features)} features")

# Organize into phases
phases = rg.execute("organize_phases", features=features)

# Create milestones
milestones = rg.execute("create_milestones", phases=phases)
```

#### Inherited Methods

RoadmapGenerator inherits all methods from the [Agent](#agent) base class, including:
- `initialize()`, `cleanup()`
- `process_context()`, `format_response()`
- `register_tool()`, `execute_tool()`, `list_tools()`
- `add_context()`, `get_context()`, `search_context()`

#### Example Usage

```python
from agent_framework.roadmap import RoadmapGenerator
from agent_framework.context import ContextManager
from agent_framework.logging import AgentLogger, LogLevel

# Create components
logger = AgentLogger("roadmap-example", level=LogLevel.INFO)
context_manager = ContextManager(max_files=100, logger=logger)

# Create roadmap generator
generator = RoadmapGenerator(
    name="Strategic Roadmap Generator",
    config={"version": "1.0"},
    context_manager=context_manager,
    logger=logger
)

# Initialize
generator.initialize()

# Add codebase files to context
context_manager.add_file(
    "src/main.py",
    "# Main application\nfrom api import create_app",
    metadata={"component": "core"}
)

# Define context with competitive data
context = {
    "name": "Product Roadmap 2024",
    "description": "Strategic development roadmap with competitive positioning",
    "requirements": {
        "feat-ai-search": {
            "name": "AI-Powered Search",
            "description": "Intelligent search with natural language",
            "moscow_priority": "SHOULD",
            "business_value": 85,
            "technical_complexity": 70,
            "estimated_effort_days": 15.0
        }
    },
    "market": {
        "size": "Growing",
        "trends": ["AI integration", "Mobile-first", "Real-time collaboration"]
    }
}

# Generate roadmap
roadmap = generator.generate_roadmap(context)

# Access roadmap components
print(f"Roadmap: {roadmap.name}")
print(f"Features: {len(roadmap.features)}")
print(f"Phases: {len(roadmap.phases)}")
print(f"Milestones: {len(roadmap.milestones)}")

# Examine features by priority
must_haves = roadmap.get_features_by_priority(MoSCoWPriority.MUST)
print(f"Must-have features: {len(must_haves)}")

# Validate dependencies
is_valid = roadmap.validate_dependencies()
has_cycles = roadmap.has_circular_dependencies()
print(f"Dependencies valid: {is_valid}, Has cycles: {has_cycles}")

# Format and display
response = generator.format_response(roadmap)
print(response)

# Cleanup
generator.cleanup()
```

---

### Roadmap

```python
from agent_framework.roadmap_models import Roadmap
```

Main roadmap container organizing features, milestones, and phases into a strategic development plan.

#### Constructor

```python
Roadmap(
    id: str,
    name: str,
    description: str,
    version: str = "1.0.0",
    created_at: datetime = datetime.now(),
    updated_at: datetime = datetime.now(),
    features: List[Feature] = [],
    milestones: List[Milestone] = [],
    phases: List[Phase] = [],
    market_context: Dict[str, Any] = {},
    dependencies: Dict[str, List[str]] = {},
    success_metrics: List[str] = [],
    metadata: Dict[str, Any] = {}
)
```

**Attributes:**
- `id` (str): Unique identifier for the roadmap
- `name` (str): Human-readable roadmap name
- `description` (str): Detailed roadmap description
- `version` (str): Roadmap version string (default: "1.0.0")
- `created_at` (datetime): Roadmap creation timestamp
- `updated_at` (datetime): Last update timestamp
- `features` (List[Feature]): List of all features in the roadmap
- `milestones` (List[Milestone]): List of all milestones
- `phases` (List[Phase]): List of all phases (automatically sorted by order)
- `market_context` (Dict[str, Any]): Context about market and competitive landscape
- `dependencies` (Dict[str, List[str]]): Dependency graph mapping feature relationships
- `success_metrics` (List[str]): Overall roadmap success metrics
- `metadata` (Dict[str, Any]): Additional roadmap metadata

#### Methods

##### get_feature_by_id

```python
def get_feature_by_id(feature_id: str) -> Optional[Feature]
```

Get a feature by its ID.

**Parameters:**
- `feature_id` (str): The feature ID to look up

**Returns:**
- `Optional[Feature]`: The feature if found, None otherwise

##### get_milestone_by_id

```python
def get_milestone_by_id(milestone_id: str) -> Optional[Milestone]
```

Get a milestone by its ID.

**Parameters:**
- `milestone_id` (str): The milestone ID to look up

**Returns:**
- `Optional[Milestone]`: The milestone if found, None otherwise

##### get_phase_by_id

```python
def get_phase_by_id(phase_id: str) -> Optional[Phase]
```

Get a phase by its ID.

**Parameters:**
- `phase_id` (str): The phase ID to look up

**Returns:**
- `Optional[Phase]`: The phase if found, None otherwise

##### get_features_by_priority

```python
def get_features_by_priority(priority: MoSCoWPriority) -> List[Feature]
```

Get all features with a specific MoSCoW priority.

**Parameters:**
- `priority` (MoSCoWPriority): The priority level to filter by

**Returns:**
- `List[Feature]`: List of features matching the priority

##### get_features_by_phase

```python
def get_features_by_phase(phase_id: str) -> List[Feature]
```

Get all features in a specific phase.

**Parameters:**
- `phase_id` (str): The phase ID to filter by

**Returns:**
- `List[Feature]`: List of features in the phase

##### validate_dependencies

```python
def validate_dependencies() -> bool
```

Validate that all feature dependencies are resolvable.

**Returns:**
- `bool`: True if all dependencies are valid, False otherwise

##### has_circular_dependencies

```python
def has_circular_dependencies() -> bool
```

Check if the roadmap has circular dependencies.

**Returns:**
- `bool`: True if circular dependencies exist, False otherwise

#### Example Usage

```python
from agent_framework.roadmap_models import (
    Roadmap, Feature, Phase, Milestone, MoSCoWPriority
)

# Create features
feature1 = Feature(
    id="feat-1",
    name="Core Architecture",
    description="Foundation setup",
    moscow_priority=MoSCoWPriority.MUST,
    priority_rationale="Required for all other features",
    business_value=90,
    technical_complexity=60,
    estimated_effort_days=8.0
)

feature2 = Feature(
    id="feat-2",
    name="User Authentication",
    description="Login system",
    moscow_priority=MoSCoWPriority.MUST,
    priority_rationale="Security requirement",
    business_value=95,
    technical_complexity=50,
    estimated_effort_days=5.0,
    dependencies=["feat-1"]
)

# Create phase
phase1 = Phase(
    id="phase-1",
    name="Foundation",
    description="Core infrastructure",
    order=1,
    features=["feat-1", "feat-2"],
    objectives=["Establish architecture", "Implement security"],
    success_criteria=["All tests passing", "Security audit complete"]
)

# Create milestone
milestone1 = Milestone(
    id="ms-1",
    name="Foundation Complete",
    description="Phase 1 completion",
    success_metrics=["Architecture documented", "Auth system live"],
    features=["feat-1", "feat-2"],
    phase_id="phase-1"
)

# Create roadmap
roadmap = Roadmap(
    id="roadmap-2024",
    name="Product Roadmap 2024",
    description="Strategic development plan",
    features=[feature1, feature2],
    phases=[phase1],
    milestones=[milestone1]
)

# Query roadmap
must_features = roadmap.get_features_by_priority(MoSCoWPriority.MUST)
phase_features = roadmap.get_features_by_phase("phase-1")

# Validate
is_valid = roadmap.validate_dependencies()  # True
has_cycles = roadmap.has_circular_dependencies()  # False
```

---

### Feature

```python
from agent_framework.roadmap_models import Feature
```

Represents a feature in the development roadmap with prioritization, effort estimation, and success metrics.

#### Constructor

```python
Feature(
    id: str,
    name: str,
    description: str,
    moscow_priority: MoSCoWPriority,
    priority_rationale: str,
    business_value: int = 0,
    technical_complexity: int = 0,
    estimated_effort_days: float = 0.0,
    dependencies: List[str] = [],
    competitor_pain_points: List[str] = [],
    success_metrics: List[str] = [],
    status: FeatureStatus = FeatureStatus.PROPOSED,
    phase_id: Optional[str] = None,
    metadata: Dict[str, Any] = {}
)
```

**Attributes:**
- `id` (str): Unique identifier for the feature
- `name` (str): Human-readable feature name
- `description` (str): Detailed feature description
- `moscow_priority` (MoSCoWPriority): MoSCoW prioritization category
- `priority_rationale` (str): Explanation for the prioritization decision
- `business_value` (int): Business value score (0-100)
- `technical_complexity` (int): Technical complexity score (0-100)
- `estimated_effort_days` (float): Estimated effort in person-days
- `dependencies` (List[str]): List of feature IDs this feature depends on
- `competitor_pain_points` (List[str]): List of competitor pain point IDs this addresses
- `success_metrics` (List[str]): List of measurable success criteria
- `status` (FeatureStatus): Current implementation status
- `phase_id` (Optional[str]): ID of the phase this feature belongs to
- `metadata` (Dict[str, Any]): Additional feature metadata

**Validation:**
- `business_value` must be between 0 and 100
- `technical_complexity` must be between 0 and 100
- `estimated_effort_days` must be non-negative

#### Example Usage

```python
from agent_framework.roadmap_models import Feature, MoSCoWPriority, FeatureStatus

# Create a feature
feature = Feature(
    id="feat-api-gateway",
    name="API Gateway",
    description="Centralized API gateway with rate limiting and authentication",
    moscow_priority=MoSCoWPriority.MUST,
    priority_rationale="Required for scalable microservices architecture",
    business_value=85,
    technical_complexity=65,
    estimated_effort_days=12.0,
    dependencies=["feat-auth-service"],
    competitor_pain_points=["pain-slow-api", "pain-no-rate-limiting"],
    success_metrics=[
        "Handle 1000+ req/sec",
        "Response time <100ms",
        "99.9% uptime"
    ],
    status=FeatureStatus.PLANNED,
    metadata={"team": "platform", "sprint": 3}
)

# Access properties
print(f"Feature: {feature.name}")
print(f"Priority: {feature.moscow_priority.value}")
print(f"Business Value: {feature.business_value}/100")
print(f"Effort: {feature.estimated_effort_days} days")
print(f"Dependencies: {len(feature.dependencies)}")
```

---

### Milestone

```python
from agent_framework.roadmap_models import Milestone
```

Represents a milestone in the development roadmap with success metrics and feature tracking.

#### Constructor

```python
Milestone(
    id: str,
    name: str,
    description: str,
    target_date: Optional[datetime] = None,
    success_metrics: List[str] = [],
    features: List[str] = [],
    phase_id: Optional[str] = None,
    is_completed: bool = False,
    completed_date: Optional[datetime] = None,
    metadata: Dict[str, Any] = {}
)
```

**Attributes:**
- `id` (str): Unique identifier for the milestone
- `name` (str): Human-readable milestone name
- `description` (str): Detailed milestone description
- `target_date` (Optional[datetime]): Target completion date
- `success_metrics` (List[str]): List of measurable criteria for milestone completion (required, minimum 1)
- `features` (List[str]): List of feature IDs included in this milestone
- `phase_id` (Optional[str]): ID of the phase this milestone belongs to
- `is_completed` (bool): Whether the milestone has been achieved
- `completed_date` (Optional[datetime]): Actual completion date (required if is_completed is True)
- `metadata` (Dict[str, Any]): Additional milestone metadata

**Validation:**
- Must have at least one success metric
- If `is_completed` is True, `completed_date` must be set

#### Example Usage

```python
from agent_framework.roadmap_models import Milestone
from datetime import datetime, timedelta

# Create a milestone
milestone = Milestone(
    id="ms-mvp",
    name="MVP Launch",
    description="Minimum viable product ready for beta users",
    target_date=datetime.now() + timedelta(days=90),
    success_metrics=[
        "All core features deployed",
        "Load testing passed",
        "Security audit complete",
        "Beta user signups >100"
    ],
    features=["feat-1", "feat-2", "feat-3"],
    phase_id="phase-1",
    is_completed=False,
    metadata={"priority": "critical", "team": "product"}
)

# Track completion
if milestone.is_completed:
    print(f"Completed on: {milestone.completed_date}")
else:
    days_remaining = (milestone.target_date - datetime.now()).days
    print(f"Due in {days_remaining} days")
```

---

### Phase

```python
from agent_framework.roadmap_models import Phase
```

Represents a development phase containing related features and milestones.

#### Constructor

```python
Phase(
    id: str,
    name: str,
    description: str,
    order: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    features: List[str] = [],
    milestones: List[str] = [],
    objectives: List[str] = [],
    success_criteria: List[str] = [],
    status: str = "planned",
    metadata: Dict[str, Any] = {}
)
```

**Attributes:**
- `id` (str): Unique identifier for the phase
- `name` (str): Human-readable phase name
- `description` (str): Detailed phase description
- `order` (int): Sequential order of this phase (0-indexed)
- `start_date` (Optional[datetime]): Planned start date
- `end_date` (Optional[datetime]): Planned end date
- `features` (List[str]): List of feature IDs in this phase
- `milestones` (List[str]): List of milestone IDs in this phase
- `objectives` (List[str]): List of phase objectives
- `success_criteria` (List[str]): List of criteria for phase completion
- `status` (str): Current phase status (e.g., "planned", "in_progress", "completed")
- `metadata` (Dict[str, Any]): Additional phase metadata

**Validation:**
- `order` must be non-negative
- If both `start_date` and `end_date` are set, start must be before end

#### Example Usage

```python
from agent_framework.roadmap_models import Phase
from datetime import datetime, timedelta

# Create a phase
phase = Phase(
    id="phase-foundation",
    name="Foundation",
    description="Core infrastructure and architecture setup",
    order=1,
    start_date=datetime.now(),
    end_date=datetime.now() + timedelta(days=60),
    features=["feat-arch", "feat-auth", "feat-db"],
    milestones=["ms-arch-complete"],
    objectives=[
        "Establish core architecture patterns",
        "Set up development infrastructure",
        "Implement security fundamentals"
    ],
    success_criteria=[
        "Architecture documented and reviewed",
        "All foundational tests passing",
        "Security audit passed"
    ],
    status="in_progress",
    metadata={"lead": "architect-team", "budget": 50000}
)

print(f"Phase {phase.order}: {phase.name}")
print(f"Features: {len(phase.features)}")
print(f"Duration: {(phase.end_date - phase.start_date).days} days")
```

---

### MoSCoWPriority

```python
from agent_framework.roadmap_models import MoSCoWPriority
```

MoSCoW prioritization enumeration for features. This enum defines the four categories of the MoSCoW prioritization method.

**Values:**
- `MUST`: Critical features that must be delivered for success
- `SHOULD`: Important features that should be included if possible
- `COULD`: Desirable features that could be included if resources permit
- `WONT`: Features that won't be delivered in this iteration but may be considered later

#### Example

```python
from agent_framework.roadmap_models import Feature, MoSCoWPriority

# Create features with different priorities
critical_feature = Feature(
    id="feat-1",
    name="User Authentication",
    description="Secure login system",
    moscow_priority=MoSCoWPriority.MUST,
    priority_rationale="Security requirement",
    business_value=95,
    technical_complexity=50,
    estimated_effort_days=5.0
)

nice_to_have = Feature(
    id="feat-2",
    name="Dark Mode",
    description="UI theme toggle",
    moscow_priority=MoSCoWPriority.COULD,
    priority_rationale="User preference, not critical for MVP",
    business_value=40,
    technical_complexity=30,
    estimated_effort_days=2.0
)

# Filter by priority
features = [critical_feature, nice_to_have]
must_haves = [f for f in features if f.moscow_priority == MoSCoWPriority.MUST]
```

---

### FeatureStatus

```python
from agent_framework.roadmap_models import FeatureStatus
```

Feature implementation status enumeration. This enum tracks the current state of feature development.

**Values:**
- `PROPOSED`: Feature has been proposed but not yet planned
- `PLANNED`: Feature is planned for implementation
- `IN_PROGRESS`: Feature is currently being implemented
- `COMPLETED`: Feature implementation is complete
- `CANCELLED`: Feature has been cancelled and won't be implemented

#### Example

```python
from agent_framework.roadmap_models import Feature, FeatureStatus, MoSCoWPriority

# Track feature lifecycle
feature = Feature(
    id="feat-notifications",
    name="Push Notifications",
    description="Real-time push notification system",
    moscow_priority=MoSCoWPriority.SHOULD,
    priority_rationale="Improves user engagement",
    business_value=70,
    technical_complexity=60,
    estimated_effort_days=8.0,
    status=FeatureStatus.PROPOSED
)

# Update status as work progresses
feature.status = FeatureStatus.PLANNED
print(f"Feature planned: {feature.name}")

feature.status = FeatureStatus.IN_PROGRESS
print(f"Implementation started: {feature.name}")

feature.status = FeatureStatus.COMPLETED
print(f"Feature complete: {feature.name}")

# Check status
if feature.status == FeatureStatus.COMPLETED:
    print("Ready for deployment")
```

---

## Common Patterns

### Creating a Complete Agent System

```python
from agent_framework import Agent, ToolRegistry, ValidationError
from agent_framework.context import ContextManager
from agent_framework.logging import AgentLogger, LogLevel
from typing import Any, Dict

# Create components
logger = AgentLogger("my-system", level=LogLevel.DEBUG)
tool_registry = ToolRegistry(logger=logger)
context_manager = ContextManager(max_files=500, logger=logger)

# Register tools
tool_registry.register(my_calculator_tool)
tool_registry.register(my_file_reader_tool)

# Add context
context_manager.add_file(
    "src/main.py",
    file_content,
    metadata={"language": "python", "type": "source"}
)

# Create custom agent
class MyAgent(Agent):
    def execute(self, task: str, **kwargs) -> Any:
        self._log("info", f"Executing task: {task}")

        # Use tools
        result = self.execute_tool("calculator", operation="add", a=1, b=2)

        # Use context
        files = self.search_context("import")

        return result

    def process_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return context

    def format_response(self, result: Any) -> str:
        return f"Result: {result}"

# Initialize agent with components
agent = MyAgent(
    name="my-agent",
    config={"max_iterations": 10},
    tool_registry=tool_registry,
    context_manager=context_manager,
    logger=logger
)

# Use the agent
agent.initialize()
try:
    result = agent.execute("Process data")
    response = agent.format_response(result)
    print(response)
finally:
    agent.cleanup()

# Review logs
print(logger.get_logs())
```

### Strategic Roadmap Generation

```python
from agent_framework.roadmap import RoadmapGenerator
from agent_framework.roadmap_models import (
    Roadmap, Feature, MoSCoWPriority, FeatureStatus
)
from agent_framework.context import ContextManager
from agent_framework.logging import AgentLogger, LogLevel

# Set up components
logger = AgentLogger("roadmap-system", level=LogLevel.INFO)
context_manager = ContextManager(max_files=500, logger=logger)

# Add codebase files for analysis
context_manager.add_file(
    "src/api/main.py",
    "# Main API entry point\nfrom fastapi import FastAPI\napp = FastAPI()",
    metadata={"component": "api", "language": "python"}
)
context_manager.add_file(
    "src/database/models.py",
    "# Database models\nfrom sqlalchemy import Column, Integer, String",
    metadata={"component": "database", "language": "python"}
)

# Create roadmap generator
generator = RoadmapGenerator(
    name="Product Roadmap Generator",
    config={"version": "2024.1"},
    context_manager=context_manager,
    logger=logger
)

generator.initialize()

# Define comprehensive context
context = {
    "name": "Product Development Roadmap 2024",
    "description": "Strategic roadmap for next-gen product platform",
    "requirements": {
        "feat-realtime-collab": {
            "name": "Real-time Collaboration",
            "description": "Multi-user real-time editing and commenting",
            "moscow_priority": "MUST",
            "priority_rationale": "Key differentiator from competitors",
            "business_value": 92,
            "technical_complexity": 75,
            "estimated_effort_days": 18.0,
            "success_metrics": [
                "Support 50+ concurrent users per document",
                "Conflict resolution <100ms",
                "Zero data loss in collaboration"
            ]
        },
        "feat-ai-assistant": {
            "name": "AI Writing Assistant",
            "description": "AI-powered content suggestions and auto-complete",
            "moscow_priority": "SHOULD",
            "priority_rationale": "High user demand, competitive advantage",
            "business_value": 88,
            "technical_complexity": 85,
            "estimated_effort_days": 25.0,
            "dependencies": ["feat-core-architecture"],
            "success_metrics": [
                "95% suggestion accuracy",
                "Responses <500ms",
                "User adoption >60%"
            ]
        }
    },
    "competitors": [
        {
            "name": "Competitor X",
            "pain_points": [
                {
                    "id": "pain-slow-sync",
                    "name": "Slow Synchronization",
                    "description": "Users report slow sync across devices",
                    "severity": "HIGH",
                    "frequency": "VERY_COMMON",
                    "potential_solution": "Real-time collaboration and instant sync"
                }
            ]
        }
    ],
    "market": {
        "size": "Growing - 25% YoY",
        "trends": ["AI integration", "Real-time collaboration", "Mobile-first"],
        "target_segment": "SMB and Enterprise teams"
    }
}

# Generate complete roadmap
roadmap = generator.generate_roadmap(context)

# Analyze the roadmap
print(f"\nRoadmap: {roadmap.name}")
print(f"Total Features: {len(roadmap.features)}")
print(f"Phases: {len(roadmap.phases)}")
print(f"Milestones: {len(roadmap.milestones)}")

# Examine features by priority
must_haves = roadmap.get_features_by_priority(MoSCoWPriority.MUST)
should_haves = roadmap.get_features_by_priority(MoSCoWPriority.SHOULD)
could_haves = roadmap.get_features_by_priority(MoSCoWPriority.COULD)

print(f"\nPriority Breakdown:")
print(f"  MUST: {len(must_haves)} features")
print(f"  SHOULD: {len(should_haves)} features")
print(f"  COULD: {len(could_haves)} features")

# Examine phases
print(f"\nPhase Overview:")
for phase in roadmap.phases:
    phase_features = roadmap.get_features_by_phase(phase.id)
    total_effort = sum(f.estimated_effort_days for f in phase_features)
    print(f"  Phase {phase.order}: {phase.name}")
    print(f"    Features: {len(phase_features)}")
    print(f"    Total Effort: {total_effort} person-days")
    print(f"    Objectives: {len(phase.objectives)}")

# Check milestones
print(f"\nMilestones:")
for milestone in roadmap.milestones:
    print(f"  {milestone.name}")
    print(f"    Features: {len(milestone.features)}")
    print(f"    Success Metrics: {len(milestone.success_metrics)}")
    if milestone.success_metrics:
        print(f"      - {milestone.success_metrics[0]}")

# Validate roadmap integrity
print(f"\nValidation:")
deps_valid = roadmap.validate_dependencies()
has_cycles = roadmap.has_circular_dependencies()
print(f"  Dependencies valid: {deps_valid}")
print(f"  Circular dependencies: {has_cycles}")

# Find features addressing competitor pain points
features_with_pain_points = [
    f for f in roadmap.features if f.competitor_pain_points
]
print(f"  Features addressing pain points: {len(features_with_pain_points)}")

# Calculate total effort
total_effort = sum(f.estimated_effort_days for f in roadmap.features)
print(f"  Total estimated effort: {total_effort} person-days")

# Get specific feature details
realtime_feature = roadmap.get_feature_by_id("feat-realtime-collab")
if realtime_feature:
    print(f"\nFeatured: {realtime_feature.name}")
    print(f"  Priority: {realtime_feature.moscow_priority.value}")
    print(f"  Business Value: {realtime_feature.business_value}/100")
    print(f"  Complexity: {realtime_feature.technical_complexity}/100")
    print(f"  Effort: {realtime_feature.estimated_effort_days} days")
    print(f"  Success Metrics: {len(realtime_feature.success_metrics)}")

# Clean up
generator.cleanup()
print("\nRoadmap generation complete!")
```

### Error Handling

```python
from agent_framework import ValidationError

try:
    # Execute with validation
    tool.execute(invalid_param="value")
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
except KeyError as e:
    logger.error(f"Tool not found: {e}")
except RuntimeError as e:
    logger.error(f"Runtime error: {e}")
```

---

## See Also

- [User Guide](user_guide.md) - Step-by-step guide for using the framework
- [Architecture Overview](architecture.md) - Detailed architecture documentation
- [README](../README.md) - Project overview and quick start
