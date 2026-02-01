"""
Prioritization engine for MoSCoW categorization and feature ranking.

This module provides the PrioritizationEngine class for assigning MoSCoW
priorities to features, analyzing dependencies, and generating rationale
for prioritization decisions.
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from agent_framework.prioritization_models import (
    Priority,
    MoSCoWCategory,
    DependencyGraph
)
from agent_framework.roadmap_models import Feature, MoSCoWPriority

if TYPE_CHECKING:
    from agent_framework.logging import AgentLogger

# Export DependencyGraph so it can be imported from this module
__all__ = ['PrioritizationEngine', 'DependencyGraph', 'Priority', 'MoSCoWCategory']


class PrioritizationEngine:
    """
    Engine for prioritizing features using MoSCoW methodology.

    The PrioritizationEngine analyzes features based on business value,
    technical complexity, risk, and dependencies to assign appropriate
    MoSCoW categories and generate prioritization rationale.

    Attributes:
        logger: Optional logger for tracing prioritization operations.
        _priorities: Internal cache of Priority objects by item ID.
    """

    def __init__(self, logger: Optional["AgentLogger"] = None):
        """
        Initialize the prioritization engine.

        Args:
            logger: Optional logger for tracing prioritization operations.
        """
        self.logger = logger
        self._priorities: Dict[str, Priority] = {}

    def _log(self, level: str, message: str, **extra) -> None:
        """
        Internal helper to safely log messages if logger is available.

        Args:
            level: Log level (debug, info, warning, error, critical).
            message: The message to log.
            **extra: Additional context to include in the log.
        """
        if self.logger is not None:
            log_method = getattr(self.logger, level.lower(), None)
            if log_method is not None:
                log_method(message, component="PrioritizationEngine", **extra)

    def categorize_feature(
        self,
        feature: Feature,
        business_value: int = None,
        technical_complexity: int = None,
        risk_level: int = 0
    ) -> MoSCoWCategory:
        """
        Assign a MoSCoW category to a feature based on scoring.

        Args:
            feature: The feature to categorize
            business_value: Business value score (0-100), defaults to feature.business_value
            technical_complexity: Complexity score (0-100), defaults to feature.technical_complexity
            risk_level: Risk assessment score (0-100)

        Returns:
            The assigned MoSCoW category

        Raises:
            ValueError: If scores are out of valid range
        """
        self._log("debug", f"Categorizing feature: {feature.id}")

        # Use feature values if not explicitly provided
        bv = business_value if business_value is not None else feature.business_value
        tc = technical_complexity if technical_complexity is not None else feature.technical_complexity

        # Create Priority object
        priority = Priority(
            item_id=feature.id,
            moscow_category=MoSCoWCategory.COULD_HAVE,  # Default, will be updated
            business_value=bv,
            technical_complexity=tc,
            risk_level=risk_level,
            effort_estimate_days=feature.estimated_effort_days
        )

        # Calculate priority score
        priority.calculate_priority_score()

        # Update MoSCoW category based on score
        moscow_category = priority.update_moscow_from_score()

        # Cache the priority
        self._priorities[feature.id] = priority

        self._log("info", f"Feature {feature.id} categorized as {moscow_category.value}",
                  priority_score=priority.priority_score)

        return moscow_category

    def categorize_features(
        self,
        features: List[Feature],
        scoring_overrides: Optional[Dict[str, Dict[str, int]]] = None
    ) -> Dict[str, MoSCoWCategory]:
        """
        Categorize multiple features at once.

        Args:
            features: List of features to categorize
            scoring_overrides: Optional dict mapping feature IDs to score overrides
                             (keys: business_value, technical_complexity, risk_level)

        Returns:
            Dictionary mapping feature IDs to MoSCoW categories
        """
        self._log("info", f"Categorizing {len(features)} features")

        results = {}
        overrides = scoring_overrides or {}

        for feature in features:
            override = overrides.get(feature.id, {})
            category = self.categorize_feature(
                feature,
                business_value=override.get('business_value'),
                technical_complexity=override.get('technical_complexity'),
                risk_level=override.get('risk_level', 0)
            )
            results[feature.id] = category

        return results

    def get_priority(self, item_id: str) -> Optional[Priority]:
        """
        Get the Priority object for a previously categorized item.

        Args:
            item_id: The item ID to look up

        Returns:
            The Priority object if found, None otherwise
        """
        return self._priorities.get(item_id)

    def get_features_by_category(
        self,
        features: List[Feature],
        category: MoSCoWCategory
    ) -> List[Feature]:
        """
        Filter features by MoSCoW category.

        Args:
            features: List of features to filter
            category: The MoSCoW category to filter by

        Returns:
            List of features matching the category
        """
        # Map MoSCoWCategory to MoSCoWPriority for comparison
        priority_map = {
            MoSCoWCategory.MUST_HAVE: MoSCoWPriority.MUST,
            MoSCoWCategory.SHOULD_HAVE: MoSCoWPriority.SHOULD,
            MoSCoWCategory.COULD_HAVE: MoSCoWPriority.COULD,
            MoSCoWCategory.WONT_HAVE: MoSCoWPriority.WONT
        }

        target_priority = priority_map.get(category)
        if target_priority is None:
            return []

        return [f for f in features if f.moscow_priority == target_priority]

    def validate_dependencies(
        self,
        features: List[Feature]
    ) -> tuple[bool, List[str]]:
        """
        Validate feature dependencies to prevent impossible sequences.

        Args:
            features: List of features to validate

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        self._log("debug", f"Validating dependencies for {len(features)} features")

        # Create dependency graph
        graph = DependencyGraph(
            graph_id="validation",
            name="Feature Dependency Validation"
        )

        # Add all features as nodes
        for feature in features:
            graph.add_node(feature.id, {
                "name": feature.name,
                "priority": feature.moscow_priority.value
            })

        # Add dependency edges
        errors = []
        for feature in features:
            for dep_id in feature.dependencies:
                try:
                    graph.add_dependency(feature.id, dep_id)
                except ValueError as e:
                    errors.append(str(e))

        # Validate the graph
        is_valid, validation_errors = graph.validate()
        errors.extend(validation_errors)

        if errors:
            self._log("warning", f"Dependency validation failed with {len(errors)} errors")
        else:
            self._log("info", "Dependency validation passed")

        return len(errors) == 0, errors

    def get_execution_order(
        self,
        features: List[Feature]
    ) -> Optional[List[List[str]]]:
        """
        Get optimal execution order for features respecting dependencies.

        Args:
            features: List of features to order

        Returns:
            List of lists where each inner list contains feature IDs that can
            be executed in parallel, or None if dependencies are invalid
        """
        self._log("debug", f"Computing execution order for {len(features)} features")

        # Create dependency graph
        graph = DependencyGraph(
            graph_id="execution",
            name="Feature Execution Order"
        )

        # Add all features as nodes
        for feature in features:
            graph.add_node(feature.id)

        # Add dependency edges (skip invalid dependencies)
        for feature in features:
            for dep_id in feature.dependencies:
                try:
                    graph.add_dependency(feature.id, dep_id)
                except ValueError:
                    # Skip dependencies that would create cycles
                    self._log("warning", f"Skipping cyclic dependency: {feature.id} -> {dep_id}")

        # Get execution order
        execution_order = graph.get_execution_order()

        if execution_order:
            self._log("info", f"Computed execution order with {len(execution_order)} levels")
        else:
            self._log("error", "Failed to compute execution order - graph has cycles")

        return execution_order

    def generate_rationale(
        self,
        item_id: str,
        moscow_category: str
    ) -> str:
        """
        Generate a human-readable rationale for a prioritization decision.

        Args:
            item_id: The item ID to generate rationale for
            moscow_category: The MoSCoW category (MUST, SHOULD, COULD, WONT)

        Returns:
            A human-readable rationale explaining the prioritization decision
        """
        self._log("debug", f"Generating rationale for {item_id} with category {moscow_category}")

        # Map string category to enum
        category_map = {
            'MUST': MoSCoWCategory.MUST_HAVE,
            'SHOULD': MoSCoWCategory.SHOULD_HAVE,
            'COULD': MoSCoWCategory.COULD_HAVE,
            'WONT': MoSCoWCategory.WONT_HAVE
        }

        category_enum = category_map.get(moscow_category.upper())
        if category_enum is None:
            return f"Invalid MoSCoW category: {moscow_category}"

        # Check if we have cached priority data
        priority = self._priorities.get(item_id)

        if priority is not None:
            # Generate rationale based on actual priority data
            rationale_parts = []

            # Category justification
            category_justifications = {
                MoSCoWCategory.MUST_HAVE: "This item is categorized as MUST HAVE due to its critical importance",
                MoSCoWCategory.SHOULD_HAVE: "This item is categorized as SHOULD HAVE as it provides significant value",
                MoSCoWCategory.COULD_HAVE: "This item is categorized as COULD HAVE as it offers additional benefits",
                MoSCoWCategory.WONT_HAVE: "This item is categorized as WON'T HAVE for this release cycle"
            }
            rationale_parts.append(category_justifications[category_enum])

            # Business value assessment
            if priority.business_value >= 80:
                rationale_parts.append(f"with exceptionally high business value (score: {priority.business_value}/100)")
            elif priority.business_value >= 60:
                rationale_parts.append(f"with strong business value (score: {priority.business_value}/100)")
            elif priority.business_value >= 40:
                rationale_parts.append(f"with moderate business value (score: {priority.business_value}/100)")
            else:
                rationale_parts.append(f"with limited business value (score: {priority.business_value}/100)")

            # Technical complexity consideration
            if priority.technical_complexity >= 80:
                rationale_parts.append(f"However, it has high technical complexity (score: {priority.technical_complexity}/100)")
            elif priority.technical_complexity >= 60:
                rationale_parts.append(f"It has moderate technical complexity (score: {priority.technical_complexity}/100)")
            else:
                rationale_parts.append(f"It has relatively low technical complexity (score: {priority.technical_complexity}/100)")

            # Risk assessment
            if priority.risk_level >= 60:
                rationale_parts.append(f"and carries significant risk (score: {priority.risk_level}/100)")
            elif priority.risk_level >= 30:
                rationale_parts.append(f"with manageable risk (score: {priority.risk_level}/100)")
            elif priority.risk_level > 0:
                rationale_parts.append(f"with low risk (score: {priority.risk_level}/100)")

            # Overall priority score
            rationale_parts.append(f"The overall priority score is {priority.priority_score}/100.")

            rationale = ". ".join(rationale_parts)

        else:
            # Generate generic rationale without cached data
            category_rationales = {
                MoSCoWCategory.MUST_HAVE: (
                    f"Item '{item_id}' is categorized as MUST HAVE, indicating it is essential "
                    "for the project's success and must be delivered in this release. "
                    "MUST HAVE items are non-negotiable and critical to core functionality."
                ),
                MoSCoWCategory.SHOULD_HAVE: (
                    f"Item '{item_id}' is categorized as SHOULD HAVE, indicating it is important "
                    "but not vital for this release. SHOULD HAVE items add significant value "
                    "and should be included if possible, but the project can succeed without them."
                ),
                MoSCoWCategory.COULD_HAVE: (
                    f"Item '{item_id}' is categorized as COULD HAVE, indicating it is desirable "
                    "but not necessary. COULD HAVE items will be included if time and resources "
                    "permit, but can be easily deferred to a future release."
                ),
                MoSCoWCategory.WONT_HAVE: (
                    f"Item '{item_id}' is categorized as WON'T HAVE for this release, meaning "
                    "it has been agreed that it will not be delivered in this timeframe. "
                    "It may be reconsidered for future releases."
                )
            }
            rationale = category_rationales[category_enum]

        self._log("info", f"Generated rationale for {item_id}", rationale_length=len(rationale))
        return rationale

    def __repr__(self) -> str:
        """Return a string representation of the engine."""
        return f"PrioritizationEngine(cached_priorities={len(self._priorities)})"

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"PrioritizationEngine with {len(self._priorities)} cached priority assessments"
