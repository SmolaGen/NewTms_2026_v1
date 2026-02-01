"""
Tests for the CompetitiveAnalyzer agent.

This module tests the CompetitiveAnalyzer to ensure proper competitive
analysis, pain point extraction, market gap identification, and
competitor analysis functionality.
"""

import pytest
from typing import List

from agent_framework.competitive_analysis import CompetitiveAnalyzer
from agent_framework.competitive_models import (
    Competitor,
    PainPoint,
    Market,
    PainPointSeverity,
    PainPointFrequency,
    MarketPosition
)


class TestCompetitiveAnalyzerInitialization:
    """Test suite for CompetitiveAnalyzer initialization."""

    def test_analyzer_initialization(self):
        """Test that CompetitiveAnalyzer initializes with correct defaults."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        assert analyzer.name == "test_analyzer"
        assert analyzer.config == {}
        assert analyzer._market_data is None
        assert analyzer._initialized is False

    def test_analyzer_initialization_with_config(self):
        """Test that CompetitiveAnalyzer accepts custom config parameter."""
        config = {"analysis_depth": "deep", "include_trends": True}
        analyzer = CompetitiveAnalyzer(name="test_analyzer", config=config)

        assert analyzer.name == "test_analyzer"
        assert analyzer.config == config
        assert analyzer._market_data is None

    def test_analyzer_is_agent_subclass(self):
        """Test that CompetitiveAnalyzer is a proper Agent subclass."""
        from agent_framework.agent import Agent

        analyzer = CompetitiveAnalyzer(name="test_analyzer")
        assert isinstance(analyzer, Agent)

    def test_analyzer_repr(self):
        """Test the __repr__ method."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")
        repr_str = repr(analyzer)

        assert "CompetitiveAnalyzer" in repr_str
        assert "test_analyzer" in repr_str

    def test_analyzer_str(self):
        """Test the __str__ method."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")
        str_repr = str(analyzer)

        assert str_repr == "Agent: test_analyzer"


class TestProcessContext:
    """Test suite for context processing."""

    def test_process_context_basic(self):
        """Test that process_context processes basic context correctly."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        context = {
            "competitors": ["comp1", "comp2"],
            "pain_points": ["pain1", "pain2"],
            "market_data": {"size": 1000},
            "focus_areas": ["area1", "area2"]
        }

        processed = analyzer.process_context(context)

        assert processed["competitors"] == ["comp1", "comp2"]
        assert processed["pain_points"] == ["pain1", "pain2"]
        assert processed["market_data"] == {"size": 1000}
        assert processed["focus_areas"] == ["area1", "area2"]

    def test_process_context_with_defaults(self):
        """Test that process_context handles missing fields with defaults."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        context = {}
        processed = analyzer.process_context(context)

        assert processed["competitors"] == []
        assert processed["pain_points"] == []
        assert processed["market_data"] == {}
        assert processed["focus_areas"] == []

    def test_process_context_with_market_object(self):
        """Test that process_context loads Market objects into internal state."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        market = Market(
            id="market1",
            name="Test Market",
            description="A test market"
        )

        context = {"market": market}
        processed = analyzer.process_context(context)

        assert analyzer._market_data is market

    def test_process_context_does_not_modify_original(self):
        """Test that process_context doesn't modify the original context."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        original_context = {
            "competitors": ["comp1"],
            "pain_points": ["pain1"]
        }

        processed = analyzer.process_context(original_context)
        processed["competitors"].append("comp2")

        assert len(original_context["competitors"]) == 1


class TestFormatResponse:
    """Test suite for response formatting."""

    def test_format_response_with_error(self):
        """Test formatting of error responses."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        result = {"error": "Something went wrong"}
        formatted = analyzer.format_response(result)

        assert formatted == "Error: Something went wrong"

    def test_format_response_with_pain_points(self):
        """Test formatting of pain points results."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        pain_point = PainPoint(
            id="pp1",
            name="Test Pain Point",
            description="A test pain point",
            severity=PainPointSeverity.HIGH,
            frequency=PainPointFrequency.COMMON,
            competitor_ids=["comp1"]
        )

        result = {"pain_points": [pain_point]}
        formatted = analyzer.format_response(result)

        assert "Found 1 pain points:" in formatted
        assert "[HIGH] Test Pain Point: A test pain point" in formatted

    def test_format_response_with_empty_pain_points(self):
        """Test formatting when no pain points are found."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        result = {"pain_points": []}
        formatted = analyzer.format_response(result)

        assert formatted == "No pain points found"

    def test_format_response_with_competitor_analysis(self):
        """Test formatting of competitor analysis results."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        result = {
            "competitor_analysis": {
                "name": "CompanyX",
                "position": "leader",
                "weaknesses": ["weakness1", "weakness2"],
                "pain_points": ["pp1", "pp2"]
            }
        }

        formatted = analyzer.format_response(result)

        assert "Competitor Analysis: CompanyX" in formatted
        assert "Position: leader" in formatted
        assert "Weaknesses: 2" in formatted
        assert "Pain Points: 2" in formatted

    def test_format_response_with_market_gaps(self):
        """Test formatting of market gaps results."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        result = {"market_gaps": ["gap1", "gap2", "gap3"]}
        formatted = analyzer.format_response(result)

        assert "Identified 3 market gaps:" in formatted
        assert "gap1" in formatted
        assert "gap2" in formatted
        assert "gap3" in formatted

    def test_format_response_with_empty_market_gaps(self):
        """Test formatting when no market gaps are identified."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        result = {"market_gaps": []}
        formatted = analyzer.format_response(result)

        assert formatted == "No market gaps identified"

    def test_format_response_with_loaded_market_data(self):
        """Test formatting of market data load results."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        result = {"loaded": True, "competitors": 5, "pain_points": 10}
        formatted = analyzer.format_response(result)

        assert "Market data loaded: 5 competitors, 10 pain points" in formatted

    def test_format_response_with_generic_dict(self):
        """Test formatting of generic dictionary results."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        result = {"some_key": "some_value"}
        formatted = analyzer.format_response(result)

        assert formatted == str(result)

    def test_format_response_with_non_dict(self):
        """Test formatting of non-dictionary results."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        result = "plain string result"
        formatted = analyzer.format_response(result)

        assert formatted == "plain string result"


