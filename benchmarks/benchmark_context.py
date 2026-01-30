"""
Benchmark tests for context indexing performance.

This module contains benchmarks to verify that the ContextManager
meets performance requirements:
- 100+ file indexing completes in <5 seconds
- Memory usage is acceptable
- Search operations are efficient
- Relationship tracking performs well
"""

import os
import pytest
from agent_framework.context import ContextManager


@pytest.mark.benchmark
@pytest.mark.timing
def test_small_codebase_indexing(small_codebase, timer):
    """
    Benchmark indexing performance for a small codebase (10 files).

    This establishes a baseline for indexing performance.
    """
    base_dir, file_paths, relationships = small_codebase

    context_manager = ContextManager(max_files=1000)

    start = timer()

    # Index all files
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            content = f.read()
        context_manager.add_file(file_path, content)

    elapsed = timer() - start

    # Verify all files were indexed
    assert len(context_manager) == len(file_paths)

    # Small codebase should index very quickly (< 1 second)
    assert elapsed < 1.0, f"Small codebase indexing took {elapsed:.3f}s (expected <1s)"

    print(f"\n  Small codebase (10 files) indexed in {elapsed:.3f}s")


@pytest.mark.benchmark
@pytest.mark.timing
def test_medium_codebase_indexing(medium_codebase, timer):
    """
    Benchmark indexing performance for a medium codebase (100 files).

    This is the primary acceptance criterion: 100+ files should index in <5 seconds.
    """
    base_dir, file_paths, relationships = medium_codebase

    context_manager = ContextManager(max_files=10000)

    start = timer()

    # Index all files
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            content = f.read()
        context_manager.add_file(file_path, content)

    elapsed = timer() - start

    # Verify all files were indexed
    assert len(context_manager) == len(file_paths)

    # ACCEPTANCE CRITERION: 100+ files must index in <5 seconds
    assert elapsed < 5.0, f"Medium codebase indexing took {elapsed:.3f}s (requirement: <5s)"

    stats = context_manager.get_stats()
    print(f"\n  Medium codebase (100 files) indexed in {elapsed:.3f}s")
    print(f"  Total size: {stats['total_size']:,} bytes")
    print(f"  Average file size: {stats['average_file_size']:.1f} bytes")
    print(f"  Index size: {stats['index_size']:,} tokens")
    print(f"  Relationships tracked: {stats['relationship_count']}")


@pytest.mark.benchmark
@pytest.mark.timing
@pytest.mark.slow
def test_large_codebase_indexing(large_codebase, timer):
    """
    Benchmark indexing performance for a large codebase (1000 files).

    This tests scalability beyond the basic requirement.
    """
    base_dir, file_paths, relationships = large_codebase

    context_manager = ContextManager(max_files=10000)

    start = timer()

    # Index all files
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            content = f.read()
        context_manager.add_file(file_path, content)

    elapsed = timer() - start

    # Verify all files were indexed
    assert len(context_manager) == len(file_paths)

    # Large codebase should still be reasonable (< 60 seconds)
    assert elapsed < 60.0, f"Large codebase indexing took {elapsed:.3f}s (expected <60s)"

    stats = context_manager.get_stats()
    print(f"\n  Large codebase (1000 files) indexed in {elapsed:.3f}s")
    print(f"  Total size: {stats['total_size']:,} bytes")
    print(f"  Average file size: {stats['average_file_size']:.1f} bytes")
    print(f"  Index size: {stats['index_size']:,} tokens")
    print(f"  Relationships tracked: {stats['relationship_count']}")
    print(f"  Throughput: {len(file_paths) / elapsed:.1f} files/second")


@pytest.mark.benchmark
@pytest.mark.memory
def test_medium_codebase_memory_usage(medium_codebase, memory_tracker):
    """
    Benchmark memory usage for indexing 100 files.

    Verifies that memory usage is acceptable (< 100MB for 100 files).
    """
    if memory_tracker is None:
        pytest.skip("psutil not available for memory tracking")

    base_dir, file_paths, relationships = medium_codebase

    # Measure baseline memory
    baseline_memory = memory_tracker()

    context_manager = ContextManager(max_files=10000)

    # Index all files
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            content = f.read()
        context_manager.add_file(file_path, content)

    # Measure memory after indexing
    final_memory = memory_tracker()
    memory_used = final_memory - baseline_memory

    # Verify memory usage is reasonable
    # For 100 files, we expect < 100MB (conservative estimate)
    max_memory_mb = 100
    memory_used_mb = memory_used / (1024 * 1024)

    assert memory_used_mb < max_memory_mb, \
        f"Memory usage {memory_used_mb:.1f}MB exceeds limit of {max_memory_mb}MB"

    stats = context_manager.get_stats()
    print(f"\n  Memory used: {memory_used_mb:.2f}MB for {len(file_paths)} files")
    print(f"  Total content size: {stats['total_size'] / (1024 * 1024):.2f}MB")
    print(f"  Memory overhead: {(memory_used_mb / (stats['total_size'] / (1024 * 1024))) - 1:.1f}x")


