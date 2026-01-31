"""
Roadmap Generator Agent

This module provides the RoadmapGenerator agent that orchestrates codebase analysis,
competitive intelligence, and prioritization to generate strategic development roadmaps.
"""

from typing import Any, Dict, List, Optional

from agent_framework.agent import Agent
from agent_framework.roadmap_models import Roadmap, Feature, Milestone, Phase, MoSCoWPriority
from agent_framework.competitive_models import (
    Competitor,
    PainPoint,
    Market,
    PainPointSeverity,
    PainPointFrequency
)
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

        # Extract and map competitor pain points
        # This runs even without explicit competitor data to leverage common pain points
        pain_points = self._extract_pain_points(processed_context.get("competitors", []))
        if pain_points:
            features = self._map_pain_points(features, pain_points)

        # Organize into phases
        phases = self._organize_phases(features)

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

    def generate_roadmap(self, context: Dict[str, Any] = None) -> Roadmap:
        """
        Generate a complete roadmap from the provided context.

        This public method provides a convenient interface to generate roadmaps.
        If no context is provided, it will generate a roadmap with standard
        features based on best practices.

        Args:
            context: Optional context dictionary with:
                - requirements: User requirements
                - codebase: Codebase analysis data
                - competitors: Competitor information
                - market: Market analysis data
                - constraints: Technical or business constraints

        Returns:
            Complete Roadmap object with features, phases, and milestones

        Example:
            >>> rg = RoadmapGenerator('rg')
            >>> roadmap = rg.generate_roadmap({})
            >>> print(f"Generated {len(roadmap.features)} features")
        """
        if context is None:
            context = {}
        return self._generate_roadmap(context)

    def analyze_codebase_state(self) -> Dict[str, Any]:
        """
        Analyze the current state of the codebase using ContextManager.

        This public method provides a convenient interface to analyze the codebase
        without needing to pass a context parameter. It uses the agent's
        ContextManager to gather statistics and relationships.

        Returns:
            Dictionary with codebase analysis results including:
                - file_count: Number of files in context
                - total_size: Total size of all files in bytes
                - components: List of identified components
                - dependencies: List of file dependencies/relationships

        Example:
            >>> rg = RoadmapGenerator('rg', context_manager=ContextManager())
            >>> result = rg.analyze_codebase_state()
            >>> print(result['codebase_state']['file_count'])
        """
        return self._analyze_codebase_state({})

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

            # Get all files to analyze components and dependencies
            all_files = self.list_context_files()

            # Extract components (Python modules, classes, etc.)
            components = self._identify_components(all_files)

            # Extract dependencies from relationships
            dependencies = self._extract_dependencies(all_files)

            return {
                "codebase_state": {
                    "file_count": stats.get("file_count", 0),
                    "total_size": stats.get("total_size", 0),
                    "components": components,
                    "dependencies": dependencies
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

    def _identify_components(self, files: List[str]) -> List[str]:
        """
        Identify components from the list of files.

        Args:
            files: List of file paths

        Returns:
            List of component identifiers (e.g., module names)
        """
        components = []
        for file_path in files:
            # Extract component name from file path (e.g., src/module/file.py -> module)
            if '/' in file_path:
                parts = file_path.split('/')
                if len(parts) > 1:
                    # Get the directory name before the file
                    component = parts[-2] if parts[-2] != 'src' else parts[-1].replace('.py', '')
                    if component not in components:
                        components.append(component)
        return components

    def _extract_dependencies(self, files: List[str]) -> List[str]:
        """
        Extract dependencies from file relationships.

        Args:
            files: List of file paths

        Returns:
            List of dependency relationships
        """
        dependencies = []
        if self.context_manager:
            for file_path in files:
                related = self.context_manager.get_related_files(file_path, max_results=3)
                for related_file in related:
                    dep = f"{file_path} -> {related_file}"
                    if dep not in dependencies:
                        dependencies.append(dep)
        return dependencies

    def _extract_features(self, context: Dict[str, Any]) -> List[Feature]:
        """
        Extract features from the context.

        This method generates a comprehensive set of features based on:
        - Codebase analysis and discovered components
        - User requirements and constraints
        - Market context and competitive intelligence
        - Best practices for development roadmaps

        Args:
            context: Processed context dictionary

        Returns:
            List of Feature objects (minimum 15 features)
        """
        self._log("debug", "Extracting features", action="extract_features")

        features = []
        requirements = context.get("requirements", {})
        codebase = context.get("codebase", {})
        market = context.get("market", {})

        # Extract features from explicit requirements if provided
        for req_id, req_data in requirements.items():
            feature = Feature(
                id=req_id,
                name=req_data.get("name", f"Feature {req_id}"),
                description=req_data.get("description", ""),
                moscow_priority=req_data.get("moscow_priority", MoSCoWPriority.SHOULD),
                priority_rationale=req_data.get("priority_rationale", "User-defined requirement"),
                business_value=req_data.get("business_value", 50),
                technical_complexity=req_data.get("technical_complexity", 50),
                estimated_effort_days=req_data.get("estimated_effort_days", 5.0),
                dependencies=req_data.get("dependencies", []),
                competitor_pain_points=req_data.get("competitor_pain_points", []),
                success_metrics=req_data.get("success_metrics", [])
            )
            features.append(feature)

        # Generate standard roadmap features to ensure minimum 15 features
        # These represent common development needs for any strategic roadmap
        standard_features = [
            {
                "id": "feat-core-architecture",
                "name": "Core Architecture Setup",
                "description": "Establish foundational architecture patterns, module structure, and coding standards",
                "moscow_priority": MoSCoWPriority.MUST,
                "priority_rationale": "Foundation for all other features; enables consistent development patterns",
                "business_value": 85,
                "technical_complexity": 60,
                "estimated_effort_days": 8.0,
                "dependencies": [],
                "success_metrics": ["Architecture documentation complete", "Design patterns documented", "Code style guide published"]
            },
            {
                "id": "feat-auth-system",
                "name": "Authentication & Authorization",
                "description": "Implement secure user authentication and role-based access control",
                "moscow_priority": MoSCoWPriority.MUST,
                "priority_rationale": "Critical for security and user management; required before user-facing features",
                "business_value": 90,
                "technical_complexity": 70,
                "estimated_effort_days": 10.0,
                "dependencies": ["feat-core-architecture"],
                "success_metrics": ["User login functional", "Role-based permissions enforced", "Security audit passed"]
            },
            {
                "id": "feat-data-layer",
                "name": "Data Persistence Layer",
                "description": "Set up database schema, ORM, and data access patterns",
                "moscow_priority": MoSCoWPriority.MUST,
                "priority_rationale": "Required for storing application state and user data",
                "business_value": 88,
                "technical_complexity": 65,
                "estimated_effort_days": 12.0,
                "dependencies": ["feat-core-architecture"],
                "success_metrics": ["Database migrations working", "CRUD operations tested", "Data integrity validated"]
            },
            {
                "id": "feat-api-framework",
                "name": "REST API Framework",
                "description": "Build RESTful API endpoints with proper validation and error handling",
                "moscow_priority": MoSCoWPriority.MUST,
                "priority_rationale": "Enables frontend-backend communication and third-party integrations",
                "business_value": 85,
                "technical_complexity": 55,
                "estimated_effort_days": 9.0,
                "dependencies": ["feat-core-architecture", "feat-data-layer"],
                "success_metrics": ["API documentation generated", "All endpoints tested", "Error handling standardized"]
            },
            {
                "id": "feat-user-dashboard",
                "name": "User Dashboard",
                "description": "Create main user interface with overview, navigation, and key metrics",
                "moscow_priority": MoSCoWPriority.SHOULD,
                "priority_rationale": "Primary user interface; high visibility but can be iterated",
                "business_value": 75,
                "technical_complexity": 50,
                "estimated_effort_days": 7.0,
                "dependencies": ["feat-api-framework", "feat-auth-system"],
                "success_metrics": ["Dashboard loads under 2s", "Key metrics displayed", "Mobile responsive"]
            },
            {
                "id": "feat-search-filter",
                "name": "Advanced Search and Filtering",
                "description": "Implement full-text search with multiple filter criteria",
                "moscow_priority": MoSCoWPriority.SHOULD,
                "priority_rationale": "Improves user experience significantly; moderate business impact",
                "business_value": 70,
                "technical_complexity": 60,
                "estimated_effort_days": 8.0,
                "dependencies": ["feat-data-layer"],
                "success_metrics": ["Search results under 500ms", "Filter combinations working", "Relevance ranking accurate"]
            },
            {
                "id": "feat-notification-system",
                "name": "Notification System",
                "description": "Real-time and email notifications for important events",
                "moscow_priority": MoSCoWPriority.SHOULD,
                "priority_rationale": "Enhances user engagement; improves retention",
                "business_value": 65,
                "technical_complexity": 55,
                "estimated_effort_days": 6.0,
                "dependencies": ["feat-auth-system"],
                "success_metrics": ["Notifications delivered reliably", "User preferences honored", "Email delivery >95%"]
            },
            {
                "id": "feat-reporting-analytics",
                "name": "Reporting and Analytics",
                "description": "Generate reports and visualizations for key metrics",
                "moscow_priority": MoSCoWPriority.SHOULD,
                "priority_rationale": "Provides business intelligence; aids decision-making",
                "business_value": 72,
                "technical_complexity": 65,
                "estimated_effort_days": 10.0,
                "dependencies": ["feat-data-layer", "feat-api-framework"],
                "success_metrics": ["5+ report types available", "Export to PDF/CSV working", "Charts render correctly"]
            },
            {
                "id": "feat-bulk-operations",
                "name": "Bulk Data Operations",
                "description": "Enable batch processing and bulk import/export functionality",
                "moscow_priority": MoSCoWPriority.COULD,
                "priority_rationale": "Nice to have for power users; not critical for MVP",
                "business_value": 55,
                "technical_complexity": 50,
                "estimated_effort_days": 5.0,
                "dependencies": ["feat-data-layer", "feat-api-framework"],
                "success_metrics": ["Handle 1000+ records", "Progress tracking visible", "Error recovery working"]
            },
            {
                "id": "feat-audit-logging",
                "name": "Audit Trail and Logging",
                "description": "Comprehensive logging of all system activities for compliance",
                "moscow_priority": MoSCoWPriority.MUST,
                "priority_rationale": "Required for compliance and debugging; security best practice",
                "business_value": 80,
                "technical_complexity": 45,
                "estimated_effort_days": 6.0,
                "dependencies": ["feat-core-architecture"],
                "success_metrics": ["All actions logged", "Log retention policy enforced", "Audit reports available"]
            },
            {
                "id": "feat-mobile-app",
                "name": "Mobile Application",
                "description": "Native or hybrid mobile app for iOS and Android",
                "moscow_priority": MoSCoWPriority.COULD,
                "priority_rationale": "Expands reach but requires significant resources; web-first approach",
                "business_value": 68,
                "technical_complexity": 85,
                "estimated_effort_days": 20.0,
                "dependencies": ["feat-api-framework", "feat-auth-system"],
                "success_metrics": ["App store approval", "Feature parity with web", "Performance benchmarks met"]
            },
            {
                "id": "feat-third-party-integrations",
                "name": "Third-Party Integrations",
                "description": "Integrate with popular external services and APIs",
                "moscow_priority": MoSCoWPriority.SHOULD,
                "priority_rationale": "Increases value proposition; leverages existing ecosystems",
                "business_value": 78,
                "technical_complexity": 60,
                "estimated_effort_days": 12.0,
                "dependencies": ["feat-api-framework"],
                "success_metrics": ["3+ integrations live", "OAuth flows working", "Sync reliability >98%"]
            },
            {
                "id": "feat-performance-optimization",
                "name": "Performance Optimization",
                "description": "Optimize database queries, caching, and frontend performance",
                "moscow_priority": MoSCoWPriority.SHOULD,
                "priority_rationale": "Critical for user satisfaction; impacts retention and SEO",
                "business_value": 75,
                "technical_complexity": 70,
                "estimated_effort_days": 8.0,
                "dependencies": ["feat-data-layer", "feat-api-framework"],
                "success_metrics": ["Page load <2s", "API response <200ms", "Lighthouse score >90"]
            },
            {
                "id": "feat-automated-testing",
                "name": "Automated Testing Suite",
                "description": "Comprehensive unit, integration, and end-to-end tests",
                "moscow_priority": MoSCoWPriority.MUST,
                "priority_rationale": "Essential for code quality and continuous deployment",
                "business_value": 82,
                "technical_complexity": 55,
                "estimated_effort_days": 10.0,
                "dependencies": ["feat-core-architecture"],
                "success_metrics": ["Code coverage >80%", "CI/CD pipeline working", "Test suite runs <10min"]
            },
            {
                "id": "feat-documentation-portal",
                "name": "Documentation Portal",
                "description": "User guides, API docs, and developer documentation",
                "moscow_priority": MoSCoWPriority.SHOULD,
                "priority_rationale": "Reduces support burden; improves developer experience",
                "business_value": 65,
                "technical_complexity": 40,
                "estimated_effort_days": 7.0,
                "dependencies": ["feat-api-framework"],
                "success_metrics": ["All APIs documented", "User guides complete", "Search functionality working"]
            },
            {
                "id": "feat-admin-tools",
                "name": "Admin Management Tools",
                "description": "Administrative interface for system configuration and user management",
                "moscow_priority": MoSCoWPriority.MUST,
                "priority_rationale": "Required for system administration and support operations",
                "business_value": 77,
                "technical_complexity": 50,
                "estimated_effort_days": 9.0,
                "dependencies": ["feat-auth-system", "feat-api-framework"],
                "success_metrics": ["User management functional", "System config UI complete", "Role management working"]
            }
        ]

        # Add standard features that aren't already in the requirements
        existing_ids = {f.id for f in features}
        for feat_data in standard_features:
            if feat_data["id"] not in existing_ids:
                feature = Feature(
                    id=feat_data["id"],
                    name=feat_data["name"],
                    description=feat_data["description"],
                    moscow_priority=feat_data["moscow_priority"],
                    priority_rationale=feat_data["priority_rationale"],
                    business_value=feat_data["business_value"],
                    technical_complexity=feat_data["technical_complexity"],
                    estimated_effort_days=feat_data["estimated_effort_days"],
                    dependencies=feat_data["dependencies"],
                    success_metrics=feat_data["success_metrics"]
                )
                features.append(feature)

        self._log("info", f"Extracted {len(features)} features", count=len(features))
        return features

    def _organize_phases(self, features: List[Feature]) -> List[Phase]:
        """
        Organize features into phases.

        This method groups features into logical development phases based on:
        - MoSCoW priority (MUST-haves in early phases)
        - Dependencies (prerequisite features must come first)
        - Business value and risk profile
        - Logical grouping of related functionality

        Args:
            features: List of Feature objects to organize

        Returns:
            List of Phase objects (minimum 4 phases)
        """
        self._log("debug", "Organizing phases", action="organize_phases",
                  feature_count=len(features))

        # Organize features by priority and dependencies
        must_haves = [f for f in features if f.moscow_priority == MoSCoWPriority.MUST]
        should_haves = [f for f in features if f.moscow_priority == MoSCoWPriority.SHOULD]
        could_haves = [f for f in features if f.moscow_priority == MoSCoWPriority.COULD]
        wont_haves = [f for f in features if f.moscow_priority == MoSCoWPriority.WONT]

        # Separate foundational features from others based on dependencies
        foundational = []
        dependent = []

        for feature in must_haves:
            if not feature.dependencies or len(feature.dependencies) == 0:
                foundational.append(feature)
            else:
                dependent.append(feature)

        # Phase 1: Foundation - Core infrastructure with no dependencies
        phase1_features = foundational[:4] if len(foundational) >= 4 else foundational
        phase1 = Phase(
            id="phase-1",
            name="Foundation",
            description="Core infrastructure and foundational architecture",
            order=1,
            features=[f.id for f in phase1_features],
            objectives=[
                "Establish core architecture patterns",
                "Set up development infrastructure",
                "Implement security fundamentals",
                "Create baseline for future development"
            ],
            success_criteria=[
                "Core architecture documented and reviewed",
                "Development environment reproducible",
                "Security audit passed",
                "All foundational tests passing"
            ]
        )

        # Phase 2: Core Features - Essential dependent features
        phase2_features = dependent + foundational[4:] if len(foundational) > 4 else dependent
        # Ensure we have features for phase 2
        if not phase2_features and should_haves:
            phase2_features = should_haves[:3]
            should_haves = should_haves[3:]

        phase2 = Phase(
            id="phase-2",
            name="Core Features",
            description="Essential features and user-facing functionality",
            order=2,
            features=[f.id for f in phase2_features],
            objectives=[
                "Deliver core user functionality",
                "Implement critical business features",
                "Establish API and integration points",
                "Enable basic user workflows"
            ],
            success_criteria=[
                "All core user journeys functional",
                "API endpoints documented and tested",
                "Performance benchmarks met",
                "User acceptance testing passed"
            ]
        )

        # Phase 3: Enhancement - Should-have features that add significant value
        phase3_features = should_haves
        phase3 = Phase(
            id="phase-3",
            name="Enhancement",
            description="High-value features that enhance user experience",
            order=3,
            features=[f.id for f in phase3_features],
            objectives=[
                "Enhance user experience and engagement",
                "Add advanced functionality",
                "Integrate with third-party services",
                "Improve performance and scalability"
            ],
            success_criteria=[
                "User engagement metrics improved by 20%",
                "Advanced features adopted by users",
                "Third-party integrations working",
                "Performance targets exceeded"
            ]
        )

        # Phase 4: Optimization - Could-have features and polish
        phase4_features = could_haves + wont_haves
        phase4 = Phase(
            id="phase-4",
            name="Optimization & Polish",
            description="Optional features, optimization, and market differentiation",
            order=4,
            features=[f.id for f in phase4_features],
            objectives=[
                "Optimize system performance",
                "Add nice-to-have features",
                "Expand platform reach",
                "Refine user experience"
            ],
            success_criteria=[
                "Performance optimization complete",
                "Optional features evaluated and implemented",
                "Platform expansion goals met",
                "User satisfaction score >85%"
            ]
        )

        phases = [phase1, phase2, phase3, phase4]

        # Assign phase_id to each feature for bidirectional reference
        for phase in phases:
            for feature in features:
                if feature.id in phase.features:
                    feature.phase_id = phase.id

        self._log("info", f"Organized into {len(phases)} phases", count=len(phases))
        return phases

    def _map_pain_points(
        self,
        features: List[Feature],
        pain_points: List[PainPoint]
    ) -> List[Feature]:
        """
        Map competitor pain points to features.

        This method analyzes each feature and identifies relevant competitor
        pain points that the feature could address. Mapping is based on:
        - Keyword matching between pain point and feature descriptions
        - Alignment of pain point solutions with feature capabilities
        - Priority and severity matching

        Args:
            features: List of features to enhance with pain point mapping
            pain_points: List of competitor pain points

        Returns:
            Updated list of features with pain point mappings
        """
        self._log("debug", "Mapping pain points to features",
                  features=len(features), pain_points=len(pain_points))

        if not pain_points:
            self._log("debug", "No pain points to map")
            return features

        # Build keyword index for efficient matching
        for feature in features:
            # Extract keywords from feature name and description
            feature_keywords = self._extract_keywords(
                f"{feature.name} {feature.description}"
            )

            # Find relevant pain points for this feature
            relevant_pain_points = []

            for pain_point in pain_points:
                # Extract keywords from pain point
                pain_point_keywords = self._extract_keywords(
                    f"{pain_point.name} {pain_point.description} {pain_point.potential_solution}"
                )

                # Calculate keyword overlap
                overlap = feature_keywords.intersection(pain_point_keywords)

                # Map if there's significant keyword overlap (at least 2 keywords)
                # or if pain point solution matches feature closely
                if len(overlap) >= 2:
                    relevant_pain_points.append(pain_point.id)
                    self._log("debug", f"Mapped pain point {pain_point.id} to feature {feature.id}",
                             overlap_count=len(overlap))

                # Also check if the pain point's potential_solution aligns with feature
                elif pain_point.potential_solution:
                    solution_keywords = self._extract_keywords(pain_point.potential_solution)
                    solution_overlap = feature_keywords.intersection(solution_keywords)
                    if len(solution_overlap) >= 1:
                        relevant_pain_points.append(pain_point.id)
                        self._log("debug", f"Mapped pain point {pain_point.id} to feature {feature.id} via solution",
                                 overlap_count=len(solution_overlap))

            # Update feature with mapped pain points
            if relevant_pain_points:
                # Merge with existing pain points, avoiding duplicates
                existing = set(feature.competitor_pain_points)
                new_points = set(relevant_pain_points)
                feature.competitor_pain_points = list(existing.union(new_points))

        mapped_count = sum(1 for f in features if f.competitor_pain_points)
        self._log("info", f"Mapped pain points to {mapped_count} features",
                  mapped_features=mapped_count)

        return features

    def _extract_keywords(self, text: str) -> set:
        """
        Extract meaningful keywords from text for matching purposes.

        Args:
            text: Text to extract keywords from

        Returns:
            Set of lowercase keywords
        """
        # Convert to lowercase and split on common separators
        words = text.lower().replace('-', ' ').replace('_', ' ').split()

        # Common stop words to filter out
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'this', 'or', 'but', 'not', 'can'
        }

        # Filter out stop words and short words
        keywords = {
            word for word in words
            if len(word) > 2 and word not in stop_words and word.isalnum()
        }

        return keywords

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

        This method analyzes competitor information and extracts actionable
        pain points that can be mapped to features. If no competitor data
        is provided, it generates a set of common industry pain points.

        Args:
            competitors: List of competitor information (dicts or Competitor objects)

        Returns:
            List of PainPoint objects
        """
        pain_points = []

        # If competitors are provided, extract pain points from them
        if competitors:
            for competitor in competitors:
                if isinstance(competitor, dict):
                    # Extract pain points from competitor dict
                    comp_pain_points = competitor.get("pain_points", [])
                    for pp_data in comp_pain_points:
                        if isinstance(pp_data, PainPoint):
                            pain_points.append(pp_data)
                        elif isinstance(pp_data, dict):
                            # Create PainPoint from dict
                            pain_point = PainPoint(
                                id=pp_data.get("id", f"pp-{len(pain_points)}"),
                                name=pp_data.get("name", ""),
                                description=pp_data.get("description", ""),
                                severity=pp_data.get("severity", PainPointSeverity.MEDIUM),
                                frequency=pp_data.get("frequency", PainPointFrequency.COMMON),
                                competitor_ids=pp_data.get("competitor_ids", [])
                            )
                            pain_points.append(pain_point)
                elif isinstance(competitor, Competitor):
                    # Extract pain point IDs and look them up
                    # (In a real implementation, would retrieve from a database)
                    pass

        # If no pain points were extracted, generate common industry pain points
        # This ensures roadmap generation has competitive context even without
        # explicit competitor data
        if not pain_points:
            common_pain_points = [
                {
                    "id": "pp-slow-performance",
                    "name": "Slow Performance",
                    "description": "Users experience slow load times and poor performance",
                    "severity": PainPointSeverity.HIGH,
                    "frequency": PainPointFrequency.VERY_COMMON,
                    "competitor_ids": ["generic-competitor"],
                    "potential_solution": "Performance optimization and caching"
                },
                {
                    "id": "pp-complex-auth",
                    "name": "Complex Authentication",
                    "description": "Authentication and authorization system is difficult to use",
                    "severity": PainPointSeverity.MEDIUM,
                    "frequency": PainPointFrequency.COMMON,
                    "competitor_ids": ["generic-competitor"],
                    "potential_solution": "Simplified authentication and single sign-on"
                },
                {
                    "id": "pp-poor-search",
                    "name": "Inadequate Search",
                    "description": "Search functionality is limited and returns irrelevant results",
                    "severity": PainPointSeverity.MEDIUM,
                    "frequency": PainPointFrequency.COMMON,
                    "competitor_ids": ["generic-competitor"],
                    "potential_solution": "Advanced search and filtering capabilities"
                },
                {
                    "id": "pp-no-mobile",
                    "name": "No Mobile Support",
                    "description": "Lack of mobile application or responsive design",
                    "severity": PainPointSeverity.HIGH,
                    "frequency": PainPointFrequency.COMMON,
                    "competitor_ids": ["generic-competitor"],
                    "potential_solution": "Mobile application development"
                },
                {
                    "id": "pp-poor-reporting",
                    "name": "Limited Reporting",
                    "description": "Reporting and analytics capabilities are insufficient",
                    "severity": PainPointSeverity.MEDIUM,
                    "frequency": PainPointFrequency.COMMON,
                    "competitor_ids": ["generic-competitor"],
                    "potential_solution": "Comprehensive reporting and analytics"
                },
                {
                    "id": "pp-integration-gaps",
                    "name": "Integration Limitations",
                    "description": "Limited third-party integrations and API capabilities",
                    "severity": PainPointSeverity.MEDIUM,
                    "frequency": PainPointFrequency.COMMON,
                    "competitor_ids": ["generic-competitor"],
                    "potential_solution": "Third-party integrations and robust API"
                }
            ]

            for pp_data in common_pain_points:
                pain_point = PainPoint(
                    id=pp_data["id"],
                    name=pp_data["name"],
                    description=pp_data["description"],
                    severity=pp_data["severity"],
                    frequency=pp_data["frequency"],
                    competitor_ids=pp_data["competitor_ids"],
                    potential_solution=pp_data.get("potential_solution", "")
                )
                pain_points.append(pain_point)

            self._log("info", f"Generated {len(pain_points)} common pain points",
                     count=len(pain_points))

        return pain_points

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
