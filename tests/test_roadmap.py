"""
Tests for the RoadmapGenerator agent.

This module tests the RoadmapGenerator to ensure proper roadmap generation,
feature extraction, phase organization, milestone creation, and pain point mapping.
"""

import pytest
from typing import Any, Dict

from agent_framework.roadmap import RoadmapGenerator
from agent_framework.roadmap_models import (
    Roadmap,
    Feature,
    Milestone,
    Phase,
    MoSCoWPriority,
    FeatureStatus
)
from agent_framework.competitive_models import (
    PainPoint,
    PainPointSeverity,
    PainPointFrequency
)
from agent_framework.context import ContextManager


class TestRoadmapGeneratorInitialization:
    """Test suite for RoadmapGenerator initialization."""

    def test_roadmap_generator_initialization(self):
        """Test that RoadmapGenerator initializes with correct defaults."""
        rg = RoadmapGenerator(name="test_rg")

        assert rg.name == "test_rg"
        assert rg.config == {}
        assert rg._initialized is False
        assert rg._roadmap_cache is None

    def test_roadmap_generator_with_config(self):
        """Test that RoadmapGenerator accepts custom configuration."""
        config = {"max_features": 20, "min_phases": 3}
        rg = RoadmapGenerator(name="test_rg", config=config)

        assert rg.name == "test_rg"
        assert rg.config == config
        assert rg.config["max_features"] == 20

    def test_roadmap_generator_with_context_manager(self):
        """Test that RoadmapGenerator accepts a context manager."""
        cm = ContextManager()
        rg = RoadmapGenerator(name="test_rg", context_manager=cm)

        assert rg.context_manager is cm

    def test_roadmap_generator_repr(self):
        """Test the __repr__ method."""
        rg = RoadmapGenerator(name="test_rg")
        repr_str = repr(rg)

        assert "RoadmapGenerator" in repr_str
        assert "test_rg" in repr_str

    def test_roadmap_generator_str(self):
        """Test the __str__ method."""
        rg = RoadmapGenerator(name="test_rg")
        str_repr = str(rg)

        assert str_repr == "Agent: test_rg"