@pytest.mark.benchmark
@pytest.mark.timing
def test_search_performance(medium_codebase, timer):
    """
    Benchmark search performance on indexed codebase.

    Verifies that search operations complete quickly even with 100+ files.
    """
    base_dir, file_paths, relationships = medium_codebase

    context_manager = ContextManager(max_files=10000)

    # Index all files
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            content = f.read()
        context_manager.add_file(file_path, content)

    # Perform search benchmarks
    search_queries = [
        "def",        # Common keyword
        "class",      # Common keyword
        "import",     # Common keyword
        "process",    # Function name
        "Manager",    # Class name
    ]

    total_elapsed = 0

    for query in search_queries:
        start = timer()
        results = context_manager.search(query)
        elapsed = timer() - start
        total_elapsed += elapsed

        # Each search should complete very quickly (< 0.1s)
        assert elapsed < 0.1, f"Search for '{query}' took {elapsed:.3f}s (expected <0.1s)"

    avg_elapsed = total_elapsed / len(search_queries)
    print(f"\n  Average search time: {avg_elapsed * 1000:.2f}ms ({len(search_queries)} queries)")
    print(f"  Total search time: {total_elapsed * 1000:.2f}ms")


@pytest.mark.benchmark
@pytest.mark.timing
def test_relationship_tracking_performance(medium_codebase, timer):
    """
    Benchmark relationship tracking and traversal performance.

    Verifies that get_related_files() performs well on a large codebase.
    """
    base_dir, file_paths, relationships = medium_codebase

    context_manager = ContextManager(max_files=10000)

    # Index all files
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            content = f.read()
        context_manager.add_file(file_path, content)

    # Benchmark relationship traversal
    start = timer()

    # Get related files for a sample of files
    sample_size = min(20, len(file_paths))
    import random
    sample_files = random.sample(file_paths, sample_size)

    total_related = 0
    for file_path in sample_files:
        related = context_manager.get_related_files(file_path, max_results=5)
        total_related += len(related)

    elapsed = timer() - start
    avg_elapsed = elapsed / sample_size

    # Each relationship query should be fast (< 0.05s per file)
    assert avg_elapsed < 0.05, \
        f"Average relationship query took {avg_elapsed:.3f}s (expected <0.05s)"

    print(f"\n  Relationship queries: {sample_size} files in {elapsed * 1000:.2f}ms")
    print(f"  Average per query: {avg_elapsed * 1000:.2f}ms")
    print(f"  Total related files found: {total_related}")


@pytest.mark.benchmark
@pytest.mark.timing
def test_context_window_performance(medium_codebase, timer):
    """
    Benchmark context window retrieval performance.

    Verifies that get_context_window() performs well with token limits.
    """
    base_dir, file_paths, relationships = medium_codebase

    context_manager = ContextManager(max_files=10000)

    # Index all files
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            content = f.read()
        context_manager.add_file(file_path, content)

    # Benchmark context window retrieval with different token limits
    token_limits = [1000, 5000, 10000, 50000]

    for token_limit in token_limits:
        start = timer()
        context_window = context_manager.get_context_window(token_limit=token_limit)
        elapsed = timer() - start

        # Context window retrieval should be fast (< 0.2s)
        assert elapsed < 0.2, \
            f"Context window (limit={token_limit}) took {elapsed:.3f}s (expected <0.2s)"

        total_tokens = sum(
            context_manager.estimate_tokens(file_data["content"])
            for file_data in context_window
        )

        print(f"\n  Token limit: {token_limit:,}")
        print(f"    Files selected: {len(context_window)}")
        print(f"    Estimated tokens: {total_tokens:,}")
        print(f"    Retrieval time: {elapsed * 1000:.2f}ms")


@pytest.mark.benchmark
@pytest.mark.timing
def test_incremental_indexing_performance(codebase_generator, timer):
    """
    Benchmark incremental file addition performance.

    Verifies that adding files one-by-one maintains good performance.
    """
    # Generate a medium-sized codebase
    base_dir, file_paths, relationships = codebase_generator(size=100)

    context_manager = ContextManager(max_files=10000)

    # Track per-file indexing time
    indexing_times = []

    for file_path in file_paths:
        with open(file_path, 'r') as f:
            content = f.read()

        start = timer()
        context_manager.add_file(file_path, content)
        elapsed = timer() - start
        indexing_times.append(elapsed)

    # Calculate statistics
    avg_time = sum(indexing_times) / len(indexing_times)
    max_time = max(indexing_times)
    min_time = min(indexing_times)

    # Average per-file indexing should be very fast (< 0.05s)
    assert avg_time < 0.05, \
        f"Average per-file indexing took {avg_time:.3f}s (expected <0.05s)"

    # Even the slowest file should be reasonable (< 0.2s)
    assert max_time < 0.2, \
        f"Maximum per-file indexing took {max_time:.3f}s (expected <0.2s)"

    print(f"\n  Incremental indexing of {len(file_paths)} files:")
    print(f"    Average: {avg_time * 1000:.2f}ms per file")
    print(f"    Min: {min_time * 1000:.2f}ms")
    print(f"    Max: {max_time * 1000:.2f}ms")


