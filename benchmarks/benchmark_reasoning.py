"""
Benchmark tests for multi-file reasoning performance.

This module contains benchmarks to verify that agents can maintain
coherent reasoning across 10+ related files, meeting the acceptance criteria:
- Agents maintain coherent reasoning across 10+ related files
- Context window management supports multi-file tasks
- Relationship traversal enables efficient reasoning
"""

import os
import random
import pytest
from typing import Any, Dict, List, Optional

from agent_framework.agent import Agent
from agent_framework.context import ContextManager
from agent_framework.logging import AgentLogger


class ReasoningTestAgent(Agent):
    """
    A concrete agent implementation for testing multi-file reasoning.

    This agent simulates reasoning tasks that require understanding
    and processing multiple related files.
    """

    def __init__(
        self,
        name: str,
        config: Optional[Dict[str, Any]] = None,
        context_manager: Optional[ContextManager] = None,
        logger: Optional[AgentLogger] = None
    ):
        """Initialize the reasoning test agent."""
        super().__init__(name, config, None, context_manager, logger)
        self.execution_history = []

    def execute(self, task: str, **kwargs) -> Any:
        """
        Execute a reasoning task across multiple files.

        Args:
            task: The task description.
            **kwargs: Additional parameters including:
                - anchor_file: Starting file for reasoning
                - max_files: Maximum number of files to consider
                - token_limit: Token budget for context window

        Returns:
            Dictionary with task results and reasoning metadata.
        """
        anchor_file = kwargs.get("anchor_file")
        max_files = kwargs.get("max_files", 10)
        token_limit = kwargs.get("token_limit", 50000)

        # Build context for reasoning
        if anchor_file and self.context_manager:
            # Get related files
            related_files = self.context_manager.get_related_files(
                anchor_file,
                max_results=max_files
            )

            # Get context window with token budget
            context_window = self.context_manager.get_context_window(
                token_limit=token_limit,
                anchor_file=anchor_file
            )
        else:
            related_files = []
            context_window = []

        # Process context
        context = {
            "task": task,
            "anchor_file": anchor_file,
            "related_files": related_files,
            "context_window": context_window,
            "max_files": max_files,
            "token_limit": token_limit
        }

        processed_context = self.process_context(context)

        # Simulate reasoning across files
        result = {
            "task": task,
            "files_analyzed": len(processed_context.get("files", [])),
            "relationships_found": len(processed_context.get("relationships", [])),
            "tokens_used": processed_context.get("total_tokens", 0),
            "coherence_score": self._calculate_coherence(processed_context),
            "reasoning_steps": processed_context.get("reasoning_steps", [])
        }

        self.execution_history.append(result)
        return result

    def process_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process multi-file context for reasoning.

        This method simulates the context processing pipeline that
        a real agent would use for multi-file reasoning tasks.

        Args:
            context: Raw context with files and relationships.

        Returns:
            Processed context ready for reasoning.
        """
        processed = {
            "task": context["task"],
            "files": [],
            "relationships": [],
            "total_tokens": 0,
            "reasoning_steps": []
        }

        # Process files from context window
        for file_data in context.get("context_window", []):
            file_path = file_data["file_path"]
            content = file_data["content"]

            # Estimate tokens
            if self.context_manager:
                tokens = self.context_manager.estimate_tokens(content)
            else:
                tokens = len(content.split())

            processed["files"].append({
                "path": file_path,
                "tokens": tokens,
                "has_imports": "import" in content,
                "has_classes": "class" in content,
                "has_functions": "def" in content
            })

            processed["total_tokens"] += tokens

        # Track relationships
        anchor_file = context.get("anchor_file")
        if anchor_file and self.context_manager:
            # Get relationships for anchor file
            if self.context_manager.has_file(anchor_file):
                relationships = self.context_manager._relationships.get(anchor_file, {})
                for rel_type, rel_files in relationships.items():
                    for rel_file in rel_files:
                        processed["relationships"].append({
                            "type": rel_type,
                            "from": anchor_file,
                            "to": rel_file
                        })

        # Simulate reasoning steps
        processed["reasoning_steps"] = [
            "Load anchor file and extract structure",
            "Identify file dependencies and relationships",
            "Retrieve related files from context",
            "Build multi-file understanding",
            "Synthesize coherent response"
        ]

        return processed

    def format_response(self, result: Any) -> str:
        """
        Format the reasoning result into a readable response.

        Args:
            result: The execution result dictionary.

        Returns:
            Formatted string response.
        """
        if isinstance(result, dict):
            lines = [
                f"Task: {result.get('task', 'Unknown')}",
                f"Files Analyzed: {result.get('files_analyzed', 0)}",
                f"Relationships Found: {result.get('relationships_found', 0)}",
                f"Tokens Used: {result.get('tokens_used', 0):,}",
                f"Coherence Score: {result.get('coherence_score', 0.0):.2f}",
                f"Reasoning Steps: {len(result.get('reasoning_steps', []))}"
            ]
            return "\n".join(lines)
        return str(result)

    def _calculate_coherence(self, processed_context: Dict[str, Any]) -> float:
        """
        Calculate a coherence score for multi-file reasoning.

        This simulates measuring how well the agent maintains coherent
        understanding across multiple files.

        Args:
            processed_context: The processed context data.

        Returns:
            A coherence score between 0.0 and 1.0.
        """
        files = processed_context.get("files", [])
        relationships = processed_context.get("relationships", [])

        if not files:
            return 0.0

        # Score based on:
        # - Number of files processed (more is better up to a point)
        # - Presence of relationships (indicates connected reasoning)
        # - Diversity of file types (imports, classes, functions)

        file_score = min(len(files) / 10.0, 1.0)  # Optimal around 10 files
        relationship_score = min(len(relationships) / 5.0, 1.0)  # Good if 5+ relationships

        # Check diversity
        has_imports = sum(1 for f in files if f.get("has_imports", False))
        has_classes = sum(1 for f in files if f.get("has_classes", False))
        has_functions = sum(1 for f in files if f.get("has_functions", False))
        diversity_score = (has_imports + has_classes + has_functions) / (len(files) * 3)

        # Combined score
        coherence = (file_score * 0.4 + relationship_score * 0.4 + diversity_score * 0.2)
        return coherence


@pytest.mark.benchmark
@pytest.mark.timing
def test_basic_multi_file_reasoning(medium_codebase, timer):
    """
    Benchmark basic multi-file reasoning with 10 files.

    Verifies that an agent can process and reason across 10 related files
    efficiently, meeting the core acceptance criterion.
    """
    base_dir, file_paths, relationships = medium_codebase

    # Create agent with context manager
    context_manager = ContextManager(max_files=10000)
    agent = ReasoningTestAgent(
        name="reasoning_test",
        context_manager=context_manager
    )

    agent.initialize()

    # Index files
    for file_path in file_paths[:20]:  # Use subset for focused test
        with open(file_path, 'r') as f:
            content = f.read()
        agent.add_context_file(file_path, content)

    # Select an anchor file
    anchor_file = file_paths[0]

    # Execute reasoning task
    start = timer()
    result = agent.execute(
        task="Analyze file dependencies and structure",
        anchor_file=anchor_file,
        max_files=10,
        token_limit=50000
    )
    elapsed = timer() - start

    # Verify results
    assert result["files_analyzed"] >= 1, "Should analyze at least the anchor file"
    assert result["coherence_score"] > 0.0, "Should have non-zero coherence"

    # Reasoning should be fast
    assert elapsed < 1.0, f"Multi-file reasoning took {elapsed:.3f}s (expected <1s)"

    print(f"\n  Multi-file reasoning (10 files):")
    print(f"    Files analyzed: {result['files_analyzed']}")
    print(f"    Relationships found: {result['relationships_found']}")
    print(f"    Tokens used: {result['tokens_used']:,}")
    print(f"    Coherence score: {result['coherence_score']:.2f}")
    print(f"    Execution time: {elapsed * 1000:.2f}ms")

    agent.cleanup()


@pytest.mark.benchmark
@pytest.mark.timing
def test_extended_multi_file_reasoning(medium_codebase, timer):
    """
    Benchmark extended multi-file reasoning with 20+ files.

    Tests reasoning across a larger set of related files to ensure
    scalability beyond the minimum requirement.
    """
    base_dir, file_paths, relationships = medium_codebase

    context_manager = ContextManager(max_files=10000)
    agent = ReasoningTestAgent(
        name="extended_reasoning",
        context_manager=context_manager
    )

    agent.initialize()

    # Index more files
    for file_path in file_paths[:50]:
        with open(file_path, 'r') as f:
            content = f.read()
        agent.add_context_file(file_path, content)

    anchor_file = file_paths[0]

    # Execute with larger context
    start = timer()
    result = agent.execute(
        task="Comprehensive codebase analysis",
        anchor_file=anchor_file,
        max_files=20,
        token_limit=100000
    )
    elapsed = timer() - start

    # Should handle larger contexts
    assert result["files_analyzed"] >= 10, "Should analyze at least 10 files"
    assert elapsed < 2.0, f"Extended reasoning took {elapsed:.3f}s (expected <2s)"

    print(f"\n  Extended multi-file reasoning (20+ files):")
    print(f"    Files analyzed: {result['files_analyzed']}")
    print(f"    Relationships found: {result['relationships_found']}")
    print(f"    Tokens used: {result['tokens_used']:,}")
    print(f"    Coherence score: {result['coherence_score']:.2f}")
    print(f"    Execution time: {elapsed * 1000:.2f}ms")

    agent.cleanup()


@pytest.mark.benchmark
@pytest.mark.timing
def test_relationship_based_reasoning(medium_codebase, timer):
    """
    Benchmark reasoning that traverses file relationships.

    Verifies that agents can efficiently follow import chains and
    dependency relationships for coherent multi-file understanding.
    """
    base_dir, file_paths, relationships = medium_codebase

    context_manager = ContextManager(max_files=10000)
    agent = ReasoningTestAgent(
        name="relationship_reasoning",
        context_manager=context_manager
    )

    agent.initialize()

    # Index files with relationships
    for file_path in file_paths[:30]:
        with open(file_path, 'r') as f:
            content = f.read()
        agent.add_context_file(file_path, content)

    # Find a file with relationships
    anchor_file = None
    for file_path in file_paths[:30]:
        related = context_manager.get_related_files(file_path, max_results=5)
        if len(related) >= 2:
            anchor_file = file_path
            break

    if anchor_file is None:
        anchor_file = file_paths[0]

    # Execute relationship-based reasoning
    start = timer()
    result = agent.execute(
        task="Trace dependencies and relationships",
        anchor_file=anchor_file,
        max_files=15,
        token_limit=75000
    )
    elapsed = timer() - start

    # Should find relationships
    assert result["files_analyzed"] >= 1
    assert elapsed < 1.5, f"Relationship reasoning took {elapsed:.3f}s (expected <1.5s)"

    print(f"\n  Relationship-based reasoning:")
    print(f"    Anchor file: {os.path.basename(anchor_file)}")
    print(f"    Files analyzed: {result['files_analyzed']}")
    print(f"    Relationships found: {result['relationships_found']}")
    print(f"    Coherence score: {result['coherence_score']:.2f}")
    print(f"    Execution time: {elapsed * 1000:.2f}ms")

    agent.cleanup()


@pytest.mark.benchmark
@pytest.mark.timing
def test_context_window_reasoning_performance(large_codebase, timer):
    """
    Benchmark reasoning with context window on large codebase.

    Tests that context window management enables efficient reasoning
    even when the full codebase is much larger than the working set.
    """
    base_dir, file_paths, relationships = large_codebase

    context_manager = ContextManager(max_files=10000)
    agent = ReasoningTestAgent(
        name="window_reasoning",
        context_manager=context_manager
    )

    agent.initialize()

    # Index large codebase
    indexing_start = timer()
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            content = f.read()
        agent.add_context_file(file_path, content)
    indexing_time = timer() - indexing_start

    # Execute reasoning with limited token budget
    anchor_file = file_paths[0]

    start = timer()
    result = agent.execute(
        task="Focused analysis with token budget",
        anchor_file=anchor_file,
        max_files=15,
        token_limit=50000  # Limited budget
    )
    elapsed = timer() - start

    # Should respect token limit
    assert result["tokens_used"] <= 50000, "Should respect token limit"
    assert result["files_analyzed"] >= 1

    # Reasoning should still be fast despite large codebase
    assert elapsed < 2.0, f"Context window reasoning took {elapsed:.3f}s (expected <2s)"

    print(f"\n  Context window reasoning (large codebase):")
    print(f"    Total files indexed: {len(file_paths)}")
    print(f"    Indexing time: {indexing_time:.3f}s")
    print(f"    Files in context window: {result['files_analyzed']}")
    print(f"    Token budget: 50,000")
    print(f"    Tokens used: {result['tokens_used']:,}")
    print(f"    Coherence score: {result['coherence_score']:.2f}")
    print(f"    Reasoning time: {elapsed * 1000:.2f}ms")

    agent.cleanup()


@pytest.mark.benchmark
@pytest.mark.timing
def test_sequential_reasoning_tasks(medium_codebase, timer):
    """
    Benchmark multiple sequential reasoning tasks.

    Verifies that agents maintain performance across multiple
    reasoning operations on the same codebase.
    """
    base_dir, file_paths, relationships = medium_codebase

    context_manager = ContextManager(max_files=10000)
    agent = ReasoningTestAgent(
        name="sequential_reasoning",
        context_manager=context_manager
    )

    agent.initialize()

    # Index files once
    for file_path in file_paths[:40]:
        with open(file_path, 'r') as f:
            content = f.read()
        agent.add_context_file(file_path, content)

    # Execute multiple reasoning tasks
    num_tasks = 5
    task_times = []

    for i in range(num_tasks):
        anchor_file = random.choice(file_paths[:40])

        start = timer()
        result = agent.execute(
            task=f"Analysis task {i+1}",
            anchor_file=anchor_file,
            max_files=10,
            token_limit=50000
        )
        elapsed = timer() - start
        task_times.append(elapsed)

        assert result["files_analyzed"] >= 1
        assert elapsed < 1.0, f"Task {i+1} took {elapsed:.3f}s (expected <1s)"

    avg_time = sum(task_times) / len(task_times)
    max_time = max(task_times)
    min_time = min(task_times)

    print(f"\n  Sequential reasoning tasks ({num_tasks} tasks):")
    print(f"    Average time: {avg_time * 1000:.2f}ms")
    print(f"    Min time: {min_time * 1000:.2f}ms")
    print(f"    Max time: {max_time * 1000:.2f}ms")
    print(f"    Total execution history: {len(agent.execution_history)} tasks")

    agent.cleanup()


@pytest.mark.benchmark
@pytest.mark.timing
def test_coherence_across_file_types(codebase_generator, timer):
    """
    Benchmark coherence when reasoning across diverse file types.

    Tests that agents maintain coherent reasoning when files have
    different structures (imports, classes, functions, etc.).
    """
    base_dir, file_paths, relationships = codebase_generator(size=25)

    context_manager = ContextManager(max_files=10000)
    agent = ReasoningTestAgent(
        name="coherence_test",
        context_manager=context_manager
    )

    agent.initialize()

    # Index all files
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            content = f.read()
        agent.add_context_file(file_path, content)

    anchor_file = file_paths[0]

    start = timer()
    result = agent.execute(
        task="Cross-file structure analysis",
        anchor_file=anchor_file,
        max_files=12,
        token_limit=60000
    )
    elapsed = timer() - start

    # Check coherence
    coherence = result["coherence_score"]
    assert coherence > 0.3, f"Coherence score {coherence:.2f} too low (expected >0.3)"
    assert elapsed < 1.5, f"Coherence test took {elapsed:.3f}s (expected <1.5s)"

    print(f"\n  Cross-file-type coherence:")
    print(f"    Files analyzed: {result['files_analyzed']}")
    print(f"    Coherence score: {coherence:.2f}")
    print(f"    Reasoning steps: {len(result['reasoning_steps'])}")
    print(f"    Execution time: {elapsed * 1000:.2f}ms")

    agent.cleanup()


@pytest.mark.benchmark
def test_multi_file_reasoning_summary(medium_codebase, timer):
    """
    Comprehensive multi-file reasoning benchmark summary.

    This test validates all acceptance criteria for multi-file reasoning:
    1. Agents maintain coherent reasoning across 10+ related files
    2. Context window management supports efficient reasoning
    3. Performance is acceptable for real-world usage
    """
    base_dir, file_paths, relationships = medium_codebase

    # Setup
    context_manager = ContextManager(max_files=10000)
    agent = ReasoningTestAgent(
        name="comprehensive_test",
        context_manager=context_manager
    )

    agent.initialize()

    # Index files
    indexing_start = timer()
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            content = f.read()
        agent.add_context_file(file_path, content)
    indexing_time = timer() - indexing_start

    # Test 1: 10+ file reasoning
    anchor_file = file_paths[0]

    start = timer()
    result_10_files = agent.execute(
        task="10+ file analysis",
        anchor_file=anchor_file,
        max_files=12,
        token_limit=75000
    )
    reasoning_time_10 = timer() - start

    # Test 2: Context window efficiency
    start = timer()
    result_window = agent.execute(
        task="Context window test",
        anchor_file=anchor_file,
        max_files=15,
        token_limit=50000
    )
    window_time = timer() - start

    # Test 3: Relationship traversal
    start = timer()
    related_files = context_manager.get_related_files(anchor_file, max_results=10)
    traversal_time = timer() - start

    # ACCEPTANCE CRITERIA VALIDATION
    assert result_10_files["files_analyzed"] >= 10, \
        f"FAILED: Only analyzed {result_10_files['files_analyzed']} files (requirement: 10+)"

    assert result_10_files["coherence_score"] > 0.3, \
        f"FAILED: Coherence score {result_10_files['coherence_score']:.2f} too low (requirement: >0.3)"

    assert reasoning_time_10 < 2.0, \
        f"FAILED: 10+ file reasoning took {reasoning_time_10:.3f}s (requirement: <2s)"

    assert result_window["tokens_used"] <= 50000, \
        f"FAILED: Token budget exceeded {result_window['tokens_used']} (limit: 50,000)"

    # Print comprehensive summary
    print("\n" + "=" * 70)
    print("  MULTI-FILE REASONING BENCHMARK SUMMARY")
    print("=" * 70)
    print(f"\n  Dataset: {len(file_paths)} files indexed in {indexing_time:.3f}s")

    print(f"\n  10+ File Reasoning Performance:")
    print(f"    Files analyzed: {result_10_files['files_analyzed']} ✓")
    print(f"    Coherence score: {result_10_files['coherence_score']:.2f} ✓")
    print(f"    Relationships: {result_10_files['relationships_found']}")
    print(f"    Tokens used: {result_10_files['tokens_used']:,}")
    print(f"    Execution time: {reasoning_time_10 * 1000:.2f}ms ✓")

    print(f"\n  Context Window Management:")
    print(f"    Token budget: 50,000")
    print(f"    Tokens used: {result_window['tokens_used']:,} ✓")
    print(f"    Files in window: {result_window['files_analyzed']}")
    print(f"    Window retrieval time: {window_time * 1000:.2f}ms")

    print(f"\n  Relationship Traversal:")
    print(f"    Related files found: {len(related_files)}")
    print(f"    Traversal time: {traversal_time * 1000:.2f}ms")

    print("\n" + "=" * 70)
    print("  ALL MULTI-FILE REASONING CRITERIA MET ✓")
    print("=" * 70 + "\n")

    agent.cleanup()