class TestRoadmapGeneratorExecution:
    """Test suite for RoadmapGenerator execute method."""

    def test_execute_generate_task(self):
        """Test executing the 'generate' task."""
        rg = RoadmapGenerator(name="test_rg")
        context = {
            "name": "Test Roadmap",
            "description": "Test roadmap description"
        }

        result = rg.execute("generate", context=context)

        assert isinstance(result, Roadmap)
        assert result.name == "Test Roadmap"
        assert result.description == "Test roadmap description"
        assert len(result.features) >= 15  # Minimum features
        assert len(result.phases) >= 4  # Minimum phases
        assert len(result.milestones) >= 4  # One per phase

    def test_execute_analyze_codebase_task(self):
        """Test executing the 'analyze_codebase' task."""
        rg = RoadmapGenerator(name="test_rg")
        context = {
            "codebase": {
                "files": ["file1.py", "file2.py"],
                "components": ["module1", "module2"],
                "dependencies": ["dep1 -> dep2"]
            }
        }

        result = rg.execute("analyze_codebase", context=context)

        assert isinstance(result, dict)
        assert "codebase_state" in result
        assert result["codebase_state"]["file_count"] == 2
        assert "components" in result["codebase_state"]
        assert "dependencies" in result["codebase_state"]

    def test_execute_extract_features_task(self):
        """Test executing the 'extract_features' task."""
        rg = RoadmapGenerator(name="test_rg")
        context = {"requirements": {}, "codebase": {}}

        result = rg.execute("extract_features", context=context)

        assert isinstance(result, list)
        assert len(result) >= 15  # Minimum standard features
        assert all(isinstance(f, Feature) for f in result)

    def test_execute_organize_phases_task(self):
        """Test executing the 'organize_phases' task."""
        rg = RoadmapGenerator(name="test_rg")

        # Create sample features
        features = [
            Feature(
                id="f1",
                name="Feature 1",
                description="Test feature",
                moscow_priority=MoSCoWPriority.MUST,
                priority_rationale="Critical",
                dependencies=[]
            ),
            Feature(
                id="f2",
                name="Feature 2",
                description="Test feature 2",
                moscow_priority=MoSCoWPriority.SHOULD,
                priority_rationale="Important",
                dependencies=["f1"]
            )
        ]

        result = rg.execute("organize_phases", features=features)

        assert isinstance(result, list)
        assert len(result) >= 4  # Minimum phases
        assert all(isinstance(p, Phase) for p in result)

    def test_execute_map_pain_points_task(self):
        """Test executing the 'map_pain_points' task."""
        rg = RoadmapGenerator(name="test_rg")

        features = [
            Feature(
                id="f1",
                name="Performance Optimization",
                description="Optimize performance and caching",
                moscow_priority=MoSCoWPriority.MUST,
                priority_rationale="Critical"
            )
        ]

        pain_points = [
            PainPoint(
                id="pp1",
                name="Slow Performance",
                description="Performance is slow",
                severity=PainPointSeverity.HIGH,
                frequency=PainPointFrequency.VERY_COMMON,
                potential_solution="Optimize performance and caching"
            )
        ]

        result = rg.execute("map_pain_points", features=features, pain_points=pain_points)

        assert isinstance(result, list)
        assert all(isinstance(f, Feature) for f in result)
        # Should have mapped the pain point
        assert any(f.competitor_pain_points for f in result)

    def test_execute_create_milestones_task(self):
        """Test executing the 'create_milestones' task."""
        rg = RoadmapGenerator(name="test_rg")

        phases = [
            Phase(
                id="phase-1",
                name="Foundation",
                description="Core infrastructure",
                order=1,
                features=["f1", "f2"],
                success_criteria=["Criterion 1", "Criterion 2"]
            )
        ]

        result = rg.execute("create_milestones", phases=phases)

        assert isinstance(result, list)
        assert len(result) == 1
        assert all(isinstance(m, Milestone) for m in result)
        assert result[0].phase_id == "phase-1"
        assert len(result[0].success_metrics) > 0

    def test_execute_unknown_task(self):
        """Test executing an unknown task returns error."""
        rg = RoadmapGenerator(name="test_rg")

        result = rg.execute("unknown_task")

        assert isinstance(result, dict)
        assert "error" in result
        assert "Unknown task" in result["error"]


class TestProcessContext:
    """Test suite for context processing."""

    def test_process_context_basic(self):
        """Test basic context processing."""
        rg = RoadmapGenerator(name="test_rg")
        context = {
            "codebase": {"files": ["file1.py"]},
            "competitors": [{"name": "Competitor 1"}],
            "market": {"size": "large"},
            "requirements": {"req1": "Requirement 1"},
            "constraints": {"time": "6 months"}
        }

        processed = rg.process_context(context)

        assert processed["codebase"] == {"files": ["file1.py"]}
        assert processed["competitors"] == [{"name": "Competitor 1"}]
        assert processed["market"] == {"size": "large"}
        assert processed["requirements"] == {"req1": "Requirement 1"}
        assert processed["constraints"] == {"time": "6 months"}

    def test_process_context_missing_keys(self):
        """Test context processing with missing keys uses defaults."""
        rg = RoadmapGenerator(name="test_rg")
        context = {}

        processed = rg.process_context(context)

        assert processed["codebase"] == {}
        assert processed["competitors"] == []
        assert processed["market"] == {}
        assert processed["requirements"] == {}
        assert processed["constraints"] == {}

    def test_process_context_partial_data(self):
        """Test context processing with partial data."""
        rg = RoadmapGenerator(name="test_rg")
        context = {
            "codebase": {"files": ["file1.py"]},
            "market": {"size": "medium"}
        }

        processed = rg.process_context(context)

        assert processed["codebase"] == {"files": ["file1.py"]}
        assert processed["market"] == {"size": "medium"}
        assert processed["competitors"] == []
        assert processed["requirements"] == {}


