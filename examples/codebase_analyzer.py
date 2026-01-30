#!/usr/bin/env python3
"""
Codebase Analyzer Agent Example

This example demonstrates how to use the ContextManager to analyze
and understand relationships within a codebase. The agent can index
files, search for patterns, and identify related files.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from agent_framework.agent import Agent
from agent_framework.context import ContextManager
from agent_framework.logging import AgentLogger, LogLevel


class CodebaseAnalyzer(Agent):
    """
    An agent that analyzes codebases and provides insights.

    This agent demonstrates advanced context management including:
    - Multi-file indexing
    - Relationship tracking
    - Search capabilities
    - Context window management
    """

    def execute(self, task: str, **kwargs) -> dict:
        """
        Execute a codebase analysis task.

        Args:
            task: The analysis task (e.g., "index", "search", "analyze", "find_related")
            **kwargs: Task-specific parameters

        Returns:
            Dictionary with analysis results
        """
        self._log("info", f"Executing codebase analysis: {task}", task=task)

        if task == "index":
            return self._index_files(kwargs.get("files", []))
        elif task == "search":
            return self._search_codebase(kwargs.get("query", ""))
        elif task == "analyze":
            return self._analyze_structure()
        elif task == "find_related":
            return self._find_related_files(kwargs.get("file_path", ""))
        else:
            return {"error": f"Unknown task: {task}"}

    def process_context(self, context: dict) -> dict:
        """
        Process context information for analysis.

        Args:
            context: Raw context with file information

        Returns:
            Processed context ready for analysis
        """
        return {
            "files": context.get("files", []),
            "query": context.get("query", ""),
            "options": context.get("options", {})
        }

    def format_response(self, result: any) -> str:
        """
        Format analysis results into readable output.

        Args:
            result: The raw result from execute()

        Returns:
            Formatted string representation
        """
        if isinstance(result, dict):
            if "error" in result:
                return f"Error: {result['error']}"

            if "indexed" in result:
                return f"Indexed {result['indexed']} files"

            if "matches" in result:
                matches = result["matches"]
                if not matches:
                    return "No matches found"
                return f"Found {len(matches)} matches:\n  - " + "\n  - ".join(matches)

            if "related_files" in result:
                related = result["related_files"]
                if not related:
                    return "No related files found"
                return f"Found {len(related)} related files:\n  - " + "\n  - ".join(related)

            if "structure" in result:
                s = result["structure"]
                return (
                    f"Codebase Structure:\n"
                    f"  Total files: {s['total_files']}\n"
                    f"  Total size: {s['total_size']} bytes\n"
                    f"  Avg file size: {s['avg_file_size']:.0f} bytes\n"
                    f"  Relationships: {s['relationships']}"
                )

        return str(result)

    def _index_files(self, files: list) -> dict:
        """Index a list of files into the context manager."""
        if not self.context_manager:
            return {"error": "No context manager available"}

        indexed = 0
        for file_info in files:
            file_path = file_info.get("path", "")
            content = file_info.get("content", "")
            metadata = file_info.get("metadata", {})

            if file_path and content is not None:
                self.add_context_file(file_path, content, metadata)
                indexed += 1

        return {"indexed": indexed, "total": len(files)}

    def _search_codebase(self, query: str) -> dict:
        """Search the codebase for matching files."""
        if not self.context_manager:
            return {"error": "No context manager available"}

        if not query:
            return {"error": "Query cannot be empty"}

        matches = self.search_context(query, max_results=10)
        return {"query": query, "matches": matches}

    def _analyze_structure(self) -> dict:
        """Analyze the overall codebase structure."""
        if not self.context_manager:
            return {"error": "No context manager available"}

        stats = self.context_manager.get_stats()

        return {
            "structure": {
                "total_files": stats["file_count"],
                "total_size": stats["total_size"],
                "avg_file_size": stats["average_file_size"],
                "relationships": stats["relationship_count"]
            }
        }

    def _find_related_files(self, file_path: str) -> dict:
        """Find files related to the given file."""
        if not self.context_manager:
            return {"error": "No context manager available"}

        if not file_path:
            return {"error": "file_path cannot be empty"}

        related = self.context_manager.get_related_files(file_path, max_results=5)
        return {"file_path": file_path, "related_files": related}


def main():
    """Main function demonstrating codebase analysis."""
    print("=" * 60)
    print("Codebase Analyzer Example")
    print("=" * 60)
    print()

    # Create logger and context manager
    logger = AgentLogger(
        name="codebase_analyzer",
        level=LogLevel.INFO,
        format="text"
    )

    context_manager = ContextManager(max_files=100, logger=logger)

    # Create the analyzer agent
    agent = CodebaseAnalyzer(
        name="CodebaseAnalyzer",
        config={"max_file_size": 1000000},
        context_manager=context_manager,
        logger=logger
    )

    agent.initialize()
    print(f"Agent initialized: {agent}\n")

    # Example 1: Index sample Python files
    print("Example 1: Index sample files")
    print("-" * 40)
    sample_files = [
        {
            "path": "src/main.py",
            "content": "from utils import helper\n\ndef main():\n    helper.do_something()\n",
            "metadata": {"language": "python", "lines": 4}
        },
        {
            "path": "src/utils/helper.py",
            "content": "def do_something():\n    print('Hello from helper')\n",
            "metadata": {"language": "python", "lines": 2}
        },
        {
            "path": "tests/test_main.py",
            "content": "from src.main import main\n\ndef test_main():\n    main()\n",
            "metadata": {"language": "python", "lines": 4}
        },
        {
            "path": "README.md",
            "content": "# My Project\n\nThis is a sample project for demonstration.\n",
            "metadata": {"language": "markdown", "lines": 3}
        }
    ]

    result = agent.execute("index", files=sample_files)
    response = agent.format_response(result)
    print(f"Output: {response}\n")

    # Example 2: Search for files containing "main"
    print("Example 2: Search for 'main'")
    print("-" * 40)
    result = agent.execute("search", query="main")
    response = agent.format_response(result)
    print(f"Output: {response}\n")

    # Example 3: Analyze codebase structure
    print("Example 3: Analyze structure")
    print("-" * 40)
    result = agent.execute("analyze")
    response = agent.format_response(result)
    print(f"Output:\n{response}\n")

    # Example 4: Find related files
    print("Example 4: Find files related to 'src/main.py'")
    print("-" * 40)
    result = agent.execute("find_related", file_path="src/main.py")
    response = agent.format_response(result)
    print(f"Output: {response}\n")

    # Example 5: Use context window to get prioritized files
    print("Example 5: Get context window (token budget = 100)")
    print("-" * 40)
    context_window = agent.get_context_window(
        token_limit=100,
        anchor_file="src/main.py"
    )
    print(f"Files in context window: {len(context_window)}")
    for file_info in context_window:
        print(f"  - {file_info['file_path']}")
    print()

    # Show statistics
    print("Context Manager Statistics")
    print("-" * 40)
    stats = context_manager.get_stats()
    print(f"Files indexed: {stats['file_count']}")
    print(f"Total size: {stats['total_size']} bytes")
    print(f"Index tokens: {stats['index_size']}")
    print(f"Relationships: {stats['relationship_count']}")
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
