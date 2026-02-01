"""
Pytest configuration and fixtures for benchmark suite.

This module provides shared fixtures and configuration for all
benchmark tests in the agent framework.
"""

import os
import shutil
import tempfile
import pytest
from typing import Callable, Dict, List, Tuple

from benchmarks.fixtures import generate_test_codebase


@pytest.fixture
def small_codebase():
    """
    Generate a small test codebase (10 files).

    Yields:
        Tuple of (base_dir, file_paths, relationships).
    """
    base_dir, file_paths, relationships = generate_test_codebase(size=10)
    yield base_dir, file_paths, relationships

    # Cleanup
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)


@pytest.fixture
def medium_codebase():
    """
    Generate a medium test codebase (100 files).

    Yields:
        Tuple of (base_dir, file_paths, relationships).
    """
    base_dir, file_paths, relationships = generate_test_codebase(size=100)
    yield base_dir, file_paths, relationships

    # Cleanup
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)


@pytest.fixture
def large_codebase():
    """
    Generate a large test codebase (1000 files).

    Yields:
        Tuple of (base_dir, file_paths, relationships).
    """
    base_dir, file_paths, relationships = generate_test_codebase(size=1000)
    yield base_dir, file_paths, relationships

    # Cleanup
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)


@pytest.fixture
def codebase_generator():
    """
    Provide a factory function for generating custom-sized codebases.

    Returns:
        A function that generates codebases with cleanup tracking.

    Example:
        >>> def test_custom_size(codebase_generator):
        ...     base_dir, files, rels = codebase_generator(size=50)
        ...     assert len(files) == 50
    """
    created_dirs = []

    def _generator(size: int, include_relationships: bool = True):
        base_dir, file_paths, relationships = generate_test_codebase(
            size=size,
            include_relationships=include_relationships
        )
        created_dirs.append(base_dir)
        return base_dir, file_paths, relationships

    yield _generator

    # Cleanup all created directories
    for base_dir in created_dirs:
        if os.path.exists(base_dir):
            shutil.rmtree(base_dir)


@pytest.fixture
def temp_workspace():
    """
    Provide a temporary workspace directory for benchmark tests.

    Yields:
        Path to a temporary directory that will be cleaned up after the test.
    """
    temp_dir = tempfile.mkdtemp(prefix="benchmark_workspace_")
    yield temp_dir

    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def benchmark_context_manager():
    """
    Provide a ContextManager instance for benchmarking.

    Yields:
        A ContextManager instance with default settings.
    """
    from agent_framework.context import ContextManager

    cm = ContextManager(max_files=10000)
    yield cm


@pytest.fixture
def benchmark_logger():
    """
    Provide an AgentLogger instance for benchmarking.

    Yields:
        An AgentLogger instance configured for benchmarks.
    """
    from agent_framework.logging import AgentLogger

    logger = AgentLogger(
        name="benchmark",
        level="INFO",
        output_format="json"
    )
    yield logger


# Benchmark timing utilities
@pytest.fixture
def timer():
    """
    Provide a simple timing utility for benchmarks.

    Returns:
        A function that returns elapsed time in seconds.

    Example:
        >>> def test_timing(timer):
        ...     start = timer()
        ...     # ... do work ...
        ...     elapsed = timer() - start
        ...     assert elapsed < 5.0  # Should complete in under 5 seconds
    """
    import time

    def _timer():
        return time.perf_counter()

    return _timer


@pytest.fixture
def memory_tracker():
    """
    Provide a memory usage tracking utility.

    Returns:
        A function that returns current memory usage in bytes.
        Returns None if psutil is not available.

    Example:
        >>> def test_memory(memory_tracker):
        ...     if memory_tracker is None:
        ...         pytest.skip("psutil not available")
        ...     start_mem = memory_tracker()
        ...     # ... do work ...
        ...     end_mem = memory_tracker()
        ...     memory_used = end_mem - start_mem
        ...     assert memory_used < 100 * 1024 * 1024  # Less than 100MB
    """
    try:
        import psutil
        import os

        def _get_memory_usage():
            process = psutil.Process(os.getpid())
            return process.memory_info().rss

        return _get_memory_usage
    except ImportError:
        # psutil not available, return None
        return None


# Benchmark markers
def pytest_configure(config):
    """Configure custom pytest markers for benchmarks."""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers",
        "benchmark: marks tests as benchmarks"
    )
    config.addinivalue_line(
        "markers",
        "memory: marks tests that measure memory usage"
    )
    config.addinivalue_line(
        "markers",
        "timing: marks tests that measure execution time"
    )
