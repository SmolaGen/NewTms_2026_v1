"""
Tests for the prioritization engine and models.

This module tests the PrioritizationEngine class, Priority dataclass,
and DependencyGraph for MoSCoW categorization, dependency management,
and priority scoring.
"""

import pytest
from typing import Dict, Any

from agent_framework.prioritization import PrioritizationEngine, DependencyGraph
from agent_framework.prioritization_models import Priority, MoSCoWCategory
from agent_framework.roadmap_models import Feature, MoSCoWPriority, FeatureStatus


class TestPriorityModel:
    """Test suite for Priority dataclass."""

    def test_priority_initialization(self):
        """Test that Priority initializes with correct attributes."""
        priority = Priority(
            item_id="feat-1",
            moscow_category=MoSCoWCategory.MUST_HAVE,
            business_value=80,
            technical_complexity=40,
            risk_level=20
        )

        assert priority.item_id == "feat-1"
        assert priority.moscow_category == MoSCoWCategory.MUST_HAVE
        assert priority.business_value == 80
        assert priority.technical_complexity == 40
        assert priority.risk_level == 20
        assert priority.priority_score == 0.0

    def test_priority_validation_business_value(self):
        """Test that business_value validation works correctly."""
        # Valid values
        Priority(item_id="test", moscow_category=MoSCoWCategory.COULD_HAVE, business_value=0)
        Priority(item_id="test", moscow_category=MoSCoWCategory.COULD_HAVE, business_value=100)
        Priority(item_id="test", moscow_category=MoSCoWCategory.COULD_HAVE, business_value=50)

        # Invalid values
        with pytest.raises(ValueError, match="business_value must be between 0 and 100"):
            Priority(item_id="test", moscow_category=MoSCoWCategory.COULD_HAVE, business_value=101)

        with pytest.raises(ValueError, match="business_value must be between 0 and 100"):
            Priority(item_id="test", moscow_category=MoSCoWCategory.COULD_HAVE, business_value=-1)

    def test_priority_validation_technical_complexity(self):
        """Test that technical_complexity validation works correctly."""
        # Valid values
        Priority(item_id="test", moscow_category=MoSCoWCategory.COULD_HAVE, technical_complexity=0)
        Priority(item_id="test", moscow_category=MoSCoWCategory.COULD_HAVE, technical_complexity=100)

        # Invalid values
        with pytest.raises(ValueError, match="technical_complexity must be between 0 and 100"):
            Priority(item_id="test", moscow_category=MoSCoWCategory.COULD_HAVE, technical_complexity=150)

    def test_priority_validation_risk_level(self):
        """Test that risk_level validation works correctly."""
        # Valid values
        Priority(item_id="test", moscow_category=MoSCoWCategory.COULD_HAVE, risk_level=0)
        Priority(item_id="test", moscow_category=MoSCoWCategory.COULD_HAVE, risk_level=100)

        # Invalid values
        with pytest.raises(ValueError, match="risk_level must be between 0 and 100"):
            Priority(item_id="test", moscow_category=MoSCoWCategory.COULD_HAVE, risk_level=-10)

    def test_priority_validation_effort_estimate(self):
        """Test that effort_estimate_days validation works correctly."""
        # Valid values
        Priority(item_id="test", moscow_category=MoSCoWCategory.COULD_HAVE, effort_estimate_days=0)
        Priority(item_id="test", moscow_category=MoSCoWCategory.COULD_HAVE, effort_estimate_days=100.5)

        # Invalid values
        with pytest.raises(ValueError, match="effort_estimate_days must be non-negative"):
            Priority(item_id="test", moscow_category=MoSCoWCategory.COULD_HAVE, effort_estimate_days=-5)

    def test_calculate_priority_score(self):
        """Test priority score calculation."""
        priority = Priority(
            item_id="feat-1",
            moscow_category=MoSCoWCategory.MUST_HAVE,
            business_value=80,
            technical_complexity=40,
            risk_level=20
        )

        score = priority.calculate_priority_score()

        # Score = (80 * 0.5) + ((100 - 40) * 0.3) + ((100 - 20) * 0.2)
        # Score = 40 + 18 + 16 = 74
        assert score == 74.0
        assert priority.priority_score == 74.0

    def test_calculate_priority_score_high_complexity(self):
        """Test priority score with high complexity (should lower score)."""
        priority = Priority(
            item_id="feat-2",
            moscow_category=MoSCoWCategory.COULD_HAVE,
            business_value=60,
            technical_complexity=90,
            risk_level=10
        )

        score = priority.calculate_priority_score()

        # Score = (60 * 0.5) + ((100 - 90) * 0.3) + ((100 - 10) * 0.2)
        # Score = 30 + 3 + 18 = 51
        assert score == 51.0

    def test_calculate_priority_score_high_risk(self):
        """Test priority score with high risk (should lower score)."""
        priority = Priority(
            item_id="feat-3",
            moscow_category=MoSCoWCategory.SHOULD_HAVE,
            business_value=70,
            technical_complexity=30,
            risk_level=80
        )

        score = priority.calculate_priority_score()

        # Score = (70 * 0.5) + ((100 - 30) * 0.3) + ((100 - 80) * 0.2)
        # Score = 35 + 21 + 4 = 60
        assert score == 60.0

    def test_update_moscow_from_score_must_have(self):
        """Test MoSCoW categorization for high priority scores."""
        priority = Priority(
            item_id="feat-1",
            moscow_category=MoSCoWCategory.COULD_HAVE,
            business_value=90,
            technical_complexity=20,
            risk_level=10
        )

        priority.calculate_priority_score()
        category = priority.update_moscow_from_score()

        assert priority.priority_score >= 80
        assert category == MoSCoWCategory.MUST_HAVE
        assert priority.moscow_category == MoSCoWCategory.MUST_HAVE

    def test_update_moscow_from_score_should_have(self):
        """Test MoSCoW categorization for medium-high priority scores."""
        priority = Priority(
            item_id="feat-2",
            moscow_category=MoSCoWCategory.COULD_HAVE,
            business_value=70,
            technical_complexity=40,
            risk_level=30
        )

        priority.calculate_priority_score()
        category = priority.update_moscow_from_score()

        assert 60 <= priority.priority_score < 80
        assert category == MoSCoWCategory.SHOULD_HAVE

    def test_update_moscow_from_score_could_have(self):
        """Test MoSCoW categorization for medium priority scores."""
        priority = Priority(
            item_id="feat-3",
            moscow_category=MoSCoWCategory.MUST_HAVE,
            business_value=50,
            technical_complexity=60,
            risk_level=50
        )

        priority.calculate_priority_score()
        category = priority.update_moscow_from_score()

        assert 40 <= priority.priority_score < 60
        assert category == MoSCoWCategory.COULD_HAVE

    def test_update_moscow_from_score_wont_have(self):
        """Test MoSCoW categorization for low priority scores."""
        priority = Priority(
            item_id="feat-4",
            moscow_category=MoSCoWCategory.MUST_HAVE,
            business_value=20,
            technical_complexity=80,
            risk_level=70
        )

        priority.calculate_priority_score()
        category = priority.update_moscow_from_score()

        assert priority.priority_score < 40
        assert category == MoSCoWCategory.WONT_HAVE


