"""
Benchmark report generation module.

This module provides utilities for generating JSON and markdown reports
from benchmark test results.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


class BenchmarkReport:
    """
    Generate benchmark reports in multiple formats.

    Attributes:
        results: List of benchmark test results.
        metadata: Additional metadata about the benchmark run.
    """

    def __init__(self, results: Optional[List[Dict[str, Any]]] = None):
        """
        Initialize a benchmark report.

        Args:
            results: List of benchmark test results.
        """
        self.results = results or []
        self.metadata = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "total_duration": 0.0
        }

    def add_result(
        self,
        test_name: str,
        status: str,
        duration: float,
        memory_used: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a benchmark test result.

        Args:
            test_name: Name of the test.
            status: Test status (passed, failed, skipped).
            duration: Test duration in seconds.
            memory_used: Memory used in bytes (optional).
            details: Additional test details (optional).
        """
        result = {
            "test_name": test_name,
            "status": status,
            "duration": duration,
            "memory_used": memory_used,
            "details": details or {}
        }

        self.results.append(result)

        # Update metadata
        self.metadata["total_tests"] += 1
        self.metadata["total_duration"] += duration

        if status == "passed":
            self.metadata["passed"] += 1
        elif status == "failed":
            self.metadata["failed"] += 1
        elif status == "skipped":
            self.metadata["skipped"] += 1

    def to_json(self) -> Dict[str, Any]:
        """
        Convert the report to a JSON-serializable dictionary.

        Returns:
            Dictionary containing all benchmark results and metadata.
        """
        return {
            "metadata": self.metadata,
            "results": self.results,
            "summary": self._generate_summary()
        }

    def to_markdown(self) -> str:
        """
        Convert the report to a markdown-formatted string.

        Returns:
            Markdown-formatted benchmark report.
        """
        lines = []

        # Header
        lines.append("# Benchmark Results")
        lines.append("")
        lines.append(f"**Timestamp:** {self.metadata['timestamp']}")
        lines.append("")

        # Summary
        summary = self._generate_summary()
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Total Tests:** {self.metadata['total_tests']}")
        lines.append(f"- **Passed:** {self.metadata['passed']} ✅")
        lines.append(f"- **Failed:** {self.metadata['failed']} ❌")
        lines.append(f"- **Skipped:** {self.metadata['skipped']} ⏭️")
        lines.append(f"- **Total Duration:** {self.metadata['total_duration']:.3f}s")
        lines.append(f"- **Success Rate:** {summary['success_rate']:.1f}%")
        lines.append("")

        # Performance requirements
        if summary['performance_requirements']:
            lines.append("## Performance Requirements")
            lines.append("")
            for req_name, req_result in summary['performance_requirements'].items():
                status_icon = "✅" if req_result['met'] else "❌"
                lines.append(f"- **{req_name}:** {status_icon} {req_result['description']}")
            lines.append("")

        # Detailed results
        lines.append("## Detailed Results")
        lines.append("")
        lines.append("| Test Name | Status | Duration | Memory Used |")
        lines.append("|-----------|--------|----------|-------------|")

        for result in self.results:
            status_icon = {
                "passed": "✅",
                "failed": "❌",
                "skipped": "⏭️"
            }.get(result["status"], "❓")

            memory_str = "N/A"
            if result.get("memory_used"):
                memory_mb = result["memory_used"] / (1024 * 1024)
                memory_str = f"{memory_mb:.1f} MB"

            lines.append(
                f"| {result['test_name']} | {status_icon} {result['status']} | "
                f"{result['duration']:.3f}s | {memory_str} |"
            )

        lines.append("")

        # Performance metrics
        if any(r.get("details") for r in self.results):
            lines.append("## Performance Metrics")
            lines.append("")

            for result in self.results:
                if result.get("details"):
                    lines.append(f"### {result['test_name']}")
                    lines.append("")

                    for key, value in result["details"].items():
                        lines.append(f"- **{key}:** {value}")

                    lines.append("")

        return "\n".join(lines)

    def _generate_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of the benchmark results.

        Returns:
            Summary dictionary with key metrics.
        """
        total = self.metadata["total_tests"]
        passed = self.metadata["passed"]

        success_rate = (passed / total * 100) if total > 0 else 0.0

        # Check performance requirements
        performance_requirements = self._check_performance_requirements()

        return {
            "success_rate": success_rate,
            "all_passed": self.metadata["failed"] == 0,
            "performance_requirements": performance_requirements
        }

    def _check_performance_requirements(self) -> Dict[str, Dict[str, Any]]:
        """
        Check if performance requirements are met.

        Returns:
            Dictionary of requirement checks.
        """
        requirements = {}

        # Check for context indexing performance (100+ files in <5s)
        context_tests = [
            r for r in self.results
            if "medium_codebase_indexing" in r["test_name"]
        ]

        if context_tests:
            test = context_tests[0]
            met = test["status"] == "passed" and test["duration"] < 5.0
            requirements["context_indexing_100_files"] = {
                "met": met,
                "description": f"100+ files indexed in {test['duration']:.3f}s (requirement: <5s)"
            }

        # Check for multi-file reasoning
        reasoning_tests = [
            r for r in self.results
            if "reasoning" in r["test_name"] and r["status"] == "passed"
        ]

        if reasoning_tests:
            coherent_count = len(reasoning_tests)
            requirements["multi_file_reasoning"] = {
                "met": coherent_count > 0,
                "description": f"{coherent_count} reasoning tests passed"
            }

        # Check for memory usage
        memory_tests = [
            r for r in self.results
            if r.get("memory_used") is not None
        ]

        if memory_tests:
            max_memory = max(r["memory_used"] for r in memory_tests)
            max_memory_mb = max_memory / (1024 * 1024)
            met = max_memory_mb < 100  # 100MB limit
            requirements["memory_usage"] = {
                "met": met,
                "description": f"Max memory usage: {max_memory_mb:.1f}MB (requirement: <100MB)"
            }

        return requirements

    def save_json(self, filepath: str) -> None:
        """
        Save the report as a JSON file.

        Args:
            filepath: Path to save the JSON file.
        """
        report_data = self.to_json()

        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2)

    def save_markdown(self, filepath: str) -> None:
        """
        Save the report as a markdown file.

        Args:
            filepath: Path to save the markdown file.
        """
        markdown_content = self.to_markdown()

        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)

        with open(filepath, 'w') as f:
            f.write(markdown_content)


def parse_pytest_output(output: str, exit_code: int) -> BenchmarkReport:
    """
    Parse pytest output to create a benchmark report.

    Args:
        output: Pytest output string.
        exit_code: Pytest exit code.

    Returns:
        BenchmarkReport instance with parsed results.
    """
    report = BenchmarkReport()

    # Parse pytest output for test results
    # This is a simple parser - in production you might use pytest-json-report
    lines = output.split('\n')

    for line in lines:
        # Look for test result lines (e.g., "test_name PASSED" or "test_name FAILED")
        if 'PASSED' in line or 'FAILED' in line or 'SKIPPED' in line:
            parts = line.split()
            if len(parts) >= 2:
                test_name = parts[0]
                status = "passed" if "PASSED" in line else "failed" if "FAILED" in line else "skipped"

                # Extract duration if available (format: [0.123s])
                duration = 0.0
                for part in parts:
                    if part.startswith('[') and 's]' in part:
                        try:
                            duration = float(part.strip('[]s'))
                        except ValueError:
                            pass

                report.add_result(
                    test_name=test_name,
                    status=status,
                    duration=duration
                )

    # If no results were parsed, add a summary result based on exit code
    if not report.results:
        status = "passed" if exit_code == 0 else "failed"
        report.add_result(
            test_name="benchmark_suite",
            status=status,
            duration=0.0,
            details={"exit_code": exit_code}
        )

    return report
