"""
Competitive analysis data models for market and competitor research.

This module defines the core data structures for analyzing competitors,
identifying pain points, and understanding market dynamics.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any


class MarketPosition(Enum):
    """Market position categories for competitors."""
    LEADER = "leader"
    CHALLENGER = "challenger"
    FOLLOWER = "follower"
    NICHE = "niche"


class PainPointSeverity(Enum):
    """Severity levels for pain points."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PainPointFrequency(Enum):
    """Frequency of pain point occurrence."""
    VERY_COMMON = "very_common"
    COMMON = "common"
    OCCASIONAL = "occasional"
    RARE = "rare"


@dataclass
class PainPoint:
    """
    Represents a pain point or gap in competitor offerings.

    Attributes:
        id: Unique identifier for the pain point
        name: Human-readable pain point name
        description: Detailed description of the pain point
        severity: Impact severity level
        frequency: How often this pain point occurs
        competitor_ids: List of competitor IDs affected by this pain point
        affected_users: Description of affected user segments
        business_impact: Description of business impact
        potential_solution: Proposed solution or opportunity
        evidence: Supporting evidence or data points
        metadata: Additional pain point metadata
    """
    id: str
    name: str
    description: str
    severity: PainPointSeverity
    frequency: PainPointFrequency
    competitor_ids: List[str] = field(default_factory=list)
    affected_users: str = ""
    business_impact: str = ""
    potential_solution: str = ""
    evidence: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate pain point data after initialization."""
        if not self.competitor_ids:
            raise ValueError("PainPoint must be associated with at least one competitor")


@dataclass
class Competitor:
    """
    Represents a competitor in the market.

    Attributes:
        id: Unique identifier for the competitor
        name: Human-readable competitor name
        description: Detailed competitor description
        market_position: Position in the market landscape
        strengths: List of competitor strengths
        weaknesses: List of competitor weaknesses
        features: List of key features offered
        pricing_model: Description of pricing strategy
        target_audience: Description of target customer segments
        market_share: Market share percentage (0-100)
        pain_point_ids: List of pain point IDs associated with this competitor
        url: Competitor website or product URL
        founded_date: Company or product founding date
        metadata: Additional competitor metadata
    """
    id: str
    name: str
    description: str
    market_position: MarketPosition
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    pricing_model: str = ""
    target_audience: str = ""
    market_share: float = 0.0
    pain_point_ids: List[str] = field(default_factory=list)
    url: Optional[str] = None
    founded_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate competitor data after initialization."""
        if not 0 <= self.market_share <= 100:
            raise ValueError("market_share must be between 0 and 100")

    def add_pain_point(self, pain_point_id: str):
        """Add a pain point ID to this competitor."""
        if pain_point_id not in self.pain_point_ids:
            self.pain_point_ids.append(pain_point_id)

    def remove_pain_point(self, pain_point_id: str):
        """Remove a pain point ID from this competitor."""
        if pain_point_id in self.pain_point_ids:
            self.pain_point_ids.remove(pain_point_id)


@dataclass
class Market:
    """
    Represents market analysis and competitive landscape.

    Attributes:
        id: Unique identifier for the market
        name: Human-readable market name
        description: Detailed market description
        total_size: Total addressable market size (TAM) in dollars
        growth_rate: Annual market growth rate percentage
        competitors: List of competitors in the market
        pain_points: List of identified pain points
        trends: List of current market trends
        opportunities: List of market opportunities
        threats: List of market threats
        target_segments: List of target customer segments
        created_at: Market analysis creation timestamp
        updated_at: Last update timestamp
        metadata: Additional market metadata
    """
    id: str
    name: str
    description: str
    total_size: float = 0.0
    growth_rate: float = 0.0
    competitors: List[Competitor] = field(default_factory=list)
    pain_points: List[PainPoint] = field(default_factory=list)
    trends: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    threats: List[str] = field(default_factory=list)
    target_segments: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate market data after initialization."""
        if self.total_size < 0:
            raise ValueError("total_size must be non-negative")

    def get_competitor_by_id(self, competitor_id: str) -> Optional[Competitor]:
        """Get a competitor by its ID."""
        for competitor in self.competitors:
            if competitor.id == competitor_id:
                return competitor
        return None

    def get_pain_point_by_id(self, pain_point_id: str) -> Optional[PainPoint]:
        """Get a pain point by its ID."""
        for pain_point in self.pain_points:
            if pain_point.id == pain_point_id:
                return pain_point
        return None

    def get_competitors_by_position(self, position: MarketPosition) -> List[Competitor]:
        """Get all competitors with a specific market position."""
        return [c for c in self.competitors if c.market_position == position]

    def get_pain_points_by_severity(self, severity: PainPointSeverity) -> List[PainPoint]:
        """Get all pain points with a specific severity level."""
        return [p for p in self.pain_points if p.severity == severity]

    def get_critical_pain_points(self) -> List[PainPoint]:
        """Get all critical and high severity pain points."""
        return [
            p for p in self.pain_points
            if p.severity in (PainPointSeverity.CRITICAL, PainPointSeverity.HIGH)
        ]

    def get_pain_points_for_competitor(self, competitor_id: str) -> List[PainPoint]:
        """Get all pain points associated with a specific competitor."""
        return [
            p for p in self.pain_points
            if competitor_id in p.competitor_ids
        ]

    def add_competitor(self, competitor: Competitor):
        """Add a competitor to the market analysis."""
        if not self.get_competitor_by_id(competitor.id):
            self.competitors.append(competitor)
            self.updated_at = datetime.now()

    def add_pain_point(self, pain_point: PainPoint):
        """Add a pain point to the market analysis."""
        if not self.get_pain_point_by_id(pain_point.id):
            self.pain_points.append(pain_point)
            self.updated_at = datetime.now()

    def calculate_total_market_share(self) -> float:
        """Calculate total market share covered by tracked competitors."""
        return sum(c.market_share for c in self.competitors)