class TestDependencyGraph:
    """Test suite for DependencyGraph dataclass."""

    def test_dependency_graph_initialization(self):
        """Test that DependencyGraph initializes correctly."""
        graph = DependencyGraph(
            graph_id="test-graph",
            name="Test Graph",
            description="A test dependency graph"
        )

        assert graph.graph_id == "test-graph"
        assert graph.name == "Test Graph"
        assert graph.description == "A test dependency graph"
        assert graph.nodes == {}
        assert graph.edges == {}

    def test_add_node(self):
        """Test adding nodes to the graph."""
        graph = DependencyGraph()
        graph.add_node("node1", {"name": "Node 1"})
        graph.add_node("node2")

        assert "node1" in graph.nodes
        assert "node2" in graph.nodes
        assert graph.nodes["node1"] == {"name": "Node 1"}
        assert graph.nodes["node2"] == {}

    def test_add_dependency(self):
        """Test adding dependencies between nodes."""
        graph = DependencyGraph()
        graph.add_node("node1")
        graph.add_node("node2")
        graph.add_dependency("node1", "node2")

        assert "node2" in graph.edges["node1"]
        assert graph.get_dependencies("node1") == ["node2"]

    def test_add_dependency_creates_cycle(self):
        """Test that adding a dependency that creates a cycle raises an error."""
        graph = DependencyGraph()
        graph.add_node("node1")
        graph.add_node("node2")
        graph.add_node("node3")

        graph.add_dependency("node1", "node2")
        graph.add_dependency("node2", "node3")

        # This would create a cycle: node1 -> node2 -> node3 -> node1
        with pytest.raises(ValueError, match="would create a cycle"):
            graph.add_dependency("node3", "node1")

    def test_remove_dependency(self):
        """Test removing dependencies."""
        graph = DependencyGraph()
        graph.add_node("node1")
        graph.add_node("node2")
        graph.add_dependency("node1", "node2")

        assert "node2" in graph.edges["node1"]

        graph.remove_dependency("node1", "node2")

        assert "node2" not in graph.edges["node1"]

    def test_get_dependencies(self):
        """Test getting dependencies for a node."""
        graph = DependencyGraph()
        graph.add_node("node1")
        graph.add_node("node2")
        graph.add_node("node3")
        graph.add_dependency("node1", "node2")
        graph.add_dependency("node1", "node3")

        deps = graph.get_dependencies("node1")

        assert set(deps) == {"node2", "node3"}

    def test_get_dependents(self):
        """Test getting nodes that depend on a given node."""
        graph = DependencyGraph()
        graph.add_node("node1")
        graph.add_node("node2")
        graph.add_node("node3")
        graph.add_dependency("node1", "node2")
        graph.add_dependency("node3", "node2")

        dependents = graph.get_dependents("node2")

        assert set(dependents) == {"node1", "node3"}

    def test_has_cycle_false(self):
        """Test cycle detection on acyclic graph."""
        graph = DependencyGraph()
        graph.add_node("node1")
        graph.add_node("node2")
        graph.add_node("node3")
        graph.add_dependency("node1", "node2")
        graph.add_dependency("node2", "node3")

        assert graph.has_cycle() is False

    def test_has_cycle_true(self):
        """Test cycle detection on cyclic graph."""
        graph = DependencyGraph()
        graph.add_node("node1")
        graph.add_node("node2")
        graph.add_node("node3")

        # Manually create a cycle by bypassing add_dependency validation
        graph.edges["node1"] = ["node2"]
        graph.edges["node2"] = ["node3"]
        graph.edges["node3"] = ["node1"]

        assert graph.has_cycle() is True

    def test_topological_sort(self):
        """Test topological sorting of the graph."""
        graph = DependencyGraph()
        graph.add_node("node1")
        graph.add_node("node2")
        graph.add_node("node3")
        graph.add_dependency("node1", "node2")
        graph.add_dependency("node2", "node3")

        sorted_nodes = graph.topological_sort()

        assert sorted_nodes is not None
        # node3 should come before node2, node2 before node1
        assert sorted_nodes.index("node3") < sorted_nodes.index("node2")
        assert sorted_nodes.index("node2") < sorted_nodes.index("node1")

    def test_topological_sort_with_cycle(self):
        """Test that topological sort returns None for cyclic graphs."""
        graph = DependencyGraph()
        graph.add_node("node1")
        graph.add_node("node2")

        # Create a cycle
        graph.edges["node1"] = ["node2"]
        graph.edges["node2"] = ["node1"]

        sorted_nodes = graph.topological_sort()

        assert sorted_nodes is None

    def test_get_execution_order(self):
        """Test getting execution order grouped by levels."""
        graph = DependencyGraph()
        graph.add_node("a")
        graph.add_node("b")
        graph.add_node("c")
        graph.add_node("d")

        graph.add_dependency("b", "a")
        graph.add_dependency("c", "a")
        graph.add_dependency("d", "b")
        graph.add_dependency("d", "c")

        execution_order = graph.get_execution_order()

        assert execution_order is not None
        assert len(execution_order) == 3

        # Level 0: nodes with no dependencies (a)
        assert set(execution_order[0]) == {"a"}

        # Level 1: nodes depending only on level 0 (b, c)
        assert set(execution_order[1]) == {"b", "c"}

        # Level 2: nodes depending on level 1 (d)
        assert set(execution_order[2]) == {"d"}

    def test_get_execution_order_with_cycle(self):
        """Test that execution order returns None for cyclic graphs."""
        graph = DependencyGraph()
        graph.add_node("node1")
        graph.add_node("node2")

        # Create a cycle
        graph.edges["node1"] = ["node2"]
        graph.edges["node2"] = ["node1"]

        execution_order = graph.get_execution_order()

        assert execution_order is None

    def test_validate_success(self):
        """Test validation of a valid graph."""
        graph = DependencyGraph()
        graph.add_node("node1")
        graph.add_node("node2")
        graph.add_dependency("node1", "node2")

        is_valid, errors = graph.validate()

        assert is_valid is True
        assert errors == []

    def test_validate_with_cycles(self):
        """Test validation detects cycles."""
        graph = DependencyGraph()
        graph.add_node("node1")
        graph.add_node("node2")

        # Create a cycle manually
        graph.edges["node1"] = ["node2"]
        graph.edges["node2"] = ["node1"]

        is_valid, errors = graph.validate()

        assert is_valid is False
        assert "cycles" in errors[0].lower()

    def test_validate_with_dangling_references(self):
        """Test validation detects dangling references."""
        graph = DependencyGraph()
        graph.add_node("node1")

        # Manually add a dependency to a non-existent node
        graph.edges["node1"] = ["non_existent"]

        is_valid, errors = graph.validate()

        assert is_valid is False
        assert any("non-existent" in err.lower() for err in errors)

    def test_is_valid(self):
        """Test is_valid convenience method."""
        graph = DependencyGraph()
        graph.add_node("node1")
        graph.add_node("node2")
        graph.add_dependency("node1", "node2")

        assert graph.is_valid() is True


