"""Node definitions for Startup Opportunity Scanner."""

from pathlib import Path

from framework.graph import NodeSpec


def _load_prompt(filename: str) -> str:
    """Load a prompt from the prompts/ directory."""
    prompt_path = Path(__file__).parent.parent / "prompts" / filename
    return prompt_path.read_text()


# Node 1: Market Signal Detection
# Searches the web for emerging technologies, user complaints, underserved
# markets, and regulatory changes in the target domain.
market_signal_node: NodeSpec = NodeSpec(
    id="market-signals",
    name="Market Signal Detection",
    description="Scan web sources for market signals: emerging tech, user complaints, underserved markets, regulatory changes",
    node_type="event_loop",
    input_keys=["research_brief"],
    output_keys=["market_signals", "signal_summary"],
    system_prompt=_load_prompt("market_signal_prompt.md"),
    tools=[
        "web_search",
        "web_scrape",
        "save_data",
        "load_data",
        "list_data_files",
        "pinecone_query_vectors",
        "pinecone_upsert_vectors",
    ],
)

# Node 2: Trend Analysis
# Identifies growing sectors, funding activity, and technology shifts
# by searching for industry reports, funding data, and market analyses.
trend_analysis_node: NodeSpec = NodeSpec(
    id="trend-analysis",
    name="Trend Analysis",
    description="Identify growing sectors, funding patterns, and technological shifts in the target domain",
    node_type="event_loop",
    input_keys=["research_brief", "market_signals", "signal_summary"],
    output_keys=["trends", "trend_summary"],
    system_prompt="""\
You are a trend analysis agent. Given a research brief and initial market signals,
dig deeper to identify macro and micro trends that indicate where the market is heading.

**STEP 1 — Search for trend data (tool calls):**

Focus on three trend categories:

1. **Growing Sectors**: Which sub-sectors are expanding?
   - Search: "{domain} fastest growing segments 2026"
   - Search: "{domain} market growth forecast"
   - Search: "{domain} emerging sub-sectors"

2. **Funding Activity**: Where is money flowing?
   - Search: "{domain} startup funding 2025 2026"
   - Search: "{domain} venture capital investment trends"
   - Search: "{domain} Series A B funding rounds"

3. **Technological Shifts**: What technical changes enable new products?
   - Search: "{domain} technology disruption"
   - Search: "{domain} AI automation impact"
   - Search: "{domain} platform shift infrastructure"

Use web_search with 6-8 queries. Use web_scrape on the 4-6 best URLs.

**Important:**
- Cross-reference with the market_signals already gathered
- Look for patterns: multiple signals pointing in the same direction = strong trend
- Note where trends intersect — these intersections are often the best opportunities
- Be factual — only report data you actually find
- If Pinecone tools are available and configured, query for similar past scans

**STEP 2 — When done, call set_output (one key at a time, separate turns):**
- set_output("trends", "JSON list of trend objects, each with: category (sector_growth|funding|tech_shift), trend (description), evidence (list of supporting data points with sources), strength (strong|moderate|emerging)")
- set_output("trend_summary", "Brief synthesis of the most significant trends and how they relate to the market signals")
""",
    tools=[
        "web_search",
        "web_scrape",
        "save_data",
        "load_data",
        "list_data_files",
        "pinecone_query_vectors",
        "pinecone_upsert_vectors",
    ],
)

# Node 3: Opportunity Generation
# Cross-references signals with trends to produce 8-10 concrete startup ideas.
opportunity_generation_node: NodeSpec = NodeSpec(
    id="opportunity-generation",
    name="Opportunity Generation",
    description="Synthesize market signals and trends into concrete startup opportunity proposals",
    node_type="event_loop",
    input_keys=[
        "research_brief",
        "market_signals",
        "signal_summary",
        "trends",
        "trend_summary",
    ],
    output_keys=["opportunities", "opportunity_count"],
    system_prompt=_load_prompt("opportunity_prompt.md"),
    tools=[
        "save_data",
        "load_data",
        "list_data_files",
        "pinecone_query_vectors",
    ],
)

# Node 4: Opportunity Scoring (client-facing)
# Scores all opportunities, ranks them, selects the top 5, and delivers
# an HTML report to the user.
scoring_node: NodeSpec = NodeSpec(
    id="scoring",
    name="Opportunity Scoring & Report",
    description="Score opportunities on market size, feasibility, competition, and defensibility, then deliver a ranked top-5 report",
    node_type="event_loop",
    client_facing=True,
    input_keys=[
        "research_brief",
        "opportunities",
        "opportunity_count",
        "market_signals",
        "trends",
    ],
    output_keys=["top_opportunities", "delivery_status"],
    system_prompt=_load_prompt("scoring_prompt.md"),
    tools=[
        "save_data",
        "append_data",
        "load_data",
        "list_data_files",
        "serve_file_to_user",
        "pinecone_upsert_vectors",
    ],
)

__all__ = [
    "market_signal_node",
    "trend_analysis_node",
    "opportunity_generation_node",
    "scoring_node",
]
