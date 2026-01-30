"""
Context management system for the extensible AI agent framework.

This module provides the ContextManager class for efficient multi-file
context handling and indexing. It enables agents to maintain awareness
across large codebases and track relationships between files.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import os
import re
from pathlib import Path


class ContextManager:
    """
    Manager for handling multi-file context and relationships.

    The ContextManager provides efficient storage, retrieval, and indexing
    of file content for AI agents. It maintains an in-memory index of files
    and supports searching and relationship tracking.

    Attributes:
        max_files: Maximum number of files to store (for memory management).
        _files: Internal dictionary storing file content and metadata.
        _index: Internal search index mapping tokens to file paths.
    """

    def __init__(self, max_files: int = 1000):
        """
        Initialize the context manager.

        Args:
            max_files: Maximum number of files to store in memory. Defaults to 1000.
                When exceeded, oldest files will be removed (LRU-style).
        """
        self.max_files = max_files
        self._files: Dict[str, Dict[str, Any]] = {}
        self._index: Dict[str, Set[str]] = {}
        self._access_order: List[str] = []  # Track access for LRU
        self._relationships: Dict[str, Dict[str, Set[str]]] = {}  # file -> {type -> set of related files}

    def add_file(
        self,
        file_path: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add or update a file in the context manager.

        This method stores the file content and metadata, updates the search
        index, and manages the file cache size according to max_files limit.

        Args:
            file_path: Path to the file (used as unique identifier).
            content: The file's content as a string.
            metadata: Optional dictionary of additional metadata (e.g., language,
                size, last_modified).

        Raises:
            ValueError: If file_path is empty or content is None.
        """
        if not file_path:
            raise ValueError("file_path cannot be empty")
        if content is None:
            raise ValueError("content cannot be None")

        # Normalize the file path
        normalized_path = str(Path(file_path).as_posix())

        # Remove old file from index if it exists
        if normalized_path in self._files:
            self._remove_from_index(normalized_path)
            self._access_order.remove(normalized_path)

        # Store the file
        self._files[normalized_path] = {
            "content": content,
            "metadata": metadata or {},
            "size": len(content),
        }

        # Update search index
        self._add_to_index(normalized_path, content)

        # Track relationships (imports, etc.) for Python files
        self._track_file_relationships(normalized_path, content)

        # Update access order (most recently used)
        self._access_order.append(normalized_path)

        # Enforce max_files limit
        while len(self._files) > self.max_files:
            oldest_file = self._access_order.pop(0)
            self._remove_from_index(oldest_file)
            self._remove_relationships(oldest_file)
            del self._files[oldest_file]

    def get_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a file's content and metadata.

        Args:
            file_path: Path to the file to retrieve.

        Returns:
            Dictionary containing 'content', 'metadata', and 'size' keys,
            or None if the file is not found.
        """
        normalized_path = str(Path(file_path).as_posix())

        if normalized_path not in self._files:
            return None

        # Update access order (LRU)
        if normalized_path in self._access_order:
            self._access_order.remove(normalized_path)
            self._access_order.append(normalized_path)

        return self._files[normalized_path].copy()

    def remove_file(self, file_path: str) -> bool:
        """
        Remove a file from the context manager.

        Args:
            file_path: Path to the file to remove.

        Returns:
            True if the file was removed, False if it wasn't found.
        """
        normalized_path = str(Path(file_path).as_posix())

        if normalized_path not in self._files:
            return False

        self._remove_from_index(normalized_path)
        self._remove_relationships(normalized_path)
        del self._files[normalized_path]

        if normalized_path in self._access_order:
            self._access_order.remove(normalized_path)

        return True

    def search(self, query: str, max_results: int = 10) -> List[str]:
        """
        Search for files containing the query string.

        This performs a simple token-based search across indexed files.
        The search is case-insensitive.

        Args:
            query: The search string to look for.
            max_results: Maximum number of results to return. Defaults to 10.

        Returns:
            List of file paths that match the query, ordered by relevance
            (number of matching tokens).

        Raises:
            ValueError: If query is empty.
        """
        if not query:
            raise ValueError("query cannot be empty")

        query_lower = query.lower()
        query_tokens = set(self._tokenize(query_lower))

        # Find files that contain any of the query tokens
        matching_files: Dict[str, int] = {}

        for token in query_tokens:
            if token in self._index:
                for file_path in self._index[token]:
                    matching_files[file_path] = matching_files.get(file_path, 0) + 1

        # Sort by number of matching tokens (relevance)
        sorted_files = sorted(
            matching_files.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [file_path for file_path, _ in sorted_files[:max_results]]

    def get_related_files(
        self,
        file_path: str,
        max_results: int = 5
    ) -> List[str]:
        """
        Find files related to the given file.

        This method combines explicit relationships (imports, dependencies)
        with content similarity to find related files. Explicitly related
        files are prioritized over content-similar files.

        Args:
            file_path: Path to the file to find relations for.
            max_results: Maximum number of related files to return. Defaults to 5.

        Returns:
            List of related file paths, ordered by relevance.
            Returns empty list if the file is not found.
        """
        normalized_path = str(Path(file_path).as_posix())

        if normalized_path not in self._files:
            return []

        # Collect explicitly related files (higher priority)
        explicit_related: Set[str] = set()
        if normalized_path in self._relationships:
            for relationship_type, related_files in self._relationships[normalized_path].items():
                explicit_related.update(related_files)

        # Calculate content similarity scores
        file_data = self._files[normalized_path]
        file_tokens = set(self._tokenize(file_data["content"].lower()))
        similarity_scores: Dict[str, float] = {}

        for other_path, other_data in self._files.items():
            if other_path == normalized_path:
                continue

            other_tokens = set(self._tokenize(other_data["content"].lower()))

            # Calculate Jaccard similarity
            intersection = len(file_tokens & other_tokens)
            union = len(file_tokens | other_tokens)

            if union > 0:
                similarity = intersection / union
                # Boost score for explicitly related files
                if other_path in explicit_related:
                    similarity = similarity * 1.5 + 0.5  # Boost explicit relationships
                similarity_scores[other_path] = similarity

        # Add explicitly related files that weren't found in content similarity
        for related_file in explicit_related:
            if related_file not in similarity_scores and related_file in self._files:
                similarity_scores[related_file] = 0.8  # High score for explicit relationships

        # Sort by similarity score
        sorted_files = sorted(
            similarity_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [file_path for file_path, _ in sorted_files[:max_results]]

    def list_files(self) -> List[str]:
        """
        Get a list of all files in the context manager.

        Returns:
            List of file paths in alphabetical order.
        """
        return sorted(self._files.keys())

    def has_file(self, file_path: str) -> bool:
        """
        Check if a file is stored in the context manager.

        Args:
            file_path: Path to the file to check.

        Returns:
            True if the file exists, False otherwise.
        """
        normalized_path = str(Path(file_path).as_posix())
        return normalized_path in self._files

    def clear(self) -> None:
        """Remove all files from the context manager."""
        self._files.clear()
        self._index.clear()
        self._access_order.clear()
        self._relationships.clear()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the context manager.

        Returns:
            Dictionary containing statistics such as file_count, total_size,
            index_size, etc.
        """
        total_size = sum(data["size"] for data in self._files.values())
        relationship_count = sum(
            len(related)
            for relationships in self._relationships.values()
            for related in relationships.values()
        )
        return {
            "file_count": len(self._files),
            "total_size": total_size,
            "index_size": len(self._index),
            "max_files": self.max_files,
            "average_file_size": total_size / len(self._files) if self._files else 0,
            "relationship_count": relationship_count,
        }

    def add_relationship(
        self,
        file_path: str,
        related_file: str,
        relationship_type: str = "related"
    ) -> None:
        """
        Add an explicit relationship between two files.

        This allows tracking of imports, dependencies, and other semantic
        relationships between files.

        Args:
            file_path: The source file path.
            related_file: The target file path that is related to the source.
            relationship_type: Type of relationship (e.g., 'imports', 'depends_on',
                'inherits', 'uses'). Defaults to 'related'.

        Raises:
            ValueError: If either file path is empty.
        """
        if not file_path or not related_file:
            raise ValueError("file_path and related_file cannot be empty")

        normalized_path = str(Path(file_path).as_posix())
        normalized_related = str(Path(related_file).as_posix())

        if normalized_path not in self._relationships:
            self._relationships[normalized_path] = {}

        if relationship_type not in self._relationships[normalized_path]:
            self._relationships[normalized_path][relationship_type] = set()

        self._relationships[normalized_path][relationship_type].add(normalized_related)

    def get_relationships(
        self,
        file_path: str,
        relationship_type: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """
        Get relationships for a file.

        Args:
            file_path: The file path to get relationships for.
            relationship_type: Optional filter for specific relationship type.
                If None, returns all relationship types.

        Returns:
            Dictionary mapping relationship types to lists of related files.
            Returns empty dict if file has no relationships.
        """
        normalized_path = str(Path(file_path).as_posix())

        if normalized_path not in self._relationships:
            return {}

        relationships = self._relationships[normalized_path]

        if relationship_type:
            if relationship_type in relationships:
                return {relationship_type: list(relationships[relationship_type])}
            return {}

        return {
            rel_type: list(related_files)
            for rel_type, related_files in relationships.items()
        }

    def _track_file_relationships(self, file_path: str, content: str) -> None:
        """
        Automatically track relationships in a file (e.g., imports in Python files).

        Args:
            file_path: The file path being analyzed.
            content: The file content to analyze.
        """
        # Only track relationships for Python files
        if not file_path.endswith('.py'):
            return

        # Parse Python imports
        imports = self._parse_python_imports(content)

        for imported_module in imports:
            # Convert module names to potential file paths
            # e.g., 'agent_framework.tools' -> 'agent_framework/tools.py'
            potential_paths = self._module_to_file_paths(imported_module, file_path)

            for potential_path in potential_paths:
                # Only add relationship if the file exists in our context
                if self.has_file(potential_path):
                    self.add_relationship(file_path, potential_path, "imports")

    def _parse_python_imports(self, content: str) -> List[str]:
        """
        Parse Python import statements from file content.

        Args:
            content: Python file content.

        Returns:
            List of imported module names.
        """
        imports = []

        # Match "import module" or "import module.submodule"
        import_pattern = r'^\s*import\s+([\w.]+)'
        # Match "from module import ..." or "from . import ..."
        from_import_pattern = r'^\s*from\s+([\w.]+)\s+import'

        for line in content.split('\n'):
            # Skip comments
            if line.strip().startswith('#'):
                continue

            # Check for "import module" statements
            match = re.match(import_pattern, line)
            if match:
                imports.append(match.group(1))
                continue

            # Check for "from module import ..." statements
            match = re.match(from_import_pattern, line)
            if match:
                imports.append(match.group(1))

        return imports

    def _module_to_file_paths(self, module_name: str, source_file: str) -> List[str]:
        """
        Convert a Python module name to potential file paths.

        Args:
            module_name: The module name (e.g., 'agent_framework.tools').
            source_file: The source file doing the import (for relative imports).

        Returns:
            List of potential file paths.
        """
        paths = []

        # Convert module name to path (e.g., 'agent_framework.tools' -> 'agent_framework/tools.py')
        module_path = module_name.replace('.', '/')

        # Try as a .py file
        paths.append(f"{module_path}.py")
        paths.append(f"src/{module_path}.py")

        # Try as a package (__init__.py)
        paths.append(f"{module_path}/__init__.py")
        paths.append(f"src/{module_path}/__init__.py")

        return paths

    def _remove_relationships(self, file_path: str) -> None:
        """
        Remove all relationships for a file.

        This removes both outgoing relationships (from this file to others)
        and incoming relationships (from other files to this file).

        Args:
            file_path: The file path to remove relationships for.
        """
        # Remove outgoing relationships
        if file_path in self._relationships:
            del self._relationships[file_path]

        # Remove incoming relationships (this file appearing in other files' relationships)
        for source_file, relationships in self._relationships.items():
            for rel_type, related_files in relationships.items():
                if file_path in related_files:
                    related_files.discard(file_path)

    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text for indexing and search.

        This is a simple word-based tokenization. More sophisticated
        tokenization may be added in the future.

        Args:
            text: The text to tokenize.

        Returns:
            List of tokens (words).
        """
        # Simple word-based tokenization
        # Remove common punctuation and split on whitespace
        text = text.replace("(", " ").replace(")", " ")
        text = text.replace("{", " ").replace("}", " ")
        text = text.replace("[", " ").replace("]", " ")
        text = text.replace(",", " ").replace(".", " ")
        text = text.replace(";", " ").replace(":", " ")
        text = text.replace("=", " ").replace("+", " ")
        text = text.replace("-", " ").replace("*", " ")
        text = text.replace("/", " ").replace("\\", " ")

        tokens = [token.strip() for token in text.split() if token.strip()]
        return tokens

    def _add_to_index(self, file_path: str, content: str) -> None:
        """
        Add a file's content to the search index.

        Args:
            file_path: Path to the file being indexed.
            content: The file's content.
        """
        tokens = self._tokenize(content.lower())

        for token in tokens:
            if token not in self._index:
                self._index[token] = set()
            self._index[token].add(file_path)

    def _remove_from_index(self, file_path: str) -> None:
        """
        Remove a file from the search index.

        Args:
            file_path: Path to the file to remove from index.
        """
        # Remove this file from all token sets
        tokens_to_remove = []

        for token, file_set in self._index.items():
            if file_path in file_set:
                file_set.discard(file_path)
                # Mark empty token entries for removal
                if not file_set:
                    tokens_to_remove.append(token)

        # Clean up empty token entries
        for token in tokens_to_remove:
            del self._index[token]

    def __len__(self) -> int:
        """Return the number of files in the context manager."""
        return len(self._files)

    def __repr__(self) -> str:
        """Return a string representation of the context manager."""
        return f"ContextManager(files={len(self._files)}, max_files={self.max_files})"

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return (
            f"ContextManager with {len(self._files)} file(s), "
            f"max capacity: {self.max_files}"
        )
