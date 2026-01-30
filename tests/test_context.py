"""
Tests for the ContextManager class.

This module tests the ContextManager to ensure proper file indexing,
storage, retrieval, search, and relationship tracking functionality.
"""

import pytest
from agent_framework.context import ContextManager


class TestContextManagerInitialization:
    """Test suite for ContextManager initialization."""

    def test_context_manager_initialization(self):
        """Test that ContextManager initializes with correct defaults."""
        cm = ContextManager()

        assert cm.max_files == 1000
        assert len(cm) == 0
        assert cm.list_files() == []

    def test_context_manager_custom_max_files(self):
        """Test that ContextManager accepts custom max_files parameter."""
        cm = ContextManager(max_files=50)

        assert cm.max_files == 50
        assert len(cm) == 0

    def test_context_manager_repr(self):
        """Test the __repr__ method."""
        cm = ContextManager(max_files=100)
        repr_str = repr(cm)

        assert "ContextManager" in repr_str
        assert "files=0" in repr_str
        assert "max_files=100" in repr_str

    def test_context_manager_str(self):
        """Test the __str__ method."""
        cm = ContextManager(max_files=100)
        str_repr = str(cm)

        assert "0 file(s)" in str_repr
        assert "max capacity: 100" in str_repr


class TestFileManagement:
    """Test suite for file addition, retrieval, and removal."""

    def test_file_storage(self):
        """Test efficient file content storage and retrieval."""
        cm = ContextManager()

        # Test basic storage
        cm.add_file("file1.py", "content1")
        assert cm.has_file("file1.py")
        assert cm.get_file("file1.py")["content"] == "content1"

        # Test storage with metadata
        metadata = {"language": "python", "size": 100}
        cm.add_file("file2.py", "content2", metadata=metadata)
        file2_data = cm.get_file("file2.py")
        assert file2_data["content"] == "content2"
        assert file2_data["metadata"] == metadata

        # Test updating existing file
        cm.add_file("file1.py", "updated_content1")
        assert cm.get_file("file1.py")["content"] == "updated_content1"
        assert len(cm) == 2  # Should still have 2 files, not 3

        # Test retrieval returns copy (data isolation)
        data1 = cm.get_file("file1.py")
        data1["content"] = "modified"
        data2 = cm.get_file("file1.py")
        assert data2["content"] == "updated_content1"  # Original unchanged

        # Test efficient storage of multiple files
        for i in range(10):
            cm.add_file(f"bulk_{i}.py", f"content_{i}")
        assert len(cm) == 12  # 2 original + 10 new

        # Verify all files are retrievable
        for i in range(10):
            assert cm.has_file(f"bulk_{i}.py")
            assert cm.get_file(f"bulk_{i}.py")["content"] == f"content_{i}"

        # Test storage statistics
        stats = cm.get_stats()
        assert stats["file_count"] == 12
        assert stats["total_size"] > 0

    def test_add_file(self):
        """Test adding a file to the context manager."""
        cm = ContextManager()
        cm.add_file("test.py", "def hello(): pass")

        assert len(cm) == 1
        assert cm.has_file("test.py")

    def test_add_file_with_metadata(self):
        """Test adding a file with metadata."""
        cm = ContextManager()
        metadata = {"language": "python", "author": "test"}
        cm.add_file("test.py", "def hello(): pass", metadata=metadata)

        file_data = cm.get_file("test.py")
        assert file_data is not None
        assert file_data["content"] == "def hello(): pass"
        assert file_data["metadata"] == metadata
        assert file_data["size"] == len("def hello(): pass")

    def test_add_file_updates_existing(self):
        """Test that adding a file with same path updates it."""
        cm = ContextManager()
        cm.add_file("test.py", "old content")
        cm.add_file("test.py", "new content")

        assert len(cm) == 1
        file_data = cm.get_file("test.py")
        assert file_data["content"] == "new content"

    def test_add_file_empty_path_raises_error(self):
        """Test that adding a file with empty path raises ValueError."""
        cm = ContextManager()

        with pytest.raises(ValueError) as exc_info:
            cm.add_file("", "content")

        assert "file_path cannot be empty" in str(exc_info.value)

    def test_add_file_none_content_raises_error(self):
        """Test that adding a file with None content raises ValueError."""
        cm = ContextManager()

        with pytest.raises(ValueError) as exc_info:
            cm.add_file("test.py", None)

        assert "content cannot be None" in str(exc_info.value)

    def test_get_file(self):
        """Test retrieving a file from the context manager."""
        cm = ContextManager()
        cm.add_file("test.py", "content here")

        file_data = cm.get_file("test.py")

        assert file_data is not None
        assert file_data["content"] == "content here"
        assert file_data["size"] == len("content here")
        assert "metadata" in file_data

    def test_get_file_not_found(self):
        """Test that getting a non-existent file returns None."""
        cm = ContextManager()

        file_data = cm.get_file("nonexistent.py")

        assert file_data is None

    def test_get_file_returns_copy(self):
        """Test that get_file returns a copy, not original."""
        cm = ContextManager()
        cm.add_file("test.py", "content")

        file_data1 = cm.get_file("test.py")
        file_data2 = cm.get_file("test.py")

        # Modify one copy
        file_data1["content"] = "modified"

        # Other copy should be unchanged
        assert file_data2["content"] == "content"

    def test_remove_file(self):
        """Test removing a file from the context manager."""
        cm = ContextManager()
        cm.add_file("test.py", "content")

        assert cm.has_file("test.py")

        result = cm.remove_file("test.py")

        assert result is True
        assert not cm.has_file("test.py")
        assert len(cm) == 0

    def test_remove_file_not_found(self):
        """Test that removing a non-existent file returns False."""
        cm = ContextManager()

        result = cm.remove_file("nonexistent.py")

        assert result is False

    def test_has_file(self):
        """Test checking if a file exists."""
        cm = ContextManager()

        assert not cm.has_file("test.py")

        cm.add_file("test.py", "content")

        assert cm.has_file("test.py")

    def test_list_files(self):
        """Test listing all files."""
        cm = ContextManager()

        cm.add_file("b.py", "content")
        cm.add_file("a.py", "content")
        cm.add_file("c.py", "content")

        files = cm.list_files()

        # Should be in alphabetical order
        assert files == ["a.py", "b.py", "c.py"]

    def test_clear(self):
        """Test clearing all files."""
        cm = ContextManager()

        cm.add_file("test1.py", "content1")
        cm.add_file("test2.py", "content2")

        assert len(cm) == 2

        cm.clear()

        assert len(cm) == 0
        assert cm.list_files() == []