class TestFormatResponse:
    """Test suite for response formatting."""

    def test_format_response_roadmap(self):
        """Test formatting a Roadmap object."""
        rg = RoadmapGenerator(name="test_rg")
        roadmap = Roadmap(
            id="rm1",
            name="Test Roadmap",
            description="Test description",
            features=[],
            phases=[],
            milestones=[]
        )

        formatted = rg.format_response(roadmap)

        assert "Test Roadmap" in formatted
        assert "Test description" in formatted
        assert "Features: 0" in formatted
        assert "Phases: 0" in formatted

    def test_format_response_error(self):
        """Test formatting an error result."""
        rg = RoadmapGenerator(name="test_rg")
        result = {"error": "Something went wrong"}

        formatted = rg.format_response(result)

        assert formatted == "Error: Something went wrong"

    def test_format_response_codebase_state(self):
        """Test formatting codebase state analysis."""
        rg = RoadmapGenerator(name="test_rg")
        result = {
            "codebase_state": {
                "file_count": 10,
                "total_size": 5000,
                "components": ["comp1", "comp2"],
                "dependencies": ["dep1", "dep2"]
            }
        }

        formatted = rg.format_response(result)

        assert "Codebase State Analysis" in formatted
        assert "Files analyzed: 10" in formatted
        assert "Total size: 5000 bytes" in formatted
        assert "Components: 2" in formatted
        assert "Dependencies: 2" in formatted

    def test_format_response_features(self):
        """Test formatting features result."""
        rg = RoadmapGenerator(name="test_rg")
        result = {"features": [1, 2, 3, 4, 5]}

        formatted = rg.format_response(result)

        assert "Extracted 5 features" in formatted

    def test_format_response_phases(self):
        """Test formatting phases result."""
        rg = RoadmapGenerator(name="test_rg")
        result = {"phases": [1, 2, 3, 4]}

        formatted = rg.format_response(result)

        assert "Organized features into 4 phases" in formatted

    def test_format_response_milestones(self):
        """Test formatting milestones result."""
        rg = RoadmapGenerator(name="test_rg")
        result = {"milestones": [1, 2, 3]}

        formatted = rg.format_response(result)

        assert "Created 3 milestones" in formatted


class TestFeatureExtraction:
    """Test suite for feature extraction."""

    def test_extract_features_minimum_count(self):
        """Test that at least 15 features are extracted."""
        rg = RoadmapGenerator(name="test_rg")
        context = {"requirements": {}, "codebase": {}}

        features = rg._extract_features(context)

        assert len(features) >= 15

    def test_extract_features_from_requirements(self):
        """Test extracting features from requirements."""
        rg = RoadmapGenerator(name="test_rg")
        context = {
            "requirements": {
                "req1": {
                    "name": "Custom Feature",
                    "description": "Custom feature description",
                    "moscow_priority": MoSCoWPriority.MUST,
                    "priority_rationale": "Custom rationale",
                    "business_value": 90,
                    "technical_complexity": 70,
                    "estimated_effort_days": 10.0
                }
            }
        }

        features = rg._extract_features(context)

        # Should include the custom feature
        custom_features = [f for f in features if f.id == "req1"]
        assert len(custom_features) == 1
        assert custom_features[0].name == "Custom Feature"
        assert custom_features[0].business_value == 90

    def test_extract_features_standard_features(self):
        """Test that standard features are included."""
        rg = RoadmapGenerator(name="test_rg")
        context = {}

        features = rg._extract_features(context)

        feature_ids = [f.id for f in features]

        # Check for some standard features
        assert "feat-core-architecture" in feature_ids
        assert "feat-auth-system" in feature_ids
        assert "feat-data-layer" in feature_ids

    def test_extract_features_valid_objects(self):
        """Test that all extracted features are valid Feature objects."""
        rg = RoadmapGenerator(name="test_rg")
        context = {}

        features = rg._extract_features(context)

        for feature in features:
            assert isinstance(feature, Feature)
            assert feature.id
            assert feature.name
            assert feature.description
            assert isinstance(feature.moscow_priority, MoSCoWPriority)
            assert feature.priority_rationale
            assert 0 <= feature.business_value <= 100
            assert 0 <= feature.technical_complexity <= 100
            assert feature.estimated_effort_days >= 0


