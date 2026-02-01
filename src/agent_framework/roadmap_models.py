"""
Roadmap data models for strategic development planning.

This module defines the core data structures for creating and managing
development roadmaps with features, milestones, phases, and prioritization.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any


class MoSCoWPriority(Enum):
    """MoSCoW prioritization categories."""
    MUST = "MUST"
    SHOULD = "SHOULD"
    COULD = "COULD"
    WONT = "WONT"


class FeatureStatus(Enum):
    """Feature implementation status."""
    PROPOSED = "proposed"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Feature:
    """
    Represents a feature in the development roadmap.

    Attributes:
        id: Unique identifier for the feature
        name: Human-readable feature name
        description: Detailed feature description
        moscow_priority: MoSCoW prioritization category
        priority_rationale: Explanation for the prioritization decision
        business_value: Business value score (0-100)
        technical_complexity: Technical complexity score (0-100)
        estimated_effort_days: Estimated effort in person-days
        dependencies: List of feature IDs this feature depends on
        competitor_pain_points: List of competitor pain points this addresses
        success_metrics: List of measurable success criteria
        status: Current implementation status
        phase_id: ID of the phase this feature belongs to
        metadata: Additional feature metadata
    """
    id: str
    name: str
    description: str
    moscow_priority: MoSCoWPriority
    priority_rationale: str
    business_value: int = 0
    technical_complexity: int = 0
    estimated_effort_days: float = 0.0
    dependencies: List[str] = field(default_factory=list)
    competitor_pain_points: List[str] = field(default_factory=list)
    success_metrics: List[str] = field(default_factory=list)
    status: FeatureStatus = FeatureStatus.PROPOSED
    phase_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate feature data after initialization."""
        if not 0 <= self.business_value <= 100:
            raise ValueError("business_value must be between 0 and 100")
        if not 0 <= self.technical_complexity <= 100:
            raise ValueError("technical_complexity must be between 0 and 100")
        if self.estimated_effort_days < 0:
            raise ValueError("estimated_effort_days must be non-negative")


@dataclass
class Milestone:
    """
    Represents a milestone in the development roadmap.

    Attributes:
        id: Unique identifier for the milestone
        name: Human-readable milestone name
        description: Detailed milestone description
        target_date: Target completion date
        success_metrics: List of measurable criteria for milestone completion
        features: List of feature IDs included in this milestone
        phase_id: ID of the phase this milestone belongs to
        is_completed: Whether the milestone has been achieved
        completed_date: Actual completion date
        metadata: Additional milestone metadata
    """
    id: str
    name: str
    description: str
    target_date: Optional[datetime] = None
    success_metrics: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    phase_id: Optional[str] = None
    is_completed: bool = False
    completed_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate milestone data after initialization."""
        if self.is_completed and not self.completed_date:
            raise ValueError("completed_date must be set when is_completed is True")
        if not self.success_metrics:
            raise ValueError("Milestone must have at least one success metric")


@dataclass
class Phase:
    """
    Represents a development phase containing related features and milestones.

    Attributes:
        id: Unique identifier for the phase
        name: Human-readable phase name
        description: Detailed phase description
        order: Sequential order of this phase (0-indexed)
        start_date: Planned start date
        end_date: Planned end date
        features: List of feature IDs in this phase
        milestones: List of milestone IDs in this phase
        objectives: List of phase objectives
        success_criteria: List of criteria for phase completion
        status: Current phase status
        metadata: Additional phase metadata
    """
    id: str
    name: str
    description: str
    order: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    features: List[str] = field(default_factory=list)
    milestones: List[str] = field(default_factory=list)
    objectives: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    status: str = "planned"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate phase data after initialization."""
        if self.order < 0:
            raise ValueError("Phase order must be non-negative")
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("Phase start_date must be before end_date")


@dataclass
class Roadmap:
    """
    Main roadmap container organizing features, milestones, and phases.

    Attributes:
        id: Unique identifier for the roadmap
        name: Human-readable roadmap name
        description: Detailed roadmap description
        version: Roadmap version string
        created_at: Roadmap creation timestamp
        updated_at: Last update timestamp
        features: List of all features in the roadmap
        milestones: List of all milestones in the roadmap
        phases: List of all phases in the roadmap
        market_context: Context about market and competitive landscape
        dependencies: Dependency graph mapping feature relationships
        success_metrics: Overall roadmap success metrics
        metadata: Additional roadmap metadata
    """
    id: str
    name: str
    description: str
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    features: List[Feature] = field(default_factory=list)
    milestones: List[Milestone] = field(default_factory=list)
    phases: List[Phase] = field(default_factory=list)
    market_context: Dict[str, Any] = field(default_factory=dict)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    success_metrics: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate roadmap data after initialization."""
        # Sort phases by order
        self.phases.sort(key=lambda p: p.order)

    def get_feature_by_id(self, feature_id: str) -> Optional[Feature]:
        """Get a feature by its ID."""
        for feature in self.features:
            if feature.id == feature_id:
                return feature
        return None

    def get_milestone_by_id(self, milestone_id: str) -> Optional[Milestone]:
        """Get a milestone by its ID."""
        for milestone in self.milestones:
            if milestone.id == milestone_id:
                return milestone
        return None

    def get_phase_by_id(self, phase_id: str) -> Optional[Phase]:
        """Get a phase by its ID."""
        for phase in self.phases:
            if phase.id == phase_id:
                return phase
        return None

    def get_features_by_priority(self, priority: MoSCoWPriority) -> List[Feature]:
        """Get all features with a specific MoSCoW priority."""
        return [f for f in self.features if f.moscow_priority == priority]

    def get_features_by_phase(self, phase_id: str) -> List[Feature]:
        """Get all features in a specific phase."""
        return [f for f in self.features if f.phase_id == phase_id]

    def validate_dependencies(self) -> bool:
        """
        Validate that all feature dependencies are resolvable.

        Returns:
            True if all dependencies are valid, False otherwise
        """
        feature_ids = {f.id for f in self.features}

        for feature in self.features:
            for dep_id in feature.dependencies:
                if dep_id not in feature_ids:
                    return False

        return True

    def has_circular_dependencies(self) -> bool:
        """
        Check if the roadmap has circular dependencies.

        Returns:
            True if circular dependencies exist, False otherwise
        """
        def has_cycle(feature_id: str, visited: set, rec_stack: set) -> bool:
            visited.add(feature_id)
            rec_stack.add(feature_id)

            feature = self.get_feature_by_id(feature_id)
            if feature:
                for dep_id in feature.dependencies:
                    if dep_id not in visited:
                        if has_cycle(dep_id, visited, rec_stack):
                            return True
                    elif dep_id in rec_stack:
                        return True

            rec_stack.remove(feature_id)
            return False

        visited = set()
        rec_stack = set()

        for feature in self.features:
            if feature.id not in visited:
                if has_cycle(feature.id, visited, rec_stack):
                    return True

        return False
