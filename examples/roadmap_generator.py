#!/usr/bin/env python3
"""
Roadmap Generator Example

This example demonstrates how to use the RoadmapGenerator agent to create
strategic development roadmaps from codebase analysis and competitive intelligence.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from agent_framework.roadmap import RoadmapGenerator
from agent_framework.context import ContextManager
from agent_framework.logging import AgentLogger, LogLevel
from agent_framework.competitive_models import (
    Competitor,
    PainPoint,
    Market,
    MarketPosition,
    PainPointSeverity,
    PainPointFrequency
)


def main():
    """Main function demonstrating roadmap generation."""
    print("=" * 60)
    print("Roadmap Generator Example")
    print("=" * 60)
    print()

    # Create logger and context manager
    logger = AgentLogger(
        name="roadmap_generator",
        level=LogLevel.INFO,
        format="text"
    )

    context_manager = ContextManager(max_files=100, logger=logger)

    # Create the roadmap generator agent
    agent = RoadmapGenerator(
        name="RoadmapGenerator",
        config={"version": "1.0"},
        context_manager=context_manager,
        logger=logger
    )

    agent.initialize()
    print(f"Agent initialized: {agent}\n")

    # Example 1: Generate a basic roadmap with default features
    print("Example 1: Generate a basic roadmap")
    print("-" * 40)
    roadmap = agent.generate_roadmap()
    response = agent.format_response(roadmap)
    print(response)
    print()

    # Example 2: Analyze codebase state
    print("Example 2: Analyze codebase state")
    print("-" * 40)
    # Add some sample files to the context
    sample_files = [
        {
            "path": "src/main.py",
            "content": "# Main application entry point\nimport config\nfrom api import app\n",
            "metadata": {"component": "core"}
        },
        {
            "path": "src/api.py",
            "content": "# API endpoints\nimport database\nfrom auth import authenticate\n",
            "metadata": {"component": "api"}
        },
        {
            "path": "src/database.py",
            "content": "# Database layer\nimport sqlalchemy\n",
            "metadata": {"component": "data"}
        }
    ]

    for file_info in sample_files:
        agent.add_context_file(
            file_info["path"],
            file_info["content"],
            file_info["metadata"]
        )

    result = agent.analyze_codebase_state()
    response = agent.format_response(result)
    print(response)
    print()

    # Example 3: Generate roadmap with competitive intelligence
    print("Example 3: Generate roadmap with competitive data")
    print("-" * 40)

    # Define sample competitors
    competitors = [
        Competitor(
            id="competitor-1",
            name="Acme Corp",
            description="Leading project management platform",
            market_position=MarketPosition.LEADER,
            strengths=["Large user base", "Extensive integrations"],
            weaknesses=["Slow performance", "Poor mobile experience"],
            features=["Task management", "Gantt charts", "Time tracking"],
            pricing_model="Subscription",
            target_audience="Enterprise teams",
            metadata={"founded": "2015", "users": "10M+"}
        ),
        Competitor(
            id="competitor-2",
            name="QuickTask",
            description="Fast and simple task management tool",
            market_position=MarketPosition.CHALLENGER,
            strengths=["Fast performance", "Clean UI"],
            weaknesses=["Limited reporting", "No API access"],
            features=["Task lists", "Basic collaboration"],
            pricing_model="Freemium",
            target_audience="Small teams",
            metadata={"founded": "2018", "users": "2M+"}
        )
    ]

    # Define pain points for competitors
    pain_points = [
        PainPoint(
            id="pain-1",
            name="Slow Performance",
            description="Users complain about slow page loads and sluggish UI",
            severity=PainPointSeverity.HIGH,
            frequency=PainPointFrequency.VERY_COMMON,
            competitor_ids=["competitor-1"],
            affected_users="Enterprise users with large datasets",
            business_impact="User churn, negative reviews",
            potential_solution="Implement caching, optimize database queries, use CDN",
            evidence=["User reviews", "Support tickets", "Performance benchmarks"]
        ),
        PainPoint(
            id="pain-2",
            name="Limited Reporting",
            description="Lack of customizable reports and analytics",
            severity=PainPointSeverity.MEDIUM,
            frequency=PainPointFrequency.COMMON,
            competitor_ids=["competitor-2"],
            affected_users="Team leads and managers",
            business_impact="Limited visibility into team productivity",
            potential_solution="Add customizable dashboard, export capabilities",
            evidence=["Feature requests", "Customer feedback"]
        ),
        PainPoint(
            id="pain-3",
            name="Poor Mobile Experience",
            description="Mobile app is clunky and missing key features",
            severity=PainPointSeverity.HIGH,
            frequency=PainPointFrequency.COMMON,
            competitor_ids=["competitor-1"],
            affected_users="Remote workers, field teams",
            business_impact="Reduced mobile adoption, lower engagement",
            potential_solution="Redesign mobile app with native features",
            evidence=["App store reviews", "Usage analytics"]
        )
    ]

    # Create context with competitive data
    context = {
        "competitors": competitors,
        "requirements": {
            "target_users": "Development teams",
            "key_features": ["Fast performance", "Great mobile", "Advanced reporting"]
        },
        "market": {
            "size": "Growing",
            "trends": ["Remote work", "Agile adoption", "AI integration"]
        }
    }

    # Generate roadmap with competitive context
    roadmap_with_context = agent.execute("generate", context=context)
    response = agent.format_response(roadmap_with_context)
    print(response)
    print()

    # Example 4: Extract and examine features
    print("Example 4: Extract features from context")
    print("-" * 40)
    features = agent.execute("extract_features", context=context)
    print(f"Extracted {len(features)} features:")
    for i, feature in enumerate(features[:5], 1):  # Show first 5
        print(f"  {i}. {feature.name} ({feature.priority.value})")
        print(f"     Business Value: {feature.business_value}/100")
        print(f"     Effort: {feature.estimated_effort} person-days")
    if len(features) > 5:
        print(f"  ... and {len(features) - 5} more features")
    print()

    # Example 5: Map pain points to features
    print("Example 5: Map competitor pain points to features")
    print("-" * 40)
    features_with_pain_points = agent.execute(
        "map_pain_points",
        features=features,
        pain_points=pain_points
    )
    mapped_features = [
        f for f in features_with_pain_points
        if f.competitor_pain_points
    ]
    print(f"Found {len(mapped_features)} features addressing competitor pain points:")
    for i, feature in enumerate(mapped_features[:3], 1):  # Show first 3
        print(f"  {i}. {feature.name}")
        print(f"     Addresses: {', '.join([pp.name for pp in feature.competitor_pain_points])}")
    if len(mapped_features) > 3:
        print(f"  ... and {len(mapped_features) - 3} more features")
    print()

    # Example 6: Organize features into phases
    print("Example 6: Organize features into phases")
    print("-" * 40)
    phases = agent.execute("organize_phases", features=features)
    print(f"Organized into {len(phases)} phases:")
    for phase in phases:
        print(f"  Phase {phase.order}: {phase.name}")
        print(f"    Features: {len(phase.features)}")
        print(f"    Objective: {phase.objectives}")
    print()

    # Example 7: Create milestones with success metrics
    print("Example 7: Create milestones with success metrics")
    print("-" * 40)
    milestones = agent.execute("create_milestones", phases=phases)
    print(f"Created {len(milestones)} milestones:")
    for i, milestone in enumerate(milestones, 1):
        print(f"  {i}. {milestone.name}")
        print(f"     Features: {len(milestone.features)}")
        print(f"     Success Metrics: {len(milestone.success_metrics)}")
        if milestone.success_metrics:
            print(f"       - {milestone.success_metrics[0]}")
    print()

    # Example 8: Validation - check roadmap acceptance criteria
    print("Example 8: Validate roadmap acceptance criteria")
    print("-" * 40)
    validation_results = []

    # Check: At least 15 features
    feature_count = len(roadmap.features)
    validation_results.append(
        f"✓ Features count: {feature_count} (requirement: 15+)"
        if feature_count >= 15
        else f"✗ Features count: {feature_count} (requirement: 15+)"
    )

    # Check: 4+ phases
    phase_count = len(roadmap.phases)
    validation_results.append(
        f"✓ Phases count: {phase_count} (requirement: 4+)"
        if phase_count >= 4
        else f"✗ Phases count: {phase_count} (requirement: 4+)"
    )

    # Check: MoSCoW prioritization
    prioritized = all(hasattr(f, 'priority') for f in roadmap.features)
    validation_results.append(
        f"✓ MoSCoW prioritization: All features prioritized"
        if prioritized
        else f"✗ MoSCoW prioritization: Missing priorities"
    )

    # Check: Success metrics
    has_metrics = all(
        hasattr(m, 'success_metrics') and m.success_metrics
        for m in roadmap.milestones
    )
    validation_results.append(
        f"✓ Success metrics: All milestones have metrics"
        if has_metrics
        else f"✗ Success metrics: Some milestones missing metrics"
    )

    # Check: Dependencies validated
    is_valid = roadmap.validate_dependencies()
    validation_results.append(
        f"✓ Dependencies: No circular dependencies"
        if is_valid
        else f"✗ Dependencies: Circular dependencies detected"
    )

    print("Roadmap Validation Results:")
    for result in validation_results:
        print(f"  {result}")
    print()

    # Show agent logs
    print("Agent Activity Log")
    print("-" * 40)
    logs = logger.get_logs()
    if logs:
        print(logs)
    else:
        print("(Logging disabled or no logs generated)")
    print()

    # Cleanup
    agent.cleanup()
    print("Agent cleaned up successfully")
    print()
    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
