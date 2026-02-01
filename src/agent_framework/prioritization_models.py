"""
Prioritization data models for feature and task ranking.

This module defines the core data structures for prioritizing features,
tasks, and managing dependencies in development roadmaps.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Set, Any, Tuple


class MoSCoWCategory(Enum):
    """MoSCoW prioritization categories for features and tasks."""
    MUST_HAVE = "MUST_HAVE"
    SHOULD_HAVE = "SHOULD_HAVE"
    COULD_HAVE = "COULD_HAVE"
    WONT_HAVE = "WONT_HAVE"


@dataclass
class Priority:
    """
    Represents a priority assessment for a feature or task.

    Attributes:
        item_id: Unique identifier for the item being prioritized
        moscow_category: MoSCoW categorization
        priority_score: Calculated priority score (0-100)
        business_value: Business value score (0-100)
        technical_complexity: Technical complexity score (0-100)
        risk_level: Risk assessment score (0-100)
        effort_estimate_days: Estimated effort in person-days
        rationale: Explanation for the prioritization decision
        factors: Dictionary of factors contributing to the priority
        dependencies: List of item IDs this item depends on
        stakeholder_input: Notes from stakeholder prioritization sessions
        last_updated: Timestamp of last priority assessment
        metadata: Additional priority metadata
    """
    item_id: str
    moscow_category: MoSCoWCategory
    priority_score: float = 0.0
    business_value: int = 0
    technical_complexity: int = 0
    risk_level: int = 0
    effort_estimate_days: float = 0.0
    rationale: str = ""
    factors: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    stakeholder_input: str = ""
    last_updated: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate priority data after initialization."""
        if not 0 <= self.priority_score <= 100:
            raise ValueError("priority_score must be between 0 and 100")
        if not 0 <= self.business_value <= 100:
            raise ValueError("business_value must be between 0 and 100")
        if not 0 <= self.technical_complexity <= 100:
            raise ValueError("technical_complexity must be between 0 and 100")
        if not 0 <= self.risk_level <= 100:
            raise ValueError("risk_level must be between 0 and 100")
        if self.effort_estimate_days < 0:
            raise ValueError("effort_estimate_days must be non-negative")

    def calculate_priority_score(self) -> float:
        """
        Calculate priority score based on business value, complexity, and risk.

        Returns:
            Calculated priority score (0-100)
        """
        # Higher business value increases priority
        # Higher complexity decreases priority
        # Higher risk decreases priority
        value_weight = 0.5
        complexity_weight = 0.3
        risk_weight = 0.2

        score = (
            (self.business_value * value_weight) +
            ((100 - self.technical_complexity) * complexity_weight) +
            ((100 - self.risk_level) * risk_weight)
        )

        self.priority_score = round(score, 2)
        return self.priority_score

    def update_moscow_from_score(self) -> MoSCoWCategory:
        """
        Update MoSCoW category based on priority score.

        Returns:
            Updated MoSCoW category
        """
        if self.priority_score >= 80:
            self.moscow_category = MoSCoWCategory.MUST_HAVE
        elif self.priority_score >= 60:
            self.moscow_category = MoSCoWCategory.SHOULD_HAVE
        elif self.priority_score >= 40:
            self.moscow_category = MoSCoWCategory.COULD_HAVE
        else:
            self.moscow_category = MoSCoWCategory.WONT_HAVE

        return self.moscow_category


