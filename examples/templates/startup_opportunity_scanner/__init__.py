"""
Startup Opportunity Scanner — Market intelligence for startup founders.

Scans market signals, analyzes trends, generates startup ideas, and scores
opportunities to surface the top 5 most promising startup opportunities
in any given domain.
"""

from .agent import (
    StartupOpportunityScannerAgent,
    default_agent,
    goal,
    nodes,
    edges,
    entry_node,
    entry_points,
    terminal_nodes,
)
from .config import RuntimeConfig, AgentMetadata, default_config, metadata

__version__ = "1.0.0"

__all__ = [
    "StartupOpportunityScannerAgent",
    "default_agent",
    "goal",
    "nodes",
    "edges",
    "entry_node",
    "entry_points",
    "terminal_nodes",
    "RuntimeConfig",
    "AgentMetadata",
    "default_config",
    "metadata",
]