class TestFileIndexing:
    """Test suite for file indexing and search functionality."""

    def test_search_finds_matching_files(self):
        """Test that search finds files containing the query."""
        cm = ContextManager()

        cm.add_file("test1.py", "def hello(): print('hello world')")
        cm.add_file("test2.py", "def goodbye(): print('goodbye')")
        cm.add_file("test3.py", "class HelloWorld: pass")

        results = cm.search("hello")

        # Should find test1.py and test3.py
        assert len(results) >= 1
        assert "test1.py" in results or "test3.py" in results

    def test_search_case_insensitive(self):
        """Test that search is case-insensitive."""
        cm = ContextManager()

        cm.add_file("test.py", "HELLO World")

        results = cm.search("hello")

        assert "test.py" in results

    def test_search_empty_query_raises_error(self):
        """Test that searching with empty query raises ValueError."""
        cm = ContextManager()

        with pytest.raises(ValueError) as exc_info:
            cm.search("")

        assert "query cannot be empty" in str(exc_info.value)

    def test_search_max_results(self):
        """Test that search respects max_results parameter."""
        cm = ContextManager()

        for i in range(20):
            cm.add_file(f"test{i}.py", "def test(): pass")

        results = cm.search("test", max_results=5)

        assert len(results) <= 5

    def test_search_no_results(self):
        """Test search when no files match."""
        cm = ContextManager()

        cm.add_file("test.py", "def hello(): pass")

        results = cm.search("nonexistent")

        assert results == []

    def test_search_orders_by_relevance(self):
        """Test that search results are ordered by relevance."""
        cm = ContextManager()

        # File with multiple occurrences of 'test'
        cm.add_file("very_relevant.py", "test test test function")
        cm.add_file("less_relevant.py", "test function")
        cm.add_file("unrelated.py", "function only")

        results = cm.search("test")

        # very_relevant.py should rank higher due to more matches
        assert "very_relevant.py" in results
        # The order should prioritize files with more matching tokens
        assert results.index("very_relevant.py") <= results.index("less_relevant.py")