class TestPhaseOrganization:
    """Test suite for phase organization."""

    def test_organize_phases_minimum_count(self):
        """Test that at least 4 phases are created."""
        rg = RoadmapGenerator(name="test_rg")
        features = rg._extract_features({})

        phases = rg._organize_phases(features)

        assert len(phases) >= 4

    def test_organize_phases_correct_order(self):
        """Test that phases are in correct order."""
        rg = RoadmapGenerator(name="test_rg")
        features = rg._extract_features({})

        phases = rg._organize_phases(features)

        orders = [p.order for p in phases]
        assert orders == sorted(orders)
        assert orders[0] == 1

    def test_organize_phases_must_haves_first(self):
        """Test that MUST-have features are in early phases."""
        rg = RoadmapGenerator(name="test_rg")

        features = [
            Feature(
                id="must1",
                name="Must Feature",
                description="Must have",
                moscow_priority=MoSCoWPriority.MUST,
                priority_rationale="Critical",
                dependencies=[]
            ),
            Feature(
                id="could1",
                name="Could Feature",
                description="Could have",
                moscow_priority=MoSCoWPriority.COULD,
                priority_rationale="Nice to have"
            )
        ]

        phases = rg._organize_phases(features)

        # Find which phase contains each feature
        must_phase_order = None
        could_phase_order = None

        for phase in phases:
            if "must1" in phase.features:
                must_phase_order = phase.order
            if "could1" in phase.features:
                could_phase_order = phase.order

        # MUST features should come in earlier phases than COULD features
        if must_phase_order and could_phase_order:
            assert must_phase_order <= could_phase_order

    def test_organize_phases_assigns_phase_id(self):
        """Test that features are assigned phase_id."""
        rg = RoadmapGenerator(name="test_rg")
        features = rg._extract_features({})

        phases = rg._organize_phases(features)

        # Check that features have been assigned phase_id
        for feature in features:
            if any(feature.id in phase.features for phase in phases):
                assert feature.phase_id is not None

    def test_organize_phases_all_have_objectives(self):
        """Test that all phases have objectives."""
        rg = RoadmapGenerator(name="test_rg")
        features = rg._extract_features({})

        phases = rg._organize_phases(features)

        for phase in phases:
            assert len(phase.objectives) > 0
            assert len(phase.success_criteria) > 0


class TestMilestoneCreation:
    """Test suite for milestone creation."""

    def test_create_milestones_one_per_phase(self):
        """Test that one milestone is created per phase."""
        rg = RoadmapGenerator(name="test_rg")
        phases = [
            Phase(
                id="phase-1",
                name="Phase 1",
                description="First phase",
                order=1,
                features=["f1"],
                success_criteria=["Criterion 1"]
            ),
            Phase(
                id="phase-2",
                name="Phase 2",
                description="Second phase",
                order=2,
                features=["f2"],
                success_criteria=["Criterion 2"]
            )
        ]

        milestones = rg._create_milestones(phases)

        assert len(milestones) == 2

    def test_create_milestones_valid_objects(self):
        """Test that all milestones are valid Milestone objects."""
        rg = RoadmapGenerator(name="test_rg")
        phases = [
            Phase(
                id="phase-1",
                name="Foundation",
                description="Core infrastructure",
                order=1,
                features=["f1", "f2"],
                success_criteria=["Criterion 1", "Criterion 2"]
            )
        ]

        milestones = rg._create_milestones(phases)

        for milestone in milestones:
            assert isinstance(milestone, Milestone)
            assert milestone.id
            assert milestone.name
            assert milestone.description
            assert len(milestone.success_metrics) > 0
            assert milestone.phase_id

    def test_create_milestones_links_to_phase(self):
        """Test that milestones are linked to their phases."""
        rg = RoadmapGenerator(name="test_rg")
        phases = [
            Phase(
                id="phase-test",
                name="Test Phase",
                description="Test phase",
                order=1,
                features=["f1"],
                success_criteria=["Criterion"]
            )
        ]

        milestones = rg._create_milestones(phases)

        assert milestones[0].phase_id == "phase-test"

    def test_create_milestones_includes_features(self):
        """Test that milestones include feature references."""
        rg = RoadmapGenerator(name="test_rg")
        phases = [
            Phase(
                id="phase-1",
                name="Phase 1",
                description="First phase",
                order=1,
                features=["f1", "f2", "f3"],
                success_criteria=["Criterion"]
            )
        ]

        milestones = rg._create_milestones(phases)

        assert len(milestones[0].features) == 3
        assert "f1" in milestones[0].features
        assert "f2" in milestones[0].features