@pytest.mark.benchmark
@pytest.mark.timing
def test_lru_eviction_performance(timer):
    """
    Benchmark LRU eviction performance when max_files is exceeded.

    Verifies that eviction doesn't cause performance degradation.
    """
    # Create a small context manager (max 50 files)
    context_manager = ContextManager(max_files=50)

    # Generate content for 100 files
    files_to_add = 100

    start = timer()

    for i in range(files_to_add):
        file_path = f"/test/file_{i}.py"
        content = f"# File {i}\n" + ("def func(): pass\n" * 10)
        context_manager.add_file(file_path, content)

    elapsed = timer() - start

    # Verify only max_files are stored
    assert len(context_manager) == 50

    # Adding files with eviction should still be fast
    avg_time = elapsed / files_to_add
    assert avg_time < 0.01, \
        f"Average per-file time with eviction: {avg_time:.3f}s (expected <0.01s)"

    stats = context_manager.get_stats()
    print(f"\n  LRU eviction test ({files_to_add} files added, max={context_manager.max_files}):")
    print(f"    Total time: {elapsed * 1000:.2f}ms")
    print(f"    Average per file: {avg_time * 1000:.2f}ms")
    print(f"    Files retained: {stats['file_count']}")
    print(f"    Evictions: {files_to_add - stats['file_count']}")


@pytest.mark.benchmark
def test_overall_performance_summary(medium_codebase, timer, memory_tracker):
    """
    Comprehensive performance test that validates all acceptance criteria.

    This test ensures:
    1. 100+ files index in <5 seconds
    2. Memory usage is acceptable
    3. All operations perform well
    """
    base_dir, file_paths, relationships = medium_codebase

    # PHASE 1: Indexing
    context_manager = ContextManager(max_files=10000)

    if memory_tracker:
        baseline_memory = memory_tracker()

    indexing_start = timer()

    for file_path in file_paths:
        with open(file_path, 'r') as f:
            content = f.read()
        context_manager.add_file(file_path, content)

    indexing_time = timer() - indexing_start

    # PHASE 2: Search operations
    search_start = timer()
    search_results = context_manager.search("def")
    search_time = timer() - search_start

    # PHASE 3: Relationship traversal
    rel_start = timer()
    if file_paths:
        related = context_manager.get_related_files(file_paths[0])
    rel_time = timer() - rel_start

    # PHASE 4: Context window
    window_start = timer()
    context_window = context_manager.get_context_window(token_limit=10000)
    window_time = timer() - window_start

    # Collect stats
    stats = context_manager.get_stats()

    # ACCEPTANCE CRITERIA VALIDATION
    assert indexing_time < 5.0, \
        f"FAILED: Indexing {len(file_paths)} files took {indexing_time:.3f}s (requirement: <5s)"

    if memory_tracker:
        final_memory = memory_tracker()
        memory_used_mb = (final_memory - baseline_memory) / (1024 * 1024)
        assert memory_used_mb < 100, \
            f"FAILED: Memory usage {memory_used_mb:.1f}MB exceeds 100MB limit"

    # Print comprehensive summary
    print("\n" + "=" * 70)
    print("  PERFORMANCE BENCHMARK SUMMARY")
    print("=" * 70)
    print(f"\n  Dataset: {len(file_paths)} files, {stats['total_size']:,} bytes")
    print(f"\n  Indexing Performance:")
    print(f"    Time: {indexing_time:.3f}s (requirement: <5s) ✓")
    print(f"    Throughput: {len(file_paths) / indexing_time:.1f} files/second")
    print(f"    Index size: {stats['index_size']:,} tokens")
    print(f"    Relationships: {stats['relationship_count']}")

    if memory_tracker:
        print(f"\n  Memory Usage:")
        print(f"    Total: {memory_used_mb:.2f}MB (requirement: <100MB) ✓")
        print(f"    Content size: {stats['total_size'] / (1024 * 1024):.2f}MB")
        print(f"    Overhead: {(memory_used_mb / (stats['total_size'] / (1024 * 1024))):.2f}x")

    print(f"\n  Operation Performance:")
    print(f"    Search: {search_time * 1000:.2f}ms ({len(search_results)} results)")
    print(f"    Relationship query: {rel_time * 1000:.2f}ms")
    print(f"    Context window: {window_time * 1000:.2f}ms ({len(context_window)} files)")

    print("\n" + "=" * 70)
    print("  ALL ACCEPTANCE CRITERIA MET ✓")
    print("=" * 70 + "\n")
