"""Runtime configuration for Startup Opportunity Scanner."""

from dataclasses import dataclass

from framework.config import RuntimeConfig

default_config: RuntimeConfig = RuntimeConfig()


@dataclass
class AgentMetadata:
    """Metadata for the Startup Opportunity Scanner agent."""

    name: str = "Startup Opportunity Scanner"
    version: str = "1.0.0"
    description: str = (
        "Scans market signals, analyzes trends, generates startup ideas, "
        "and scores opportunities to surface the top 5 startup ideas in any "
        "given domain — with optional Pinecone vector search for deeper insights."
    )
    intro_message: str = (
        "Hi! I'm your startup opportunity scanner. Tell me a domain or industry "
        "(e.g. 'climate tech', 'AI in healthcare', 'fintech for SMBs') and I'll "
        "research market signals, identify trends, generate startup ideas, and "
        "rank the top 5 opportunities for you."
    )


metadata: AgentMetadata = AgentMetadata()
