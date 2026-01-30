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

```python
from agent_framework import Agent

# Example coming soon
```

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

- **Agent Base Class**: Abstract base for creating custom agents
- **Tool System**: Modular tool registration and execution
- **Context Manager**: Multi-file codebase indexing and relationship tracking
- **Logging System**: Structured logging with introspection hooks

## Documentation

- [API Documentation](docs/api.md)
- [User Guide](docs/user_guide.md)
- [Architecture Overview](docs/architecture.md)

## Performance

The framework is designed to meet strict performance requirements:

- Context indexing for 100+ files: < 5 seconds
- Coherent reasoning across 10+ related files
- Efficient memory usage for large codebases

## License

MIT License

## Contributing

Contributions are welcome! Please ensure all tests pass and code is properly formatted before submitting pull requests.
