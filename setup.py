"""
Setup script for agent-framework package.

This file is maintained for backward compatibility with older pip versions
and build tools. Modern installation should use pyproject.toml.
"""

from setuptools import setup, find_packages

setup(
    name="agent-framework",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
)
