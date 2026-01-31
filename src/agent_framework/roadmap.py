"""
Roadmap Generator Agent

This module provides the RoadmapGenerator agent that orchestrates codebase analysis,
competitive intelligence, and prioritization to generate strategic development roadmaps.
"""

from typing import Any, Dict, List, Optional

from agent_framework.agent import Agent
from agent_framework.roadmap_models import Roadmap, Feature, Milestone, Phase
from agent_framework.competitive_models import Competitor, PainPoint, Market
from agent_framework.prioritization_models import MoSCoWCategory, Priority


class RoadmapGenerator(Agent):
    """
    An agent that generates strategic roadmaps from codebase analysis.

    This agent orchestrates multiple components to create comprehensive development
    roadmaps that include:
    - Feature extraction and organization
    - MoSCoW prioritization with rationale
    - Competitor pain point mapping
    - Milestone generation with success metrics
    - Dependency validation
    - Phase organization

    The agent integrates with CompetitiveAnalyzer for market intelligence and
    PrioritizationEngine for feature prioritization.
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
        Initialize the RoadmapGenerator agent.

        Args:
            name: A human-readable name for this agent instance.
            config: Optional dictionary of configuration parameters.
            tool_registry: Optional tool registry for managing agent tools.
            context_manager: Optional context manager for multi-file context handling.
            logger: Optional logger for introspection and debugging.
        """
        super().__init__(name, config, tool_registry, context_manager, logger)
        self._roadmap_cache: Optional[Roadmap] = None

    def execute(self, task: str, **kwargs) -> Any:
        """
        Execute a roadmap generation task.

        Args:
            task: The task type to execute. Supported tasks:
                - "generate": Generate a complete roadmap
                - "analyze_codebase": Analyze current codebase state
                - "extract_features": Extract features from context
                - "organize_phases": Organize features into phases
                - "map_pain_points": Map competitor pain points to features
                - "create_milestones": Create milestones with success metrics
            **kwargs: Task-specific parameters

        Returns:
            Task-specific results (dict, Roadmap, list, etc.)

        Raises:
            ValueError: If task type is unknown
        """
        self._log("info", f"Executing roadmap task: {task}", task=task)

        if task == "generate":
            return self._generate_roadmap(kwargs.get("context", {}))
        elif task == "analyze_codebase":
            return self._analyze_codebase_state(kwargs.get("context", {}))
        elif task == "extract_features":
            return self._extract_features(kwargs.get("context", {}))
        elif task == "organize_phases":
            return self._organize_phases(kwargs.get("features", []))
        elif task == "map_pain_points":
            return self._map_pain_points(
                kwargs.get("features", []),
                kwargs.get("pain_points", [])
            )
        elif task == "create_milestones":
            return self._create_milestones(kwargs.get("phases", []))
        else:
            error_msg = f"Unknown task: {task}"
            self._log("error", error_msg, task=task)
            return {"error": error_msg}

    def process_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and transform context information for roadmap generation.

        This method extracts relevant information from the raw context and
        prepares it for use in roadmap generation tasks.

        Args:
            context: Raw context dictionary containing:
                - codebase: Codebase analysis data
                - competitors: List of competitor information
                - market: Market analysis data
                - requirements: User requirements and priorities
                - constraints: Technical or business constraints

        Returns:
            Processed context dictionary with structured data ready for use.
        """
        processed = {
            "codebase": context.get("codebase", {}),
            "competitors": context.get("competitors", []),
            "market": context.get("market", {}),
            "requirements": context.get("requirements", {}),
            "constraints": context.get("constraints", {}),
            "options": context.get("options", {})
        }

        self._log(
            "debug",
            "Processed context",
            codebase_items=len(processed["codebase"]),
            competitors=len(processed["competitors"])
        )

        return processed

    def format_response(self, result: Any) -> str:
        """
        Format roadmap generation results into human-readable output.

        Args:
            result: The raw result from execute(). Can be:
                - Roadmap object
                - Dict with analysis results
                - List of features/phases
                - Error dict

        Returns:
            Formatted string representation suitable for presentation.
        """
        if isinstance(result, dict):
            if "error" in result:
                return f"Error: {result['error']}"

            if "codebase_state" in result:
                state = result["codebase_state"]
                return (
                    f"Codebase State Analysis:\n"
                    f"  Files analyzed: {state.get('file_count', 0)}\n"
                    f"  Total size: {state.get('total_size', 0)} bytes\n"
                    f"  Components: {len(state.get('components', []))}\n"
                    f"  Dependencies: {len(state.get('dependencies', []))}"
                )

            if "features" in result:
                features = result["features"]
                return f"Extracted {len(features)} features from context"

            if "phases" in result:
                phases = result["phases"]
                return f"Organized features into {len(phases)} phases"

            if "milestones" in result:
                milestones = result["milestones"]
                return f"Created {len(milestones)} milestones with success metrics"

        if isinstance(result, Roadmap):
            return self._format_roadmap(result)

        if isinstance(result, list):
            if result and isinstance(result[0], Feature):
                return f"Features: {len(result)}"
            if result and isinstance(result[0], Phase):
                return f"Phases: {len(result)}"
            if result and isinstance(result[0], Milestone):
                return f"Milestones: {len(result)}"

        return str(result)

    def _generate_roadmap(self, context: Dict[str, Any]) -> Roadmap:
        """
        Generate a complete roadmap from the provided context.

        This is the main orchestration method that coordinates all roadmap
        generation steps.

        Args:
            context: Context dictionary with all necessary data

        Returns:
            Complete Roadmap object
        """
        self._log("info", "Generating roadmap", action="generate_roadmap")

        processed_context = self.process_context(context)

        # Extract features from context
        features = self._extract_features(processed_context)

        # Organize into phases
        phases = self._organize_phases(features)

        # Map competitor pain points if available
        if processed_context.get("competitors"):
            pain_points = self._extract_pain_points(processed_context["competitors"])
            features = self._map_pain_points(features, pain_points)

        # Create milestones
        milestones = self._create_milestones(phases)

        # Build the roadmap
        roadmap = Roadmap(
            name=context.get("name", "Development Roadmap"),
            description=context.get("description", "Strategic development roadmap"),
            features=features,
            phases=phases,
            milestones=milestones
        )

        self._roadmap_cache = roadmap
        self._log("info", "Roadmap generated successfully",
                  features=len(features), phases=len(phases), milestones=len(milestones))

        return roadmap

    def _analyze_codebase_state(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the current state of the codebase.

        Args:
            context: Context with codebase information

        Returns:
            Dictionary with codebase analysis results
        """
        self._log("debug", "Analyzing codebase state", action="analyze_codebase")

        if self.context_manager:
            stats = self.context_manager.get_stats()
            return {
                "codebase_state": {
                    "file_count": stats.get("file_count", 0),
                    "total_size": stats.get("total_size", 0),
                    "components": [],
                    "dependencies": []
                }
            }

        # Fallback if no context manager
        codebase = context.get("codebase", {})
        return {
            "codebase_state": {
                "file_count": len(codebase.get("files", [])),
                "total_size": 0,
                "components": codebase.get("components", []),
                "dependencies": codebase.get("dependencies", [])
            }
        }

    def _extract_features(self, context: Dict[str, Any]) -> List[Feature]:
        """
        Extract features from the context.

        Args:
            context: Processed context dictionary

        Returns:
            List of Feature objects
        """
        self._log("debug", "Extracting features", action="extract_features")

        # Placeholder implementation - will be enhanced in subsequent subtasks
        features = []
        requirements = context.get("requirements", {})

        for req_id, req_data in requirements.items():
            feature = Feature(
                id=req_id,
                name=req_data.get("name", f"Feature {req_id}"),
                description=req_data.get("description", ""),
                moscow_priority=MoSCoWCategory.SHOULD,
                business_value=req_data.get("business_value", 5),
                technical_complexity=req_data.get("technical_complexity", 5),
                dependencies=req_data.get("dependencies", []),
                competitor_pain_points=[]
            )
            features.append(feature)

        self._log("info", f"Extracted {len(features)} features", count=len(features))
        return features

    def _organize_phases(self, features: List[Feature]) -> List[Phase]:
        """
        Organize features into phases.

        Args:
            features: List of Feature objects to organize

        Returns:
            List of Phase objects
        """
        self._log("debug", "Organizing phases", action="organize_phases",
                  feature_count=len(features))

        # Placeholder implementation - basic phase organization
        phases = [
            Phase(
                id="phase-1",
                name="Foundation",
                description="Core infrastructure and must-have features",
                order=1,
                features=[],
                objectives=["Establish core functionality"],
                success_criteria=["Basic features operational"]
            )
        ]

        self._log("info", f"Organized into {len(phases)} phases", count=len(phases))
        return phases

    def _map_pain_points(
        self,
        features: List[Feature],
        pain_points: List[PainPoint]
    ) -> List[Feature]:
        """
        Map competitor pain points to features.

        Args:
            features: List of features to enhance with pain point mapping
            pain_points: List of competitor pain points

        Returns:
            Updated list of features with pain point mappings
        """
        self._log("debug", "Mapping pain points to features",
                  features=len(features), pain_points=len(pain_points))

        # Placeholder implementation
        return features

    def _create_milestones(self, phases: List[Phase]) -> List[Milestone]:
        """
        Create milestones with success metrics for each phase.

        Args:
            phases: List of Phase objects

        Returns:
            List of Milestone objects
        """
        self._log("debug", "Creating milestones", action="create_milestones",
                  phase_count=len(phases))

        milestones = []
        for phase in phases:
            milestone = Milestone(
                id=f"milestone-{phase.id}",
                name=f"{phase.name} Complete",
                description=f"Completion of {phase.name} phase",
                target_date="TBD",
                success_metrics=phase.success_criteria
            )
            milestones.append(milestone)

        self._log("info", f"Created {len(milestones)} milestones", count=len(milestones))
        return milestones

    def _extract_pain_points(self, competitors: List[Any]) -> List[PainPoint]:
        """
        Extract pain points from competitor data.

        Args:
            competitors: List of competitor information

        Returns:
            List of PainPoint objects
        """
        # Placeholder implementation
        return []

    def _format_roadmap(self, roadmap: Roadmap) -> str:
        """
        Format a Roadmap object into a human-readable string.

        Args:
            roadmap: The Roadmap object to format

        Returns:
            Formatted string representation
        """
        output = [
            f"Roadmap: {roadmap.name}",
            f"Description: {roadmap.description}",
            f"",
            f"Summary:",
            f"  Features: {len(roadmap.features)}",
            f"  Phases: {len(roadmap.phases)}",
            f"  Milestones: {len(roadmap.milestones)}",
        ]

        if roadmap.phases:
            output.append("")
            output.append("Phases:")
            for phase in roadmap.phases:
                output.append(f"  {phase.order}. {phase.name}: {phase.description}")

        return "\n".join(output)