class TestPainPointMapping:
    """Test suite for pain point mapping."""

    def test_map_pain_points_keyword_matching(self):
        """Test pain point mapping with keyword matching."""
        rg = RoadmapGenerator(name="test_rg")

        features = [
            Feature(
                id="f1",
                name="Authentication System",
                description="Implement authentication and authorization",
                moscow_priority=MoSCoWPriority.MUST,
                priority_rationale="Security critical"
            )
        ]

        pain_points = [
            PainPoint(
                id="pp1",
                name="Complex Authentication",
                description="Authentication system is difficult",
                severity=PainPointSeverity.HIGH,
                frequency=PainPointFrequency.COMMON,
                potential_solution="Simplified authentication system"
            )
        ]

        result = rg._map_pain_points(features, pain_points)

        # Should map the pain point to the feature
        assert len(result[0].competitor_pain_points) > 0
        assert "pp1" in result[0].competitor_pain_points

    def test_map_pain_points_no_pain_points(self):
        """Test mapping with no pain points returns unchanged features."""
        rg = RoadmapGenerator(name="test_rg")

        features = [
            Feature(
                id="f1",
                name="Feature 1",
                description="Test feature",
                moscow_priority=MoSCoWPriority.MUST,
                priority_rationale="Important"
            )
        ]

        result = rg._map_pain_points(features, [])

        assert result == features

    def test_map_pain_points_solution_matching(self):
        """Test pain point mapping via solution matching."""
        rg = RoadmapGenerator(name="test_rg")

        features = [
            Feature(
                id="f1",
                name="Mobile App",
                description="Build mobile application",
                moscow_priority=MoSCoWPriority.COULD,
                priority_rationale="Platform expansion"
            )
        ]

        pain_points = [
            PainPoint(
                id="pp1",
                name="No Mobile",
                description="Lack of mobile support",
                severity=PainPointSeverity.HIGH,
                frequency=PainPointFrequency.COMMON,
                potential_solution="Mobile application development"
            )
        ]

        result = rg._map_pain_points(features, pain_points)

        # Should map via solution keywords
        assert "pp1" in result[0].competitor_pain_points

    def test_map_pain_points_preserves_existing(self):
        """Test that mapping preserves existing pain points."""
        rg = RoadmapGenerator(name="test_rg")

        features = [
            Feature(
                id="f1",
                name="Performance Optimization",
                description="Optimize performance",
                moscow_priority=MoSCoWPriority.MUST,
                priority_rationale="Critical",
                competitor_pain_points=["existing-pp"]
            )
        ]

        pain_points = [
            PainPoint(
                id="pp1",
                name="Slow Performance",
                description="Performance issues",
                severity=PainPointSeverity.HIGH,
                frequency=PainPointFrequency.VERY_COMMON,
                potential_solution="Performance optimization"
            )
        ]

        result = rg._map_pain_points(features, pain_points)

        # Should include both existing and new pain points
        assert "existing-pp" in result[0].competitor_pain_points
        assert "pp1" in result[0].competitor_pain_points


class TestKeywordExtraction:
    """Test suite for keyword extraction."""

    def test_extract_keywords_basic(self):
        """Test basic keyword extraction."""
        rg = RoadmapGenerator(name="test_rg")
        text = "Authentication and authorization system"

        keywords = rg._extract_keywords(text)

        assert "authentication" in keywords
        assert "authorization" in keywords
        assert "system" in keywords

    def test_extract_keywords_filters_stop_words(self):
        """Test that stop words are filtered."""
        rg = RoadmapGenerator(name="test_rg")
        text = "The authentication system is very important"

        keywords = rg._extract_keywords(text)

        assert "the" not in keywords
        assert "is" not in keywords
        assert "authentication" in keywords
        assert "system" in keywords

    def test_extract_keywords_handles_hyphens(self):
        """Test that hyphens are handled correctly."""
        rg = RoadmapGenerator(name="test_rg")
        text = "real-time notification system"

        keywords = rg._extract_keywords(text)

        assert "real" in keywords
        assert "time" in keywords
        assert "notification" in keywords

    def test_extract_keywords_lowercase(self):
        """Test that keywords are lowercased."""
        rg = RoadmapGenerator(name="test_rg")
        text = "Authentication SYSTEM Performance"

        keywords = rg._extract_keywords(text)

        assert "authentication" in keywords
        assert "system" in keywords
        assert "performance" in keywords
        # Should not have uppercase versions
        assert "Authentication" not in keywords


