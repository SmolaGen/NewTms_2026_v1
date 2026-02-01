"""
Benchmark suite for the extensible AI agent framework.

This package provides benchmarking tools to validate performance requirements
for context management, multi-file reasoning, and other framework capabilities.
"""

from benchmarks.fixtures import (
    generate_test_codebase,
    generate_python_file,
    generate_file_with_imports,
)

__all__ = [
    "generate_test_codebase",
    "generate_python_file",
    "generate_file_with_imports",
]
