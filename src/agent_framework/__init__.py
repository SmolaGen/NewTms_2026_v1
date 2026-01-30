"""
Extensible AI Agent Framework

Core framework for building reliable AI agents with proper abstractions,
context management, and tool integration capabilities.
"""

from agent_framework.agent import Agent
from agent_framework.tools import Tool, ToolRegistry

__version__ = "0.1.0"
__author__ = "Auto-Claude"
__all__ = ["Agent", "Tool", "ToolRegistry"]