class TestCodebaseAnalysis:
    """Test suite for codebase analysis."""

    def test_analyze_codebase_with_context_manager(self):
        """Test codebase analysis with context manager."""
        cm = ContextManager()
        cm.add_file("src/module1/file1.py", "code content 1")
        cm.add_file("src/module2/file2.py", "code content 2")

        rg = RoadmapGenerator(name="test_rg", context_manager=cm)
        result = rg.analyze_codebase_state()

        assert "codebase_state" in result
        assert result["codebase_state"]["file_count"] == 2
        assert result["codebase_state"]["total_size"] > 0

    def test_analyze_codebase_without_context_manager(self):
        """Test codebase analysis without context manager."""
        rg = RoadmapGenerator(name="test_rg")
        context = {
            "codebase": {
                "files": ["file1.py", "file2.py"],
                "components": ["comp1"],
                "dependencies": ["dep1"]
            }
        }

        result = rg._analyze_codebase_state(context)

        assert "codebase_state" in result
        assert result["codebase_state"]["file_count"] == 2

    def test_identify_components(self):
        """Test component identification from file paths."""
        rg = RoadmapGenerator(name="test_rg")
        files = [
            "src/agent_framework/agent.py",
            "src/agent_framework/context.py",
            "src/tools/tool1.py",
            "src/tools/tool2.py"
        ]

        components = rg._identify_components(files)

        assert "agent_framework" in components
        assert "tools" in components

    def test_extract_dependencies(self):
        """Test dependency extraction."""
        cm = ContextManager()
        cm.add_file("file1.py", "import file2")
        cm.add_file("file2.py", "import file3")
        cm.add_related_file("file1.py", "file2.py")

        rg = RoadmapGenerator(name="test_rg", context_manager=cm)

        dependencies = rg._extract_dependencies(["file1.py", "file2.py"])

        # Should extract dependencies from relationships
        assert isinstance(dependencies, list)


class TestExtractPainPoints:
    """Test suite for pain point extraction."""

    def test_extract_pain_points_from_competitors(self):
        """Test extracting pain points from competitor data."""
        rg = RoadmapGenerator(name="test_rg")

        competitors = [
            {
                "name": "Competitor 1",
                "pain_points": [
                    {
                        "id": "pp1",
                        "name": "Slow Load Times",
                        "description": "Pages load slowly",
                        "severity": PainPointSeverity.HIGH,
                        "frequency": PainPointFrequency.VERY_COMMON,
                        "competitor_ids": ["comp1"]
                    }
                ]
            }
        ]

        pain_points = rg._extract_pain_points(competitors)

        assert len(pain_points) > 0
        assert any(pp.id == "pp1" for pp in pain_points)

    def test_extract_pain_points_generates_common_when_empty(self):
        """Test that common pain points are generated when none provided."""
        rg = RoadmapGenerator(name="test_rg")

        pain_points = rg._extract_pain_points([])

        # Should generate common industry pain points
        assert len(pain_points) > 0
        pain_point_ids = [pp.id for pp in pain_points]
        assert "pp-slow-performance" in pain_point_ids
        assert "pp-complex-auth" in pain_point_ids


class TestPublicMethods:
    """Test suite for public convenience methods."""

    def test_generate_roadmap_with_context(self):
        """Test public generate_roadmap method with context."""
        rg = RoadmapGenerator(name="test_rg")
        context = {
            "name": "Product Roadmap",
            "description": "Q1 2024 roadmap"
        }

        roadmap = rg.generate_roadmap(context)

        assert isinstance(roadmap, Roadmap)
        assert roadmap.name == "Product Roadmap"
        assert len(roadmap.features) >= 15
        assert len(roadmap.phases) >= 4

    def test_generate_roadmap_without_context(self):
        """Test public generate_roadmap method without context."""
        rg = RoadmapGenerator(name="test_rg")

        roadmap = rg.generate_roadmap()

        assert isinstance(roadmap, Roadmap)
        assert roadmap.name == "Development Roadmap"  # Default name
        assert len(roadmap.features) >= 15

    def test_generate_roadmap_caches_result(self):
        """Test that roadmap is cached after generation."""
        rg = RoadmapGenerator(name="test_rg")

        assert rg._roadmap_cache is None

        roadmap = rg.generate_roadmap()

        assert rg._roadmap_cache is not None
        assert rg._roadmap_cache == roadmap