class TestLoadMarketData:
    """Test suite for loading market data."""

    def test_load_market_data_success(self):
        """Test successfully loading market data."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        competitor = Competitor(
            id="comp1",
            name="Competitor 1",
            description="First competitor",
            market_position=MarketPosition.LEADER
        )

        pain_point = PainPoint(
            id="pp1",
            name="Pain Point 1",
            description="First pain point",
            severity=PainPointSeverity.HIGH,
            frequency=PainPointFrequency.COMMON,
            competitor_ids=["comp1"]
        )

        market = Market(
            id="market1",
            name="Test Market",
            description="A test market",
            competitors=[competitor],
            pain_points=[pain_point]
        )

        result = analyzer.execute("load_market_data", market=market)

        assert result["loaded"] is True
        assert result["market_id"] == "market1"
        assert result["competitors"] == 1
        assert result["pain_points"] == 1
        assert analyzer._market_data is market

    def test_load_market_data_none(self):
        """Test loading None market data returns error."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        result = analyzer.execute("load_market_data", market=None)

        assert "error" in result
        assert result["error"] == "No market data provided"

    def test_load_market_data_invalid_type(self):
        """Test loading invalid market data type returns error."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        result = analyzer.execute("load_market_data", market="not a market")

        assert "error" in result
        assert result["error"] == "Invalid market data type"


class TestExtractPainPoints:
    """Test suite for pain point extraction."""

    def test_extract_pain_points_all(self):
        """Test extracting all pain points from market data."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        pain_points = [
            PainPoint(
                id="pp1",
                name="Critical Pain",
                description="A critical issue",
                severity=PainPointSeverity.CRITICAL,
                frequency=PainPointFrequency.VERY_COMMON,
                competitor_ids=["comp1"]
            ),
            PainPoint(
                id="pp2",
                name="High Pain",
                description="A high severity issue",
                severity=PainPointSeverity.HIGH,
                frequency=PainPointFrequency.COMMON,
                competitor_ids=["comp1"]
            ),
            PainPoint(
                id="pp3",
                name="Low Pain",
                description="A low severity issue",
                severity=PainPointSeverity.LOW,
                frequency=PainPointFrequency.RARE,
                competitor_ids=["comp1"]
            )
        ]

        market = Market(
            id="market1",
            name="Test Market",
            description="Test",
            pain_points=pain_points
        )

        analyzer.execute("load_market_data", market=market)
        result = analyzer.execute("extract_pain_points", min_severity=PainPointSeverity.MEDIUM)

        assert result["count"] == 2  # Critical and High only
        assert len(result["pain_points"]) == 2

    def test_extract_pain_points_by_severity(self):
        """Test extracting pain points filtered by severity."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        pain_points = [
            PainPoint(
                id="pp1",
                name="Critical Pain",
                description="Critical",
                severity=PainPointSeverity.CRITICAL,
                frequency=PainPointFrequency.COMMON,
                competitor_ids=["comp1"]
            ),
            PainPoint(
                id="pp2",
                name="Medium Pain",
                description="Medium",
                severity=PainPointSeverity.MEDIUM,
                frequency=PainPointFrequency.COMMON,
                competitor_ids=["comp1"]
            )
        ]

        market = Market(
            id="market1",
            name="Test Market",
            description="Test",
            pain_points=pain_points
        )

        analyzer.execute("load_market_data", market=market)
        result = analyzer.execute("extract_pain_points", min_severity=PainPointSeverity.CRITICAL)

        assert result["count"] == 1
        assert result["pain_points"][0].severity == PainPointSeverity.CRITICAL

    def test_extract_pain_points_by_competitor(self):
        """Test extracting pain points for a specific competitor."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        pain_points = [
            PainPoint(
                id="pp1",
                name="Pain 1",
                description="Pain for comp1",
                severity=PainPointSeverity.HIGH,
                frequency=PainPointFrequency.COMMON,
                competitor_ids=["comp1"]
            ),
            PainPoint(
                id="pp2",
                name="Pain 2",
                description="Pain for comp2",
                severity=PainPointSeverity.HIGH,
                frequency=PainPointFrequency.COMMON,
                competitor_ids=["comp2"]
            )
        ]

        market = Market(
            id="market1",
            name="Test Market",
            description="Test",
            pain_points=pain_points
        )

        analyzer.execute("load_market_data", market=market)
        result = analyzer.execute("extract_pain_points", competitor_id="comp1")

        assert result["count"] == 1
        assert result["competitor_id"] == "comp1"
        assert result["pain_points"][0].competitor_ids == ["comp1"]

    def test_extract_pain_points_without_market_data(self):
        """Test extracting pain points without loaded market data returns error."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        result = analyzer.execute("extract_pain_points")

        assert "error" in result
        assert result["error"] == "No market data loaded"


class TestAnalyzeCompetitor:
    """Test suite for competitor analysis."""

    def test_analyze_competitor_success(self):
        """Test successfully analyzing a competitor."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        competitor = Competitor(
            id="comp1",
            name="Competitor 1",
            description="First competitor",
            market_position=MarketPosition.LEADER,
            market_share=30.0,
            strengths=["strength1", "strength2"],
            weaknesses=["weakness1"],
            features=["feature1", "feature2"]
        )

        pain_point = PainPoint(
            id="pp1",
            name="Pain 1",
            description="Competitor pain",
            severity=PainPointSeverity.HIGH,
            frequency=PainPointFrequency.COMMON,
            competitor_ids=["comp1"]
        )

        market = Market(
            id="market1",
            name="Test Market",
            description="Test",
            competitors=[competitor],
            pain_points=[pain_point]
        )

        analyzer.execute("load_market_data", market=market)
        result = analyzer.execute("analyze_competitor", competitor_id="comp1")

        assert "competitor_analysis" in result
        analysis = result["competitor_analysis"]
        assert analysis["id"] == "comp1"
        assert analysis["name"] == "Competitor 1"
        assert analysis["position"] == "leader"
        assert analysis["market_share"] == 30.0
        assert len(analysis["strengths"]) == 2
        assert len(analysis["weaknesses"]) == 1
        assert len(analysis["features"]) == 2
        assert analysis["pain_point_count"] == 1

    def test_analyze_competitor_without_market_data(self):
        """Test analyzing competitor without loaded market data returns error."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        result = analyzer.execute("analyze_competitor", competitor_id="comp1")

        assert "error" in result
        assert result["error"] == "No market data loaded"

    def test_analyze_competitor_without_id(self):
        """Test analyzing competitor without ID returns error."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        market = Market(
            id="market1",
            name="Test Market",
            description="Test"
        )

        analyzer.execute("load_market_data", market=market)
        result = analyzer.execute("analyze_competitor", competitor_id=None)

        assert "error" in result
        assert result["error"] == "competitor_id is required"

    def test_analyze_competitor_not_found(self):
        """Test analyzing non-existent competitor returns error."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        market = Market(
            id="market1",
            name="Test Market",
            description="Test"
        )

        analyzer.execute("load_market_data", market=market)
        result = analyzer.execute("analyze_competitor", competitor_id="nonexistent")

        assert "error" in result
        assert "Competitor not found" in result["error"]


class TestGetCriticalPainPoints:
    """Test suite for getting critical pain points."""

    def test_get_critical_pain_points_success(self):
        """Test getting critical pain points."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        pain_points = [
            PainPoint(
                id="pp1",
                name="Critical Pain",
                description="Critical",
                severity=PainPointSeverity.CRITICAL,
                frequency=PainPointFrequency.COMMON,
                competitor_ids=["comp1"]
            ),
            PainPoint(
                id="pp2",
                name="High Pain",
                description="High",
                severity=PainPointSeverity.HIGH,
                frequency=PainPointFrequency.COMMON,
                competitor_ids=["comp1"]
            ),
            PainPoint(
                id="pp3",
                name="Medium Pain",
                description="Medium",
                severity=PainPointSeverity.MEDIUM,
                frequency=PainPointFrequency.COMMON,
                competitor_ids=["comp1"]
            )
        ]

        market = Market(
            id="market1",
            name="Test Market",
            description="Test",
            pain_points=pain_points
        )

        analyzer.execute("load_market_data", market=market)
        result = analyzer.execute("get_critical_pain_points")

        assert result["count"] == 2
        assert len(result["pain_points"]) == 2
        assert all(
            pp.severity in (PainPointSeverity.CRITICAL, PainPointSeverity.HIGH)
            for pp in result["pain_points"]
        )

    def test_get_critical_pain_points_without_market_data(self):
        """Test getting critical pain points without market data returns error."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        result = analyzer.execute("get_critical_pain_points")

        assert "error" in result
        assert result["error"] == "No market data loaded"


class TestIdentifyMarketGaps:
    """Test suite for identifying market gaps."""

    def test_identify_market_gaps_all(self):
        """Test identifying all market gaps."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        pain_points = [
            PainPoint(
                id="pp1",
                name="Critical Gap",
                description="Critical gap",
                severity=PainPointSeverity.CRITICAL,
                frequency=PainPointFrequency.COMMON,
                competitor_ids=["comp1"],
                potential_solution="Build feature X"
            ),
            PainPoint(
                id="pp2",
                name="High Gap",
                description="High gap",
                severity=PainPointSeverity.HIGH,
                frequency=PainPointFrequency.COMMON,
                competitor_ids=["comp1"]
            )
        ]

        market = Market(
            id="market1",
            name="Test Market",
            description="Test",
            pain_points=pain_points,
            opportunities=["opportunity1", "opportunity2"]
        )

        analyzer.execute("load_market_data", market=market)
        result = analyzer.execute("identify_gaps")

        assert result["count"] == 4  # 2 pain points + 2 opportunities
        assert len(result["market_gaps"]) == 4
        assert "Critical Gap: Build feature X" in result["market_gaps"]

    def test_identify_market_gaps_with_focus_area(self):
        """Test identifying market gaps with focus area filter."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        pain_points = [
            PainPoint(
                id="pp1",
                name="Authentication Gap",
                description="Auth issues",
                severity=PainPointSeverity.CRITICAL,
                frequency=PainPointFrequency.COMMON,
                competitor_ids=["comp1"]
            ),
            PainPoint(
                id="pp2",
                name="Storage Gap",
                description="Storage issues",
                severity=PainPointSeverity.HIGH,
                frequency=PainPointFrequency.COMMON,
                competitor_ids=["comp1"]
            )
        ]

        market = Market(
            id="market1",
            name="Test Market",
            description="Test",
            pain_points=pain_points
        )

        analyzer.execute("load_market_data", market=market)
        result = analyzer.execute("identify_gaps", focus_area="authentication")

        assert result["count"] == 1
        assert "Authentication Gap" in result["market_gaps"][0]

    def test_identify_market_gaps_without_market_data(self):
        """Test identifying gaps without market data returns error."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        result = analyzer.execute("identify_gaps")

        assert "error" in result
        assert result["error"] == "No market data loaded"


