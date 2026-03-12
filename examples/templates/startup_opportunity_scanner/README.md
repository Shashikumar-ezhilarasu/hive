# Startup Opportunity Scanner (Community)

An autonomous agent that scans market signals, analyzes trends, generates startup ideas, and scores opportunities to surface the **top 5 most promising startup opportunities** in any domain.

## Prerequisites

- **Python 3.11+** with `uv`
- **LLM API key** (e.g. `ANTHROPIC_API_KEY`) set in your environment or `.env`
- **PINECONE_API_KEY** *(optional)* for vector search across historical scans

## Quick Start

### Interactive Shell
```bash
cd examples/templates
PYTHONPATH=../../core:. uv run python -m startup_opportunity_scanner shell
```

### CLI Run
```bash
PYTHONPATH=../../core:. uv run python -m startup_opportunity_scanner run \
  --domain "climate tech"
```

### TUI Dashboard
```bash
PYTHONPATH=../../core:. uv run python -m startup_opportunity_scanner tui
```

### Validate & Info
```bash
PYTHONPATH=../../core:. uv run python -m startup_opportunity_scanner validate
PYTHONPATH=../../core:. uv run python -m startup_opportunity_scanner info
```

## Agent Architecture

```
market-signals -> trend-analysis -> opportunity-generation -> scoring
```

| Node | Purpose | Tools | Client-Facing |
|------|---------|-------|:---:|
| **market-signals** | Detect emerging tech, complaints, underserved markets, regulatory changes | web_search, web_scrape, pinecone_* | |
| **trend-analysis** | Identify growing sectors, funding activity, tech shifts | web_search, web_scrape, pinecone_* | |
| **opportunity-generation** | Synthesize signals + trends into 8-10 startup ideas | save_data, pinecone_query | |
| **scoring** | Score on 4 criteria, rank top 5, generate HTML report | save_data, serve_file | Yes |

### Pipeline Flow

1. **Market Signal Detection** - Searches the web for signals across 4 categories:
   - Emerging technologies and breakthroughs
   - User complaints and pain points
   - Underserved market segments
   - Regulatory and policy changes

2. **Trend Analysis** - Builds on signals to identify macro/micro trends:
   - Growing sector segments
   - Venture funding patterns
   - Technology platform shifts

3. **Opportunity Generation** - Cross-references signals with trends to produce 8-10 concrete startup ideas, each with:
   - Problem statement
   - Target customer
   - Proposed solution
   - Market size estimate
   - Monetization model

4. **Opportunity Scoring** - Scores each opportunity (1-10) on:
   - Market size (25%)
   - Technical feasibility (25%)
   - Competition level (25%)
   - Defensibility (25%)

   Delivers a ranked **top 5** as an HTML report.

## Example Input

```
"Find startup opportunities in climate tech"
```

## Example Output

The agent produces an HTML report saved to `~/.hive/agents/startup_opportunity_scanner/` containing:
- Ranked top 5 opportunities with scores
- Per-opportunity breakdown (problem, solution, market, monetization)
- Scoring justification for each criterion
- Supporting market signals and trends

## Pinecone Integration (Optional)

The agent optionally uses Pinecone vector search to:
- Store market signals and opportunities as embeddings for cross-scan analysis
- Query historical scans to identify recurring patterns and strengthen insights

Set `PINECONE_API_KEY` in your environment to enable this. The agent works fully without it.

## Running Tests

```bash
cd examples/templates
PYTHONPATH=../../core:. uv run pytest startup_opportunity_scanner/tests/ -v
```

## File Structure

```
startup_opportunity_scanner/
├── __init__.py          # Package exports
├── __main__.py          # CLI entry point (run, tui, info, validate, shell)
├── agent.py             # Goal, edges, graph spec, agent class
├── agent.json           # Agent definition (used by build-from-template)
├── config.py            # Runtime configuration and metadata
├── mcp_servers.json     # MCP tool server configuration
├── nodes/
│   └── __init__.py      # Node definitions (4 NodeSpec instances)
├── prompts/
│   ├── market_signal_prompt.md
│   ├── opportunity_prompt.md
│   └── scoring_prompt.md
├── tests/
│   ├── conftest.py      # Test fixtures
│   └── test_structure.py # Structural validation tests
└── README.md
```
