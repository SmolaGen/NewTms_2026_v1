"""
Competitive analysis tools for extracting and analyzing competitor pain points.

This module provides the CompetitiveAnalyzer agent for identifying competitor
weaknesses, extracting pain points, and discovering market gaps that can be
leveraged for strategic advantage.
"""

from typing import Any, Dict, List, Optional
from agent_framework.agent import Agent
from agent_framework.competitive_models import (
    Competitor,
    PainPoint,
    Market,
    PainPointSeverity,
    PainPointFrequency,
    MarketPosition
)


class CompetitiveAnalyzer(Agent):
    """
    An agent that analyzes competitors and extracts actionable pain points.

    This agent provides capabilities for:
    - Extracting pain points from competitor analysis
    - Identifying market gaps and opportunities
    - Analyzing competitor weaknesses
    - Mapping pain points to potential features
    """

    def __init__(
        self,
        name: str,
        config: Optional[Dict[str, Any]] = None,
        tool_registry: Optional[Any] = None,
        context_manager: Optional[Any] = None,
        logger: Optional[Any] = None
    ):
        """
        Initialize the CompetitiveAnalyzer.

        Args:
            name: A unique identifier for this analyzer instance.
            config: Optional configuration dictionary.
            tool_registry: Optional tool registry for managing tools.
            context_manager: Optional context manager for multi-file handling.
            logger: Optional logger for tracing execution.
        """
        super().__init__(name, config, tool_registry, context_manager, logger)
        self._market_data: Optional[Market] = None

    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a competitive analysis task.

        Args:
            task: The analysis task (e.g., "extract_pain_points", "analyze_competitor", "identify_gaps")
            **kwargs: Task-specific parameters

        Returns:
            Dictionary with analysis results
        """
        self._log("info", f"Executing competitive analysis: {task}", task=task)

        if task == "extract_pain_points":
            return self._extract_pain_points(
                competitor_id=kwargs.get("competitor_id"),
                min_severity=kwargs.get("min_severity", PainPointSeverity.MEDIUM)
            )
        elif task == "analyze_competitor":
            return self._analyze_competitor(kwargs.get("competitor_id"))
        elif task == "identify_gaps":
            return self._identify_market_gaps(
                focus_area=kwargs.get("focus_area")
            )
        elif task == "get_critical_pain_points":
            return self._get_critical_pain_points()
        elif task == "load_market_data":
            return self._load_market_data(kwargs.get("market"))
        else:
            return {"error": f"Unknown task: {task}"}

    def process_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process context information for competitive analysis.

        Args:
            context: Raw context with market and competitor data

        Returns:
            Processed context ready for analysis
        """
        processed = {
            "competitors": context.get("competitors", []),
            "pain_points": context.get("pain_points", []),
            "market_data": context.get("market_data", {}),
            "focus_areas": context.get("focus_areas", [])
        }

        # Add market data to internal state if available
        if "market" in context and isinstance(context["market"], Market):
            self._market_data = context["market"]

        return processed

    def format_response(self, result: Any) -> str:
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

            if "pain_points" in result:
                pain_points = result["pain_points"]
                if not pain_points:
                    return "No pain points found"

                output_lines = [f"Found {len(pain_points)} pain points:"]
                for pp in pain_points:
                    if isinstance(pp, PainPoint):
                        output_lines.append(
                            f"  - [{pp.severity.value.upper()}] {pp.name}: {pp.description}"
                        )
                    else:
                        output_lines.append(f"  - {pp}")
                return "\n".join(output_lines)

            if "competitor_analysis" in result:
                analysis = result["competitor_analysis"]
                return (
                    f"Competitor Analysis: {analysis.get('name', 'Unknown')}\n"
                    f"  Position: {analysis.get('position', 'N/A')}\n"
                    f"  Weaknesses: {len(analysis.get('weaknesses', []))}\n"
                    f"  Pain Points: {len(analysis.get('pain_points', []))}"
                )

            if "market_gaps" in result:
                gaps = result["market_gaps"]
                if not gaps:
                    return "No market gaps identified"
                return f"Identified {len(gaps)} market gaps:\n  - " + "\n  - ".join(gaps)

            if "loaded" in result:
                return f"Market data loaded: {result.get('competitors', 0)} competitors, {result.get('pain_points', 0)} pain points"

        return str(result)

    def _load_market_data(self, market: Optional[Market]) -> Dict[str, Any]:
        """Load market data into the analyzer."""
        if market is None:
            return {"error": "No market data provided"}

        if not isinstance(market, Market):
            return {"error": "Invalid market data type"}

        self._market_data = market
        self._log("info", f"Loaded market data: {market.name}", market_id=market.id)

        return {
            "loaded": True,
            "market_id": market.id,
            "competitors": len(market.competitors),
            "pain_points": len(market.pain_points)
        }

    def _extract_pain_points(
        self,
        competitor_id: Optional[str] = None,
        min_severity: PainPointSeverity = PainPointSeverity.MEDIUM
    ) -> Dict[str, Any]:
        """
        Extract pain points from market data.

        Args:
            competitor_id: Optional competitor ID to filter by
            min_severity: Minimum severity level to include

        Returns:
            Dictionary with extracted pain points
        """
        if self._market_data is None:
            return {"error": "No market data loaded"}

        pain_points = []

        # Filter by competitor if specified
        if competitor_id:
            pain_points = self._market_data.get_pain_points_for_competitor(competitor_id)
        else:
            pain_points = self._market_data.pain_points

        # Filter by severity
        severity_order = {
            PainPointSeverity.CRITICAL: 4,
            PainPointSeverity.HIGH: 3,
            PainPointSeverity.MEDIUM: 2,
            PainPointSeverity.LOW: 1
        }
        min_level = severity_order.get(min_severity, 2)
        filtered_pain_points = [
            pp for pp in pain_points
            if severity_order.get(pp.severity, 0) >= min_level
        ]

        self._log(
            "info",
            f"Extracted {len(filtered_pain_points)} pain points",
            count=len(filtered_pain_points),
            competitor_id=competitor_id
        )

        return {
            "pain_points": filtered_pain_points,
            "count": len(filtered_pain_points),
            "competitor_id": competitor_id
        }

    def _analyze_competitor(self, competitor_id: Optional[str]) -> Dict[str, Any]:
        """
        Analyze a specific competitor.

        Args:
            competitor_id: The competitor ID to analyze

        Returns:
            Dictionary with competitor analysis
        """
        if self._market_data is None:
            return {"error": "No market data loaded"}

        if not competitor_id:
            return {"error": "competitor_id is required"}

        competitor = self._market_data.get_competitor_by_id(competitor_id)
        if not competitor:
            return {"error": f"Competitor not found: {competitor_id}"}

        # Get pain points for this competitor
        pain_points = self._market_data.get_pain_points_for_competitor(competitor_id)

        analysis = {
            "competitor_analysis": {
                "id": competitor.id,
                "name": competitor.name,
                "position": competitor.market_position.value,
                "market_share": competitor.market_share,
                "strengths": competitor.strengths,
                "weaknesses": competitor.weaknesses,
                "features": competitor.features,
                "pain_points": pain_points,
                "pain_point_count": len(pain_points)
            }
        }

        self._log(
            "info",
            f"Analyzed competitor: {competitor.name}",
            competitor_id=competitor_id,
            pain_point_count=len(pain_points)
        )

        return analysis

    def _get_critical_pain_points(self) -> Dict[str, Any]:
        """
        Get all critical and high severity pain points.

        Returns:
            Dictionary with critical pain points
        """
        if self._market_data is None:
            return {"error": "No market data loaded"}

        critical_pain_points = self._market_data.get_critical_pain_points()

        self._log(
            "info",
            f"Found {len(critical_pain_points)} critical pain points",
            count=len(critical_pain_points)
        )

        return {
            "pain_points": critical_pain_points,
            "count": len(critical_pain_points)
        }

    def _identify_market_gaps(self, focus_area: Optional[str] = None) -> Dict[str, Any]:
        """
        Identify market gaps based on competitor pain points.

        Args:
            focus_area: Optional area to focus analysis on

        Returns:
            Dictionary with identified market gaps
        """
        if self._market_data is None:
            return {"error": "No market data loaded"}

        gaps = []

        # Extract gaps from pain points
        for pain_point in self._market_data.pain_points:
            if pain_point.severity in (PainPointSeverity.CRITICAL, PainPointSeverity.HIGH):
                if pain_point.potential_solution:
                    gap = f"{pain_point.name}: {pain_point.potential_solution}"
                else:
                    gap = f"{pain_point.name} (Severity: {pain_point.severity.value})"

                # Filter by focus area if specified
                if focus_area:
                    if focus_area.lower() in gap.lower():
                        gaps.append(gap)
                else:
                    gaps.append(gap)

        # Add market opportunities
        if not focus_area:
            gaps.extend(self._market_data.opportunities)

        self._log(
            "info",
            f"Identified {len(gaps)} market gaps",
            count=len(gaps),
            focus_area=focus_area
        )

        return {
            "market_gaps": gaps,
            "count": len(gaps)
        }

    def identify_gaps(
        self,
        competitors: List[Competitor],
        focus_area: Optional[str] = None
    ) -> List[str]:
        """
        Identify market gaps based on competitor analysis.

        This method analyzes a list of competitors and their associated pain points
        to identify market gaps and opportunities. It processes high-severity pain
        points and generates actionable gap descriptions.

        Args:
            competitors: List of Competitor objects to analyze. Can be empty.
            focus_area: Optional area to focus analysis on (filters results).

        Returns:
            List of market gap descriptions as strings. Returns empty list if
            no gaps are identified or no market data is loaded.

        Raises:
            ValueError: If competitors parameter is None.
        """
        if competitors is None:
            raise ValueError("competitors parameter cannot be None")

        # If no market data loaded and no competitors provided, return empty list
        if self._market_data is None and not competitors:
            self._log(
                "debug",
                "No market data or competitors available for gap analysis",
                action="identify_gaps"
            )
            return []

        gaps = []

        # If we have market data, use the internal method
        if self._market_data is not None:
            result = self._identify_market_gaps(focus_area=focus_area)
            if "market_gaps" in result:
                gaps = result["market_gaps"]
        else:
            # Analyze provided competitors directly
            for competitor in competitors:
                for weakness in competitor.weaknesses:
                    # Create gap description from weakness
                    gap_desc = f"{competitor.name}: {weakness}"

                    # Filter by focus area if specified
                    if focus_area:
                        if focus_area.lower() in gap_desc.lower():
                            gaps.append(gap_desc)
                    else:
                        gaps.append(gap_desc)

        # Log gap identification
        self._log(
            "info",
            f"Identified {len(gaps)} market gaps",
            count=len(gaps),
            focus_area=focus_area,
            competitor_count=len(competitors)
        )

        return gaps

    def extract_pain_points_from_competitor(
        self,
        competitor: Competitor
    ) -> List[PainPoint]:
        """
        Extract pain points from a competitor's weaknesses.

        This is a utility method for creating PainPoint objects from
        competitor weakness data.

        Args:
            competitor: The competitor to analyze

        Returns:
            List of PainPoint objects
        """
        pain_points = []

        for idx, weakness in enumerate(competitor.weaknesses):
            pain_point = PainPoint(
                id=f"{competitor.id}-weakness-{idx}",
                name=f"{competitor.name}: {weakness[:50]}",
                description=weakness,
                severity=PainPointSeverity.MEDIUM,  # Default, should be analyzed
                frequency=PainPointFrequency.COMMON,  # Default, should be analyzed
                competitor_ids=[competitor.id],
                affected_users="Unknown",  # Should be determined through analysis
                business_impact="Unknown",  # Should be determined through analysis
                potential_solution=""  # Should be identified through analysis
            )
            pain_points.append(pain_point)

        return pain_points