class TestIdentifyGapsMethod:
    """Test suite for the identify_gaps public method."""

    def test_identify_gaps_with_competitors(self):
        """Test identifying gaps from competitor list."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        competitors = [
            Competitor(
                id="comp1",
                name="Competitor 1",
                description="First competitor",
                market_position=MarketPosition.LEADER,
                weaknesses=["Poor UX", "Slow performance"]
            ),
            Competitor(
                id="comp2",
                name="Competitor 2",
                description="Second competitor",
                market_position=MarketPosition.CHALLENGER,
                weaknesses=["Limited features"]
            )
        ]

        gaps = analyzer.identify_gaps(competitors)

        assert len(gaps) == 3
        assert "Competitor 1: Poor UX" in gaps
        assert "Competitor 1: Slow performance" in gaps
        assert "Competitor 2: Limited features" in gaps

    def test_identify_gaps_with_focus_area(self):
        """Test identifying gaps with focus area filter."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        competitors = [
            Competitor(
                id="comp1",
                name="Competitor 1",
                description="First competitor",
                market_position=MarketPosition.LEADER,
                weaknesses=["Poor UX design", "Slow API performance"]
            )
        ]

        gaps = analyzer.identify_gaps(competitors, focus_area="performance")

        assert len(gaps) == 1
        assert "Slow API performance" in gaps[0]

    def test_identify_gaps_with_empty_competitors(self):
        """Test identifying gaps with empty competitor list."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        gaps = analyzer.identify_gaps([])

        assert gaps == []

    def test_identify_gaps_with_none_raises_error(self):
        """Test that None competitors parameter raises ValueError."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        with pytest.raises(ValueError) as exc_info:
            analyzer.identify_gaps(None)

        assert "competitors parameter cannot be None" in str(exc_info.value)

    def test_identify_gaps_with_market_data(self):
        """Test identifying gaps when market data is loaded."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        pain_points = [
            PainPoint(
                id="pp1",
                name="Gap 1",
                description="First gap",
                severity=PainPointSeverity.CRITICAL,
                frequency=PainPointFrequency.COMMON,
                competitor_ids=["comp1"],
                potential_solution="Solution 1"
            )
        ]

        market = Market(
            id="market1",
            name="Test Market",
            description="Test",
            pain_points=pain_points,
            opportunities=["opportunity1"]
        )

        analyzer.execute("load_market_data", market=market)
        gaps = analyzer.identify_gaps([])

        assert len(gaps) == 2
        assert "Gap 1: Solution 1" in gaps
        assert "opportunity1" in gaps


class TestExtractPainPointsFromCompetitor:
    """Test suite for extracting pain points from competitor."""

    def test_extract_pain_points_from_competitor_basic(self):
        """Test extracting pain points from a competitor's weaknesses."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        competitor = Competitor(
            id="comp1",
            name="Competitor 1",
            description="First competitor",
            market_position=MarketPosition.LEADER,
            weaknesses=["Weakness 1", "Weakness 2"]
        )

        pain_points = analyzer.extract_pain_points_from_competitor(competitor)

        assert len(pain_points) == 2
        assert all(isinstance(pp, PainPoint) for pp in pain_points)
        assert pain_points[0].id == "comp1-weakness-0"
        assert pain_points[1].id == "comp1-weakness-1"
        assert pain_points[0].name == "Competitor 1: Weakness 1"
        assert pain_points[0].description == "Weakness 1"
        assert pain_points[0].competitor_ids == ["comp1"]

    def test_extract_pain_points_from_competitor_long_weakness(self):
        """Test that long weakness names are truncated in pain point name."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        long_weakness = "This is a very long weakness description that should be truncated in the name"

        competitor = Competitor(
            id="comp1",
            name="Competitor 1",
            description="First competitor",
            market_position=MarketPosition.LEADER,
            weaknesses=[long_weakness]
        )

        pain_points = analyzer.extract_pain_points_from_competitor(competitor)

        assert len(pain_points) == 1
        assert len(pain_points[0].name) <= len("Competitor 1: ") + 50
        assert pain_points[0].description == long_weakness

    def test_extract_pain_points_from_competitor_no_weaknesses(self):
        """Test extracting pain points from competitor with no weaknesses."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        competitor = Competitor(
            id="comp1",
            name="Competitor 1",
            description="First competitor",
            market_position=MarketPosition.LEADER,
            weaknesses=[]
        )

        pain_points = analyzer.extract_pain_points_from_competitor(competitor)

        assert len(pain_points) == 0

    def test_extract_pain_points_default_values(self):
        """Test that extracted pain points have correct default values."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        competitor = Competitor(
            id="comp1",
            name="Competitor 1",
            description="First competitor",
            market_position=MarketPosition.LEADER,
            weaknesses=["Weakness 1"]
        )

        pain_points = analyzer.extract_pain_points_from_competitor(competitor)

        assert pain_points[0].severity == PainPointSeverity.MEDIUM
        assert pain_points[0].frequency == PainPointFrequency.COMMON
        assert pain_points[0].affected_users == "Unknown"
        assert pain_points[0].business_impact == "Unknown"
        assert pain_points[0].potential_solution == ""


class TestExecuteMethod:
    """Test suite for the execute method."""

    def test_execute_unknown_task(self):
        """Test that unknown tasks return error."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        result = analyzer.execute("unknown_task")

        assert "error" in result
        assert "Unknown task" in result["error"]

    def test_execute_all_valid_tasks(self):
        """Test that all valid tasks can be executed."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        market = Market(
            id="market1",
            name="Test Market",
            description="Test",
            competitors=[
                Competitor(
                    id="comp1",
                    name="Competitor 1",
                    description="Test",
                    market_position=MarketPosition.LEADER
                )
            ],
            pain_points=[
                PainPoint(
                    id="pp1",
                    name="Pain 1",
                    description="Test",
                    severity=PainPointSeverity.HIGH,
                    frequency=PainPointFrequency.COMMON,
                    competitor_ids=["comp1"]
                )
            ]
        )

        # Test each task type
        result1 = analyzer.execute("load_market_data", market=market)
        assert "loaded" in result1

        result2 = analyzer.execute("extract_pain_points")
        assert "pain_points" in result2

        result3 = analyzer.execute("analyze_competitor", competitor_id="comp1")
        assert "competitor_analysis" in result3

        result4 = analyzer.execute("get_critical_pain_points")
        assert "pain_points" in result4

        result5 = analyzer.execute("identify_gaps")
        assert "market_gaps" in result5


class TestIntegration:
    """Integration tests for CompetitiveAnalyzer."""

    def test_full_competitive_analysis_workflow(self):
        """Test a complete competitive analysis workflow."""
        analyzer = CompetitiveAnalyzer(name="market_analyzer")

        # Create market data
        competitors = [
            Competitor(
                id="comp1",
                name="Market Leader",
                description="Leading competitor",
                market_position=MarketPosition.LEADER,
                market_share=40.0,
                strengths=["Brand recognition", "Large user base"],
                weaknesses=["Poor mobile experience", "Slow feature updates"],
                features=["Feature A", "Feature B"]
            ),
            Competitor(
                id="comp2",
                name="Challenger",
                description="Rising challenger",
                market_position=MarketPosition.CHALLENGER,
                market_share=25.0,
                strengths=["Modern tech stack"],
                weaknesses=["Limited enterprise features"],
                features=["Feature C"]
            )
        ]

        pain_points = [
            PainPoint(
                id="pp1",
                name="Mobile UX Issues",
                description="Poor mobile experience",
                severity=PainPointSeverity.CRITICAL,
                frequency=PainPointFrequency.VERY_COMMON,
                competitor_ids=["comp1"],
                potential_solution="Build native mobile apps"
            ),
            PainPoint(
                id="pp2",
                name="Enterprise Features Gap",
                description="Limited enterprise features",
                severity=PainPointSeverity.HIGH,
                frequency=PainPointFrequency.COMMON,
                competitor_ids=["comp2"],
                potential_solution="Add SAML SSO, RBAC"
            )
        ]

        market = Market(
            id="market1",
            name="SaaS Market",
            description="Enterprise SaaS market",
            total_size=10000000000,
            growth_rate=15.5,
            competitors=competitors,
            pain_points=pain_points,
            opportunities=["AI integration", "Better analytics"]
        )

        # Load market data
        load_result = analyzer.execute("load_market_data", market=market)
        assert load_result["loaded"] is True
        assert load_result["competitors"] == 2
        assert load_result["pain_points"] == 2

        # Extract critical pain points
        critical_result = analyzer.execute("get_critical_pain_points")
        assert critical_result["count"] == 2

        # Analyze specific competitor
        comp_result = analyzer.execute("analyze_competitor", competitor_id="comp1")
        assert comp_result["competitor_analysis"]["name"] == "Market Leader"
        assert comp_result["competitor_analysis"]["market_share"] == 40.0

        # Identify market gaps
        gaps_result = analyzer.execute("identify_gaps")
        assert gaps_result["count"] > 0
        assert any("Mobile UX Issues" in gap for gap in gaps_result["market_gaps"])

        # Format responses
        formatted = analyzer.format_response(gaps_result)
        assert "Identified" in formatted
        assert "market gaps" in formatted

    def test_competitive_analysis_with_context(self):
        """Test competitive analysis with context processing."""
        analyzer = CompetitiveAnalyzer(name="test_analyzer")

        market = Market(
            id="market1",
            name="Test Market",
            description="Test"
        )

        context = {
            "market": market,
            "competitors": ["comp1", "comp2"],
            "focus_areas": ["authentication", "performance"]
        }

        processed = analyzer.process_context(context)

        assert processed["competitors"] == ["comp1", "comp2"]
        assert processed["focus_areas"] == ["authentication", "performance"]
        assert analyzer._market_data is market