@dataclass
class DependencyGraph:
    """
    Represents dependency relationships between items (features, tasks, etc.).

    Attributes:
        graph_id: Unique identifier for the dependency graph
        name: Human-readable graph name
        description: Detailed graph description
        nodes: Dictionary mapping item IDs to node metadata
        edges: Dictionary mapping item IDs to lists of dependent item IDs
        metadata: Additional graph metadata
    """
    graph_id: str = "default"
    name: str = "Dependency Graph"
    description: str = ""
    nodes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    edges: Dict[str, List[str]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_node(self, node_id: str, node_data: Optional[Dict[str, Any]] = None):
        """
        Add a node to the dependency graph.

        Args:
            node_id: Unique identifier for the node
            node_data: Optional metadata for the node
        """
        if node_id not in self.nodes:
            self.nodes[node_id] = node_data or {}
        if node_id not in self.edges:
            self.edges[node_id] = []

    def add_dependency(self, from_id: str, to_id: str):
        """
        Add a dependency edge from one item to another.

        Args:
            from_id: ID of the item that depends on another
            to_id: ID of the item being depended upon

        Raises:
            ValueError: If adding the dependency would create a cycle
        """
        # Ensure both nodes exist
        self.add_node(from_id)
        self.add_node(to_id)

        # Check if adding this edge would create a cycle
        if self._would_create_cycle(from_id, to_id):
            raise ValueError(f"Adding dependency from {from_id} to {to_id} would create a cycle")

        # Add the dependency
        if to_id not in self.edges[from_id]:
            self.edges[from_id].append(to_id)

    def remove_dependency(self, from_id: str, to_id: str):
        """
        Remove a dependency edge between two items.

        Args:
            from_id: ID of the item that depends on another
            to_id: ID of the item being depended upon
        """
        if from_id in self.edges and to_id in self.edges[from_id]:
            self.edges[from_id].remove(to_id)

    def get_dependencies(self, node_id: str) -> List[str]:
        """
        Get all direct dependencies for a node.

        Args:
            node_id: ID of the node

        Returns:
            List of item IDs that this node depends on
        """
        return self.edges.get(node_id, [])

    def get_dependents(self, node_id: str) -> List[str]:
        """
        Get all items that depend on this node.

        Args:
            node_id: ID of the node

        Returns:
            List of item IDs that depend on this node
        """
        dependents = []
        for item_id, deps in self.edges.items():
            if node_id in deps:
                dependents.append(item_id)
        return dependents

    def has_cycle(self) -> bool:
        """
        Check if the dependency graph contains any cycles.

        Returns:
            True if cycles exist, False otherwise
        """
        def visit(node_id: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            for dep_id in self.edges.get(node_id, []):
                if dep_id not in visited:
                    if visit(dep_id, visited, rec_stack):
                        return True
                elif dep_id in rec_stack:
                    return True

            rec_stack.remove(node_id)
            return False

        visited = set()
        rec_stack = set()

        for node_id in self.nodes:
            if node_id not in visited:
                if visit(node_id, visited, rec_stack):
                    return True

        return False

    def _would_create_cycle(self, from_id: str, to_id: str) -> bool:
        """
        Check if adding a dependency would create a cycle.

        Args:
            from_id: Source node ID
            to_id: Target node ID

        Returns:
            True if adding the edge would create a cycle
        """
        # Temporarily add the edge
        temp_edges = {k: list(v) for k, v in self.edges.items()}
        if from_id not in temp_edges:
            temp_edges[from_id] = []
        if to_id not in temp_edges[from_id]:
            temp_edges[from_id].append(to_id)

        # Check for cycles using DFS
        def has_path(start: str, end: str, visited: Set[str]) -> bool:
            if start == end:
                return True
            visited.add(start)
            for dep in temp_edges.get(start, []):
                if dep not in visited:
                    if has_path(dep, end, visited):
                        return True
            return False

        # If there's a path from to_id to from_id, adding this edge creates a cycle
        return has_path(to_id, from_id, set())

    def topological_sort(self) -> Optional[List[str]]:
        """
        Perform topological sort on the dependency graph.

        Returns:
            Ordered list of item IDs in topologically sorted order,
            or None if the graph contains cycles
        """
        if self.has_cycle():
            return None

        visited = set()
        result = []

        def visit(node_id: str):
            if node_id in visited:
                return
            visited.add(node_id)

            for dep_id in self.edges.get(node_id, []):
                visit(dep_id)

            result.append(node_id)

        for node_id in self.nodes:
            visit(node_id)

        return list(reversed(result))

    def get_execution_order(self) -> Optional[List[List[str]]]:
        """
        Get execution order grouped by dependency levels.

        Returns:
            List of lists, where each inner list contains items that can be
            executed in parallel, or None if cycles exist
        """
        if self.has_cycle():
            return None

        levels = []
        remaining = set(self.nodes.keys())
        processed = set()

        while remaining:
            # Find all nodes with no unprocessed dependencies
            current_level = []
            for node_id in remaining:
                deps = self.edges.get(node_id, [])
                if all(dep in processed for dep in deps):
                    current_level.append(node_id)

            if not current_level:
                # This shouldn't happen if has_cycle() returned False
                return None

            levels.append(current_level)
            remaining -= set(current_level)
            processed.update(current_level)

        return levels

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate the dependency graph.

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Check for cycles
        if self.has_cycle():
            errors.append("Dependency graph contains cycles")

        # Check for dangling references
        for node_id, deps in self.edges.items():
            for dep_id in deps:
                if dep_id not in self.nodes:
                    errors.append(f"Node {node_id} depends on non-existent node {dep_id}")

        return len(errors) == 0, errors

    def is_valid(self) -> bool:
        """
        Check if the dependency graph is valid.

        Returns:
            True if the graph is valid (no cycles, no dangling references)
        """
        is_valid, _ = self.validate()
        return is_valid