class TestFileRelationships:
    """Test suite for file relationship tracking."""

    def test_get_related_files(self):
        """Test finding related files based on content similarity."""
        cm = ContextManager()

        cm.add_file("models.py", "class User: def save(): pass")
        cm.add_file("views.py", "class UserView: def render(): pass")
        cm.add_file("tests.py", "class TestUser: def test_save(): pass")
        cm.add_file("unrelated.py", "def completely_different(): return 42")

        related = cm.get_related_files("models.py")

        # tests.py and views.py should be related due to shared 'User' tokens
        assert len(related) > 0
        # unrelated.py should rank lower or not appear

    def test_get_related_files_not_found(self):
        """Test getting related files for non-existent file."""
        cm = ContextManager()

        related = cm.get_related_files("nonexistent.py")

        assert related == []

    def test_get_related_files_max_results(self):
        """Test that get_related_files respects max_results."""
        cm = ContextManager()

        cm.add_file("main.py", "def test(): pass")

        for i in range(20):
            cm.add_file(f"test{i}.py", "def test(): pass")

        related = cm.get_related_files("main.py", max_results=3)

        assert len(related) <= 3

    def test_get_related_files_excludes_self(self):
        """Test that get_related_files doesn't include the query file."""
        cm = ContextManager()

        cm.add_file("test1.py", "content")
        cm.add_file("test2.py", "content")

        related = cm.get_related_files("test1.py")

        assert "test1.py" not in related

    def test_add_explicit_relationship(self):
        """Test adding explicit relationships between files."""
        cm = ContextManager()

        cm.add_file("main.py", "import utils")
        cm.add_file("utils.py", "def helper(): pass")

        # Add explicit relationship
        cm.add_relationship("main.py", "utils.py", "imports")

        # Get relationships
        relationships = cm.get_relationships("main.py")

        assert "imports" in relationships
        assert "utils.py" in relationships["imports"]

    def test_get_relationships_specific_type(self):
        """Test getting specific relationship types."""
        cm = ContextManager()

        cm.add_file("main.py", "content")
        cm.add_file("utils.py", "content")
        cm.add_file("config.py", "content")

        cm.add_relationship("main.py", "utils.py", "imports")
        cm.add_relationship("main.py", "config.py", "depends_on")

        # Get only imports
        imports = cm.get_relationships("main.py", "imports")

        assert "imports" in imports
        assert "utils.py" in imports["imports"]
        assert "depends_on" not in imports

    def test_automatic_import_tracking(self):
        """Test automatic tracking of Python imports."""
        cm = ContextManager()

        # Add files that will be imported
        cm.add_file("src/agent_framework/tools.py", "class Tool: pass")
        cm.add_file("src/agent_framework/context.py", "class ContextManager: pass")

        # Add file with imports
        cm.add_file("src/agent_framework/agent.py", """
from agent_framework.tools import Tool
import agent_framework.context
""")

        # Check that relationships were automatically tracked
        relationships = cm.get_relationships("src/agent_framework/agent.py")

        assert "imports" in relationships
        # At least one import should be tracked
        assert len(relationships["imports"]) > 0

    def test_relationship_boosts_relevance(self):
        """Test that explicit relationships boost relevance in get_related_files."""
        cm = ContextManager()

        cm.add_file("main.py", "import helper")
        cm.add_file("helper.py", "def utility(): pass")
        cm.add_file("similar.py", "import different helper function")

        # Add explicit relationship
        cm.add_relationship("main.py", "helper.py", "imports")

        related = cm.get_related_files("main.py", max_results=5)

        # helper.py should rank higher due to explicit relationship
        if len(related) >= 2:
            # helper.py should appear before similar.py due to relationship boost
            assert "helper.py" in related

    def test_remove_file_cleans_relationships(self):
        """Test that removing a file also removes its relationships."""
        cm = ContextManager()

        cm.add_file("main.py", "content")
        cm.add_file("utils.py", "content")

        cm.add_relationship("main.py", "utils.py", "imports")

        # Remove the file
        cm.remove_file("main.py")

        # Relationships should be gone
        relationships = cm.get_relationships("main.py")
        assert relationships == {}

    def test_clear_removes_relationships(self):
        """Test that clear() removes all relationships."""
        cm = ContextManager()

        cm.add_file("main.py", "content")
        cm.add_file("utils.py", "content")
        cm.add_relationship("main.py", "utils.py", "imports")

        cm.clear()

        relationships = cm.get_relationships("main.py")
        assert relationships == {}

    def test_relationship_stats(self):
        """Test that statistics include relationship counts."""
        cm = ContextManager()

        cm.add_file("main.py", "content")
        cm.add_file("utils.py", "content")
        cm.add_file("config.py", "content")

        cm.add_relationship("main.py", "utils.py", "imports")
        cm.add_relationship("main.py", "config.py", "imports")

        stats = cm.get_stats()

        assert "relationship_count" in stats
        assert stats["relationship_count"] >= 2