class TestRoadmapIntegration:
    """Test suite for full roadmap generation integration."""

    def test_full_roadmap_generation_workflow(self):
        """Test complete roadmap generation workflow."""
        rg = RoadmapGenerator(name="test_rg")

        context = {
            "name": "Full Stack App Roadmap",
            "description": "Complete development roadmap for full stack application",
            "requirements": {
                "custom1": {
                    "name": "Custom Auth",
                    "description": "Custom authentication feature",
                    "moscow_priority": MoSCoWPriority.MUST,
                    "priority_rationale": "Security requirement",
                    "business_value": 95,
                    "technical_complexity": 65,
                    "estimated_effort_days": 8.0
                }
            }
        }

        roadmap = rg.generate_roadmap(context)

        # Verify roadmap structure
        assert isinstance(roadmap, Roadmap)
        assert roadmap.name == "Full Stack App Roadmap"

        # Verify features
        assert len(roadmap.features) >= 15
        custom_features = [f for f in roadmap.features if f.id == "custom1"]
        assert len(custom_features) == 1

        # Verify phases
        assert len(roadmap.phases) >= 4
        phase_names = [p.name for p in roadmap.phases]
        assert "Foundation" in phase_names

        # Verify milestones
        assert len(roadmap.milestones) >= 4
        for milestone in roadmap.milestones:
            assert len(milestone.success_metrics) > 0
            assert milestone.phase_id is not None

        # Verify dependencies are valid
        assert roadmap.validate_dependencies()

        # Verify no circular dependencies
        assert not roadmap.has_circular_dependencies()

    def test_roadmap_with_pain_points(self):
        """Test roadmap generation with pain point mapping."""
        rg = RoadmapGenerator(name="test_rg")

        context = {
            "competitors": [
                {
                    "name": "Competitor A",
                    "pain_points": [
                        {
                            "id": "pp-auth",
                            "name": "Complex Auth",
                            "description": "Authentication is too complex",
                            "severity": PainPointSeverity.MEDIUM,
                            "frequency": PainPointFrequency.COMMON,
                            "competitor_ids": ["comp-a"],
                            "potential_solution": "Simplified authentication system"
                        }
                    ]
                }
            ]
        }

        roadmap = rg.generate_roadmap(context)

        # Should have mapped some pain points to features
        features_with_pain_points = [
            f for f in roadmap.features if f.competitor_pain_points
        ]
        assert len(features_with_pain_points) > 0

    def test_roadmap_format_output(self):
        """Test formatted roadmap output."""
        rg = RoadmapGenerator(name="test_rg")
        roadmap = rg.generate_roadmap()

        formatted = rg.format_response(roadmap)

        assert "Roadmap:" in formatted
        assert "Features:" in formatted
        assert "Phases:" in formatted
        assert "Milestones:" in formatted


class TestEdgeCases:
    """Test suite for edge cases and error handling."""

    def test_empty_features_list(self):
        """Test organizing phases with empty features list."""
        rg = RoadmapGenerator(name="test_rg")

        phases = rg._organize_phases([])

        # Should still create phases
        assert len(phases) >= 4

    def test_single_feature(self):
        """Test organizing phases with single feature."""
        rg = RoadmapGenerator(name="test_rg")

        features = [
            Feature(
                id="f1",
                name="Only Feature",
                description="The only feature",
                moscow_priority=MoSCoWPriority.MUST,
                priority_rationale="Critical"
            )
        ]

        phases = rg._organize_phases(features)

        assert len(phases) >= 4
        # Feature should be in one of the phases
        assert any("f1" in phase.features for phase in phases)

    def test_feature_with_invalid_dependency(self):
        """Test that features with invalid dependencies still work."""
        rg = RoadmapGenerator(name="test_rg")

        features = [
            Feature(
                id="f1",
                name="Feature 1",
                description="First feature",
                moscow_priority=MoSCoWPriority.MUST,
                priority_rationale="Important",
                dependencies=["nonexistent-feature"]
            )
        ]

        # Should not raise error
        phases = rg._organize_phases(features)
        assert len(phases) >= 4
