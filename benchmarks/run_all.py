#!/usr/bin/env python
"""
Run all benchmarks and generate comprehensive reports.

This script executes all benchmark tests and generates JSON and markdown
reports with timing, memory, and pass/fail metrics.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# Add project root to path to import modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from benchmarks.report import BenchmarkReport


def run_pytest_benchmarks(benchmark_dir: str, verbose: bool = True) -> tuple:
    """
    Run pytest benchmarks and capture output.

    Args:
        benchmark_dir: Directory containing benchmark tests.
        verbose: Whether to show verbose output.

    Returns:
        Tuple of (exit_code, stdout, stderr).
    """
    pytest_args = [
        sys.executable, "-m", "pytest",
        benchmark_dir,
        "-v" if verbose else "",
        "-m", "benchmark",
        "--tb=short",
        "-p", "no:warnings"
    ]

    # Filter out empty strings
    pytest_args = [arg for arg in pytest_args if arg]

    try:
        result = subprocess.run(
            pytest_args,
            capture_output=True,
            text=True,
            cwd=project_root
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        print(f"Error running pytest: {e}")
        return 1, "", str(e)


def parse_pytest_json_output(json_path: str) -> BenchmarkReport:
    """
    Parse pytest JSON output to create a benchmark report.

    Args:
        json_path: Path to pytest JSON report file.

    Returns:
        BenchmarkReport instance with parsed results.
    """
    report = BenchmarkReport()

    try:
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Parse pytest-json-report format
        for test in data.get("tests", []):
            test_name = test.get("nodeid", "unknown")
            outcome = test.get("outcome", "unknown")

            # Map pytest outcomes to our status
            status_map = {
                "passed": "passed",
                "failed": "failed",
                "skipped": "skipped",
                "xfailed": "skipped",
                "xpassed": "passed"
            }
            status = status_map.get(outcome, "unknown")

            duration = test.get("duration", 0.0)

            # Extract additional details
            details = {}
            if "call" in test:
                call_info = test["call"]
                if "longrepr" in call_info:
                    details["error"] = str(call_info["longrepr"])

            report.add_result(
                test_name=test_name,
                status=status,
                duration=duration,
                details=details if details else None
            )

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not parse JSON report: {e}")

    return report


def parse_pytest_output_text(output: str, exit_code: int) -> BenchmarkReport:
    """
    Parse pytest text output to create a benchmark report.

    Args:
        output: Pytest output string.
        exit_code: Pytest exit code.

    Returns:
        BenchmarkReport instance with parsed results.
    """
    report = BenchmarkReport()
    lines = output.split('\n')

    current_test = None
    for line in lines:
        line = line.strip()

        # Look for test result lines
        # Format: "benchmarks/test_file.py::test_name PASSED [duration]"
        if '::' in line and any(status in line for status in ['PASSED', 'FAILED', 'SKIPPED']):
            parts = line.split()

            if len(parts) >= 2:
                # Extract test name (e.g., "benchmarks/test.py::test_name")
                test_full_name = parts[0]
                if '::' in test_full_name:
                    test_name = test_full_name.split('::')[-1]
                else:
                    test_name = test_full_name

                # Extract status
                status = None
                if 'PASSED' in line:
                    status = "passed"
                elif 'FAILED' in line:
                    status = "failed"
                elif 'SKIPPED' in line:
                    status = "skipped"

                # Extract duration
                duration = 0.0
                for i, part in enumerate(parts):
                    if part == 'PASSED' or part == 'FAILED' or part == 'SKIPPED':
                        # Duration might be in next part [0.123s]
                        if i + 1 < len(parts):
                            duration_str = parts[i + 1].strip('[]s')
                            try:
                                duration = float(duration_str)
                            except ValueError:
                                pass
                        break

                if status:
                    report.add_result(
                        test_name=test_name,
                        status=status,
                        duration=duration
                    )

    # If no results were parsed, add a summary based on exit code
    if not report.results:
        status = "passed" if exit_code == 0 else "failed"
        report.add_result(
            test_name="benchmark_suite",
            status=status,
            duration=0.0,
            details={"exit_code": exit_code, "note": "No individual test results parsed"}
        )

    return report


def main():
    """
    Main entry point for running all benchmarks.
    """
    print("=" * 70)
    print("Running Agent Framework Benchmarks")
    print("=" * 70)
    print()

    benchmark_dir = os.path.join(project_root, "benchmarks")

    # Check if benchmark directory exists
    if not os.path.exists(benchmark_dir):
        print(f"Error: Benchmark directory not found: {benchmark_dir}")
        sys.exit(1)

    # Run benchmarks
    print("Executing benchmark tests...")
    print()

    exit_code, stdout, stderr = run_pytest_benchmarks(benchmark_dir, verbose=True)

    # Print pytest output
    print(stdout)
    if stderr:
        print("Errors:", file=sys.stderr)
        print(stderr, file=sys.stderr)

    print()
    print("=" * 70)
    print("Generating Reports")
    print("=" * 70)
    print()

    # Try to parse pytest-json-report output first
    json_report_path = os.path.join(benchmark_dir, ".pytest_cache", "report.json")

    if os.path.exists(json_report_path):
        print("Parsing JSON report...")
        report = parse_pytest_json_output(json_report_path)
    else:
        print("Parsing text output...")
        report = parse_pytest_output_text(stdout, exit_code)

    # Generate and save reports
    results_json_path = os.path.join(benchmark_dir, "results.json")
    results_md_path = os.path.join(benchmark_dir, "results.md")

    print(f"Saving JSON report to: {results_json_path}")
    report.save_json(results_json_path)

    print(f"Saving Markdown report to: {results_md_path}")
    report.save_markdown(results_md_path)

    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print()

    summary = report.to_json()["summary"]
    metadata = report.metadata

    print(f"Total Tests: {metadata['total_tests']}")
    print(f"Passed: {metadata['passed']} ✅")
    print(f"Failed: {metadata['failed']} ❌")
    print(f"Skipped: {metadata['skipped']} ⏭️")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Total Duration: {metadata['total_duration']:.3f}s")
    print()

    # Performance requirements
    if summary['performance_requirements']:
        print("Performance Requirements:")
        for req_name, req_result in summary['performance_requirements'].items():
            status_icon = "✅" if req_result['met'] else "❌"
            print(f"  {status_icon} {req_name}: {req_result['description']}")
        print()

    # Exit with pytest's exit code
    if summary['all_passed']:
        print("🎉 All benchmarks passed!")
        sys.exit(0)
    else:
        print("⚠️  Some benchmarks failed.")
        sys.exit(exit_code if exit_code != 0 else 1)


if __name__ == "__main__":
    main()