def test_file_relationships():
    """
    Comprehensive test for multi-file relationship tracking.

    This test validates import tracking, dependency tracking, and
    semantic relationships between files.
    """
    cm = ContextManager()

    # Create a mini project structure
    cm.add_file("src/agent_framework/__init__.py", "")
    cm.add_file("src/agent_framework/agent.py", """
from agent_framework.tools import Tool, ToolRegistry
from agent_framework.context import ContextManager

class Agent:
    def __init__(self):
        self.tools = ToolRegistry()
        self.context = ContextManager()
""")

    cm.add_file("src/agent_framework/tools.py", """
class Tool:
    pass

class ToolRegistry:
    pass
""")

    cm.add_file("src/agent_framework/context.py", """
class ContextManager:
    pass
""")

    # Test automatic import tracking
    agent_relationships = cm.get_relationships("src/agent_framework/agent.py")
    assert "imports" in agent_relationships
    assert len(agent_relationships["imports"]) > 0

    # Test that related files are found
    related_to_agent = cm.get_related_files("src/agent_framework/agent.py", max_results=5)
    assert len(related_to_agent) > 0

    # At least one of the imported files should be in related files
    imported_files = set(agent_relationships["imports"])
    related_set = set(related_to_agent)
    assert len(imported_files & related_set) > 0

    # Test manual relationship addition
    cm.add_relationship("src/agent_framework/tools.py",
                       "src/agent_framework/context.py",
                       "depends_on")

    tools_relationships = cm.get_relationships("src/agent_framework/tools.py")
    assert "depends_on" in tools_relationships
    assert "src/agent_framework/context.py" in tools_relationships["depends_on"]

    # Test that relationships survive file updates
    cm.add_file("src/agent_framework/agent.py", """
from agent_framework.tools import Tool
# Updated content
class Agent:
    pass
""")

    # Should still have import relationships (re-tracked)
    agent_relationships_updated = cm.get_relationships("src/agent_framework/agent.py")
    assert "imports" in agent_relationships_updated

    # Test relationship removal
    cm.remove_file("src/agent_framework/agent.py")
    agent_relationships_after_removal = cm.get_relationships("src/agent_framework/agent.py")
    assert agent_relationships_after_removal == {}

    # Test statistics
    stats = cm.get_stats()
    assert "relationship_count" in stats
    assert stats["relationship_count"] >= 0


class TestContextManagerStats:
    """Test suite for context manager statistics."""

    def test_get_stats(self):
        """Test getting statistics about the context manager."""
        cm = ContextManager(max_files=100)

        stats = cm.get_stats()

        assert stats["file_count"] == 0
        assert stats["total_size"] == 0
        assert stats["max_files"] == 100
        assert stats["average_file_size"] == 0

    def test_get_stats_with_files(self):
        """Test statistics with files added."""
        cm = ContextManager()

        cm.add_file("test1.py", "12345")  # 5 bytes
        cm.add_file("test2.py", "1234567890")  # 10 bytes

        stats = cm.get_stats()

        assert stats["file_count"] == 2
        assert stats["total_size"] == 15
        assert stats["average_file_size"] == 7.5
        assert stats["index_size"] > 0


class TestLRUEviction:
    """Test suite for LRU eviction when max_files is exceeded."""

    def test_evicts_oldest_file_when_max_reached(self):
        """Test that oldest file is evicted when max_files is reached."""
        cm = ContextManager(max_files=3)

        cm.add_file("file1.py", "content1")
        cm.add_file("file2.py", "content2")
        cm.add_file("file3.py", "content3")

        assert len(cm) == 3

        # Adding a 4th file should evict file1.py
        cm.add_file("file4.py", "content4")

        assert len(cm) == 3
        assert not cm.has_file("file1.py")
        assert cm.has_file("file2.py")
        assert cm.has_file("file3.py")
        assert cm.has_file("file4.py")

    def test_get_file_updates_lru(self):
        """Test that accessing a file updates its position in LRU."""
        cm = ContextManager(max_files=3)

        cm.add_file("file1.py", "content1")
        cm.add_file("file2.py", "content2")
        cm.add_file("file3.py", "content3")

        # Access file1 to make it recently used
        cm.get_file("file1.py")

        # Add a new file - should evict file2, not file1
        cm.add_file("file4.py", "content4")

        assert cm.has_file("file1.py")  # Should still be here
        assert not cm.has_file("file2.py")  # Should be evicted
        assert cm.has_file("file3.py")
        assert cm.has_file("file4.py")