class TestPrioritizationEngine:
    """Test suite for PrioritizationEngine class."""

    def test_engine_initialization(self):
        """Test that PrioritizationEngine initializes correctly."""
        engine = PrioritizationEngine()

        assert engine.logger is None
        assert engine._priorities == {}

    def test_engine_initialization_with_logger(self):
        """Test initialization with a logger."""
        from agent_framework.logging import AgentLogger

        logger = AgentLogger(name="test-logger")
        engine = PrioritizationEngine(logger=logger)

        assert engine.logger is logger

    def test_categorize_feature(self):
        """Test categorizing a single feature."""
        engine = PrioritizationEngine()
        feature = Feature(
            id="feat-1",
            name="Test Feature",
            description="A test feature",
            moscow_priority=MoSCoWPriority.COULD,
            priority_rationale="",
            business_value=80,
            technical_complexity=30,
            estimated_effort_days=5.0
        )

        category = engine.categorize_feature(feature)

        assert category == MoSCoWCategory.MUST_HAVE
        assert "feat-1" in engine._priorities
        assert engine._priorities["feat-1"].moscow_category == MoSCoWCategory.MUST_HAVE

    def test_categorize_feature_with_overrides(self):
        """Test categorizing a feature with score overrides."""
        engine = PrioritizationEngine()
        feature = Feature(
            id="feat-2",
            name="Test Feature",
            description="A test feature",
            moscow_priority=MoSCoWPriority.MUST,
            priority_rationale="",
            business_value=90,
            technical_complexity=10
        )

        # Override with lower business value
        category = engine.categorize_feature(
            feature,
            business_value=30,
            technical_complexity=80,
            risk_level=70
        )

        # With these overrides, score should be low
        assert category == MoSCoWCategory.WONT_HAVE

    def test_categorize_features_multiple(self):
        """Test categorizing multiple features at once."""
        engine = PrioritizationEngine()
        features = [
            Feature(
                id="feat-1",
                name="Feature 1",
                description="High priority",
                moscow_priority=MoSCoWPriority.MUST,
                priority_rationale="",
                business_value=90,
                technical_complexity=20
            ),
            Feature(
                id="feat-2",
                name="Feature 2",
                description="Low priority",
                moscow_priority=MoSCoWPriority.SHOULD,
                priority_rationale="",
                business_value=30,
                technical_complexity=80
            )
        ]

        results = engine.categorize_features(features)

        assert len(results) == 2
        assert results["feat-1"] == MoSCoWCategory.MUST_HAVE
        assert results["feat-2"] == MoSCoWCategory.WONT_HAVE

    def test_categorize_features_with_overrides(self):
        """Test categorizing features with scoring overrides."""
        engine = PrioritizationEngine()
        features = [
            Feature(
                id="feat-1",
                name="Feature 1",
                description="Feature",
                moscow_priority=MoSCoWPriority.MUST,
                priority_rationale="",
                business_value=50,
                technical_complexity=50
            )
        ]

        overrides = {
            "feat-1": {
                "business_value": 95,
                "technical_complexity": 10,
                "risk_level": 5
            }
        }

        results = engine.categorize_features(features, scoring_overrides=overrides)

        assert results["feat-1"] == MoSCoWCategory.MUST_HAVE

    def test_get_priority(self):
        """Test retrieving cached priority data."""
        engine = PrioritizationEngine()
        feature = Feature(
            id="feat-1",
            name="Test Feature",
            description="A test feature",
            moscow_priority=MoSCoWPriority.MUST,
            priority_rationale="",
            business_value=80,
            technical_complexity=30
        )

        engine.categorize_feature(feature)

        priority = engine.get_priority("feat-1")

        assert priority is not None
        assert priority.item_id == "feat-1"
        assert priority.business_value == 80

    def test_get_priority_not_found(self):
        """Test retrieving priority for non-existent item."""
        engine = PrioritizationEngine()

        priority = engine.get_priority("non-existent")

        assert priority is None

    def test_get_features_by_category(self):
        """Test filtering features by MoSCoW category."""
        engine = PrioritizationEngine()
        features = [
            Feature(
                id="feat-1",
                name="Feature 1",
                description="Must have",
                moscow_priority=MoSCoWPriority.MUST,
                priority_rationale=""
            ),
            Feature(
                id="feat-2",
                name="Feature 2",
                description="Should have",
                moscow_priority=MoSCoWPriority.SHOULD,
                priority_rationale=""
            ),
            Feature(
                id="feat-3",
                name="Feature 3",
                description="Must have",
                moscow_priority=MoSCoWPriority.MUST,
                priority_rationale=""
            )
        ]

        must_haves = engine.get_features_by_category(features, MoSCoWCategory.MUST_HAVE)
        should_haves = engine.get_features_by_category(features, MoSCoWCategory.SHOULD_HAVE)

        assert len(must_haves) == 2
        assert len(should_haves) == 1
        assert all(f.moscow_priority == MoSCoWPriority.MUST for f in must_haves)

    def test_validate_dependencies_valid(self):
        """Test dependency validation with valid dependencies."""
        engine = PrioritizationEngine()
        features = [
            Feature(
                id="feat-1",
                name="Feature 1",
                description="Base feature",
                moscow_priority=MoSCoWPriority.MUST,
                priority_rationale="",
                dependencies=[]
            ),
            Feature(
                id="feat-2",
                name="Feature 2",
                description="Depends on feat-1",
                moscow_priority=MoSCoWPriority.SHOULD,
                priority_rationale="",
                dependencies=["feat-1"]
            )
        ]

        is_valid, errors = engine.validate_dependencies(features)

        assert is_valid is True
        assert errors == []

    def test_validate_dependencies_cyclic(self):
        """Test dependency validation detects cycles."""
        engine = PrioritizationEngine()
        features = [
            Feature(
                id="feat-1",
                name="Feature 1",
                description="Depends on feat-2",
                moscow_priority=MoSCoWPriority.MUST,
                priority_rationale="",
                dependencies=["feat-2"]
            ),
            Feature(
                id="feat-2",
                name="Feature 2",
                description="Depends on feat-1",
                moscow_priority=MoSCoWPriority.SHOULD,
                priority_rationale="",
                dependencies=["feat-1"]
            )
        ]

        is_valid, errors = engine.validate_dependencies(features)

        assert is_valid is False
        assert len(errors) > 0

    def test_get_execution_order(self):
        """Test getting optimal execution order for features."""
        engine = PrioritizationEngine()
        features = [
            Feature(
                id="feat-1",
                name="Feature 1",
                description="Base feature",
                moscow_priority=MoSCoWPriority.MUST,
                priority_rationale="",
                dependencies=[]
            ),
            Feature(
                id="feat-2",
                name="Feature 2",
                description="Depends on feat-1",
                moscow_priority=MoSCoWPriority.SHOULD,
                priority_rationale="",
                dependencies=["feat-1"]
            ),
            Feature(
                id="feat-3",
                name="Feature 3",
                description="Depends on feat-2",
                moscow_priority=MoSCoWPriority.COULD,
                priority_rationale="",
                dependencies=["feat-2"]
            )
        ]

        execution_order = engine.get_execution_order(features)

        assert execution_order is not None
        assert len(execution_order) == 3

        # feat-1 should be in first level
        assert "feat-1" in execution_order[0]

        # feat-2 should be in second level
        assert "feat-2" in execution_order[1]

        # feat-3 should be in third level
        assert "feat-3" in execution_order[2]

    def test_get_execution_order_parallel_execution(self):
        """Test execution order with features that can run in parallel."""
        engine = PrioritizationEngine()
        features = [
            Feature(
                id="feat-1",
                name="Feature 1",
                description="Independent",
                moscow_priority=MoSCoWPriority.MUST,
                priority_rationale="",
                dependencies=[]
            ),
            Feature(
                id="feat-2",
                name="Feature 2",
                description="Independent",
                moscow_priority=MoSCoWPriority.MUST,
                priority_rationale="",
                dependencies=[]
            ),
            Feature(
                id="feat-3",
                name="Feature 3",
                description="Depends on both",
                moscow_priority=MoSCoWPriority.SHOULD,
                priority_rationale="",
                dependencies=["feat-1", "feat-2"]
            )
        ]

        execution_order = engine.get_execution_order(features)

        assert execution_order is not None
        assert len(execution_order) == 2

        # feat-1 and feat-2 can run in parallel
        assert set(execution_order[0]) == {"feat-1", "feat-2"}

        # feat-3 must wait for both
        assert "feat-3" in execution_order[1]

    def test_generate_rationale_with_cached_data(self):
        """Test generating rationale with cached priority data."""
        engine = PrioritizationEngine()
        feature = Feature(
            id="feat-1",
            name="Test Feature",
            description="A test feature",
            moscow_priority=MoSCoWPriority.MUST,
            priority_rationale="",
            business_value=85,
            technical_complexity=40,
            estimated_effort_days=5.0
        )

        engine.categorize_feature(feature, risk_level=25)

        rationale = engine.generate_rationale("feat-1", "MUST")

        assert "MUST HAVE" in rationale
        assert "exceptionally high business value" in rationale
        assert "score: 85/100" in rationale
        assert "technical complexity" in rationale
        assert "score: 40/100" in rationale

    def test_generate_rationale_without_cached_data(self):
        """Test generating generic rationale without cached data."""
        engine = PrioritizationEngine()

        rationale = engine.generate_rationale("unknown-item", "SHOULD")

        assert "SHOULD HAVE" in rationale
        assert "important" in rationale
        assert "unknown-item" in rationale

    def test_generate_rationale_all_categories(self):
        """Test rationale generation for all MoSCoW categories."""
        engine = PrioritizationEngine()

        must_rationale = engine.generate_rationale("item-1", "MUST")
        should_rationale = engine.generate_rationale("item-2", "SHOULD")
        could_rationale = engine.generate_rationale("item-3", "COULD")
        wont_rationale = engine.generate_rationale("item-4", "WONT")

        assert "MUST HAVE" in must_rationale
        assert "essential" in must_rationale

        assert "SHOULD HAVE" in should_rationale
        assert "important" in should_rationale

        assert "COULD HAVE" in could_rationale
        assert "desirable" in could_rationale

        assert "WON'T HAVE" in wont_rationale
        assert "not be delivered" in wont_rationale

    def test_generate_rationale_invalid_category(self):
        """Test rationale generation with invalid category."""
        engine = PrioritizationEngine()

        rationale = engine.generate_rationale("item-1", "INVALID")

        assert "Invalid MoSCoW category" in rationale

    def test_engine_repr(self):
        """Test __repr__ method."""
        engine = PrioritizationEngine()
        feature = Feature(
            id="feat-1",
            name="Test",
            description="Test",
            moscow_priority=MoSCoWPriority.MUST,
            priority_rationale=""
        )

        engine.categorize_feature(feature)

        repr_str = repr(engine)

        assert "PrioritizationEngine" in repr_str
        assert "cached_priorities=1" in repr_str

    def test_engine_str(self):
        """Test __str__ method."""
        engine = PrioritizationEngine()

        str_repr = str(engine)

        assert "PrioritizationEngine" in str_repr
        assert "0 cached priority assessments" in str_repr


