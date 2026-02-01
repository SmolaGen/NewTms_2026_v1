# Extensible AI Agent Framework

Core framework for building reliable AI agents with proper abstractions, context management, and tool integration capabilities.

## Overview

This framework addresses fundamental limitations that competitors (GitHub Copilot, Cursor, Windsurf) struggle with - inconsistent code quality and limited context awareness. A solid framework foundation enables superior multi-file context handling and reduces hallucinations.

## Features

- **Custom Agent Types**: Build specialized AI agents with modular tool system
- **Context Management**: Efficiently handle multi-file codebases (100+ files)
- **Coherent Reasoning**: Maintain context across 10+ related files
- **Comprehensive Logging**: Built-in introspection and debugging capabilities
- **Performance Optimized**: Benchmarked for context processing efficiency

## Installation

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Quick Start

Here's a simple example to get you started:

```python
from agent_framework import Agent
from agent_framework.logging import AgentLogger

class SimpleAgent(Agent):
    """A simple text processing agent."""

    def execute(self, task: str, **kwargs) -> dict:
        """Execute a task."""
        text = kwargs.get("text", "")

        if task == "count_words":
            return {"word_count": len(text.split())}
        elif task == "uppercase":
            return {"result": text.upper()}

        return {"error": f"Unknown task: {task}"}

    def process_context(self, context: dict) -> dict:
        """Process context information."""
        return {"text": context.get("text", "")}

    def format_response(self, result: any) -> str:
        """Format the result."""
        return str(result)

# Create and use the agent
logger = AgentLogger("simple-agent")
agent = SimpleAgent("my-agent", logger=logger)
agent.initialize()

result = agent.execute("count_words", text="Hello World")
print(agent.format_response(result))  # {"word_count": 2}

agent.cleanup()
```

For more examples, see the [examples/](examples/) directory.

## Requirements

- Python 3.8 or higher

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Coverage

```bash
pytest tests/ --cov=src/agent_framework --cov-report=term-missing
```

### Code Formatting

```bash
black src/ tests/
```

## Architecture

The framework consists of several core components:

- **Agent Base Class**: Abstract base for creating custom agents with a clean interface
- **Tool System**: Modular tool registration and execution with parameter validation
- **Context Manager**: Multi-file codebase indexing with relationship tracking and LRU eviction
- **Logging System**: Structured logging with multiple formats (text/JSON) and introspection hooks

Each component is designed to be:
- **Independent**: Can be used separately or combined as needed
- **Extensible**: Easy to subclass and customize
- **Observable**: Comprehensive logging throughout
- **Performant**: Optimized for efficiency with large codebases

See [Architecture Overview](docs/architecture.md) for detailed design documentation.

## Documentation

### Getting Started
- **[User Guide](docs/user_guide.md)** - Complete guide to using the framework, including examples and best practices
- **[Quick Start Examples](examples/)** - Working code examples for common use cases

### Reference
- **[API Documentation](docs/api.md)** - Comprehensive API reference for all classes and methods
- **[Architecture Overview](docs/architecture.md)** - Design philosophy, implementation details, and internals

### Advanced
- **[Benchmarks](benchmarks/)** - Performance benchmarks and validation suite
- **[Tests](tests/)** - Comprehensive test suite with examples of usage patterns

## Performance

The framework is designed to meet strict performance requirements and has been validated through comprehensive benchmarking:

- **Context Indexing**: Handle 100+ files in < 5 seconds
- **Multi-File Reasoning**: Maintain coherence across 10+ related files
- **Memory Efficiency**: LRU eviction and configurable limits for large codebases
- **Search Performance**: Token-based indexing for fast file search (<10ms)
- **Context Windows**: Generate prioritized file subsets within token budgets (<50ms)

Run the benchmarks yourself:

```bash
python benchmarks/run_all.py
```

Results are generated in `benchmarks/results.json` and `benchmarks/results.md`.

## License

MIT License

## Contributing

Contributions are welcome! Please ensure all tests pass and code is properly formatted before submitting pull requests.