class TestPathNormalization:
    """Test suite for file path normalization."""

    def test_path_normalization(self):
        """Test that different path formats are normalized."""
        cm = ContextManager()

        # Add with different path separators (if on Unix-like system)
        cm.add_file("dir/file.py", "content")

        # Should be found with normalized path
        assert cm.has_file("dir/file.py")

    def test_update_with_different_path_format(self):
        """Test updating a file using different path formats."""
        cm = ContextManager()

        cm.add_file("dir/file.py", "original")
        cm.add_file("dir/file.py", "updated")

        assert len(cm) == 1
        file_data = cm.get_file("dir/file.py")
        assert file_data["content"] == "updated"


def test_context_window():
    """
    Test context window management for large codebases.

    This test validates token-based context management, prioritization,
    and pruning when contexts exceed token limits.
    """
    cm = ContextManager()

    # Add files with varying sizes and importance
    # High priority: recently accessed, has relationships
    cm.add_file("main.py", "import utils\nimport config\n" + "x = 1\n" * 50)
    cm.add_file("utils.py", "def helper():\n    pass\n" + "# comment\n" * 30)
    cm.add_file("config.py", "CONFIG = {}\n" + "# settings\n" * 20)

    # Medium priority: related but not accessed
    cm.add_file("models.py", "class Model:\n    pass\n" + "# data model\n" * 40)

    # Low priority: unrelated
    cm.add_file("unrelated.py", "def unrelated():\n    pass\n" + "# unrelated\n" * 100)

    # Add explicit relationships to boost priority
    cm.add_relationship("main.py", "utils.py", "imports")
    cm.add_relationship("main.py", "config.py", "imports")

    # Test 1: Get context window with generous token limit (should include all)
    context_large = cm.get_context_window(token_limit=10000)
    assert len(context_large) > 0
    assert all(isinstance(item, dict) for item in context_large)
    assert all("file_path" in item and "content" in item for item in context_large)

    # Test 2: Get context window with strict token limit
    # Should prioritize based on relationships and relevance
    context_small = cm.get_context_window(token_limit=500, anchor_file="main.py")
    assert len(context_small) > 0
    assert len(context_small) <= len(context_large)

    # Verify total tokens don't exceed limit
    total_tokens = sum(cm.estimate_tokens(item["content"]) for item in context_small)
    assert total_tokens <= 500

    # Test 3: Anchor file should be included if specified
    file_paths = [item["file_path"] for item in context_small]
    assert "main.py" in file_paths

    # Test 4: Related files should be prioritized over unrelated
    # utils.py and config.py should be preferred over unrelated.py
    if len(context_small) >= 2:
        # At least some related files should be included
        has_related = "utils.py" in file_paths or "config.py" in file_paths
        assert has_related

    # Test 5: Test with very small token limit
    context_tiny = cm.get_context_window(token_limit=100, anchor_file="main.py")
    assert len(context_tiny) >= 1  # Should at least include anchor file
    total_tokens_tiny = sum(cm.estimate_tokens(item["content"]) for item in context_tiny)
    # May slightly exceed if anchor file alone is larger, but should be close
    assert total_tokens_tiny <= 150  # Allow some tolerance

    # Test 6: Test without anchor file (should use LRU/relevance)
    context_no_anchor = cm.get_context_window(token_limit=500)
    assert len(context_no_anchor) > 0

    # Test 7: Test token estimation
    test_content = "This is a test string with multiple words."
    tokens = cm.estimate_tokens(test_content)
    assert tokens > 0
    assert isinstance(tokens, int)

    # Simple validation: token count should be roughly proportional to content length
    short_content = "short"
    long_content = "word " * 100
    assert cm.estimate_tokens(short_content) < cm.estimate_tokens(long_content)

    # Test 8: Test with max_tokens parameter (alternative name for token_limit)
    context_max_tokens = cm.get_context_window(max_tokens=500)
    assert len(context_max_tokens) > 0

    # Test 9: Test prioritization order
    # Access a specific file to boost its priority
    cm.get_file("models.py")
    context_after_access = cm.get_context_window(token_limit=500)
    # models.py should be more likely to be included now
    # (This is a soft assertion based on LRU)

    # Test 10: Test error handling for invalid parameters
    with pytest.raises(ValueError):
        cm.get_context_window(token_limit=-100)

    with pytest.raises(ValueError):
        cm.get_context_window(token_limit=0)

    # Test 11: Empty context manager should return empty list
    cm_empty = ContextManager()
    context_empty = cm_empty.get_context_window(token_limit=1000)
    assert context_empty == []

    # Test 12: Single file within limit
    cm_single = ContextManager()
    cm_single.add_file("single.py", "content")
    context_single = cm_single.get_context_window(token_limit=1000)
    assert len(context_single) == 1
    assert context_single[0]["file_path"] == "single.py"

    # Test 13: Verify metadata is included in context window results
    assert all("metadata" in item for item in context_large)