class TestMoSCoWCategoryEnum:
    """Test suite for MoSCoWCategory enumeration."""

    def test_moscow_category_values(self):
        """Test that MoSCoW categories have correct values."""
        assert MoSCoWCategory.MUST_HAVE.value == "MUST_HAVE"
        assert MoSCoWCategory.SHOULD_HAVE.value == "SHOULD_HAVE"
        assert MoSCoWCategory.COULD_HAVE.value == "COULD_HAVE"
        assert MoSCoWCategory.WONT_HAVE.value == "WONT_HAVE"

    def test_moscow_category_enum_members(self):
        """Test that all expected enum members exist."""
        members = list(MoSCoWCategory)

        assert len(members) == 4
        assert MoSCoWCategory.MUST_HAVE in members
        assert MoSCoWCategory.SHOULD_HAVE in members
        assert MoSCoWCategory.COULD_HAVE in members
        assert MoSCoWCategory.WONT_HAVE in members


class TestPrioritizationEngineWithLogger:
    """Test suite for PrioritizationEngine logging functionality."""

    def test_engine_logs_categorization(self):
        """Test that engine logs categorization operations."""
        from agent_framework.logging import AgentLogger

        logger = AgentLogger(name="test-logger")
        engine = PrioritizationEngine(logger=logger)

        feature = Feature(
            id="feat-1",
            name="Test Feature",
            description="A test feature",
            moscow_priority=MoSCoWPriority.MUST,
            priority_rationale="",
            business_value=80,
            technical_complexity=30
        )

        # This should log without raising errors
        category = engine.categorize_feature(feature)

        assert category is not None

    def test_engine_logs_dependency_validation(self):
        """Test that engine logs dependency validation."""
        from agent_framework.logging import AgentLogger

        logger = AgentLogger(name="test-logger")
        engine = PrioritizationEngine(logger=logger)

        features = [
            Feature(
                id="feat-1",
                name="Feature 1",
                description="Base",
                moscow_priority=MoSCoWPriority.MUST,
                priority_rationale="",
                dependencies=[]
            )
        ]

        # This should log without raising errors
        is_valid, errors = engine.validate_dependencies(features)

        assert is_valid is True
