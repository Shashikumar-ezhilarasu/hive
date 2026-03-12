"""Agent graph construction for Startup Opportunity Scanner."""

from typing import Any, TYPE_CHECKING

from framework.graph import (
    EdgeSpec,
    EdgeCondition,
    Goal,
    SuccessCriterion,
    Constraint,
    NodeSpec,
)
from framework.graph.edge import GraphSpec
from framework.graph.executor import ExecutionResult, GraphExecutor
from framework.runtime.event_bus import EventBus
from framework.runtime.core import Runtime
from framework.llm import LiteLLMProvider
from framework.runner.tool_registry import ToolRegistry

from .config import default_config, metadata, RuntimeConfig
from .nodes import (
    market_signal_node,
    trend_analysis_node,
    opportunity_generation_node,
    scoring_node,
)

if TYPE_CHECKING:
    from framework.config import RuntimeConfig

# Goal definition
goal: Goal = Goal(
    id="startup-opportunity-scan",
    name="Startup Opportunity Scan",
    description=(
        "Scan market signals across a given domain, analyze trends, generate "
        "startup opportunity proposals, and score them to surface the top 5 "
        "most promising ideas with detailed justification."
    ),
    success_criteria=[
        SuccessCriterion(
            id="sc-signal-diversity",
            description="Gather signals from at least 3 of 4 categories (technology, complaints, underserved, regulatory)",
            metric="signal_categories",
            target=">=3",
            weight=0.20,
        ),
        SuccessCriterion(
            id="sc-trend-coverage",
            description="Identify trends across sector growth, funding, and technology shifts",
            metric="trend_categories",
            target=">=2",
            weight=0.20,
        ),
        SuccessCriterion(
            id="sc-opportunity-count",
            description="Generate at least 8 concrete startup opportunities",
            metric="opportunity_count",
            target=">=8",
            weight=0.20,
        ),
        SuccessCriterion(
            id="sc-scoring-completeness",
            description="Score all opportunities on 4 criteria and rank the top 5",
            metric="top_opportunities_count",
            target=">=5",
            weight=0.20,
        ),
        SuccessCriterion(
            id="sc-report-delivered",
            description="Deliver a formatted HTML report with scored and ranked opportunities",
            metric="report_delivered",
            target="true",
            weight=0.20,
        ),
    ],
    constraints=[
        Constraint(
            id="c-no-fabrication",
            description="All market signals and trends must come from actual web sources, not fabricated data",
            constraint_type="hard",
            category="quality",
        ),
        Constraint(
            id="c-source-attribution",
            description="Every signal and trend must cite its source URL",
            constraint_type="hard",
            category="quality",
        ),
        Constraint(
            id="c-scoring-transparency",
            description="Every scoring decision must include a brief justification",
            constraint_type="hard",
            category="quality",
        ),
        Constraint(
            id="c-pinecone-optional",
            description="Agent must function fully without Pinecone credentials configured",
            constraint_type="hard",
            category="compatibility",
        ),
    ],
)

# Node list
nodes: list[NodeSpec] = [
    market_signal_node,
    trend_analysis_node,
    opportunity_generation_node,
    scoring_node,
]

# Edge definitions — linear pipeline
edges: list[EdgeSpec] = [
    EdgeSpec(
        id="signals-to-trends",
        source="market-signals",
        target="trend-analysis",
        condition=EdgeCondition.ON_SUCCESS,
        priority=1,
    ),
    EdgeSpec(
        id="trends-to-opportunities",
        source="trend-analysis",
        target="opportunity-generation",
        condition=EdgeCondition.ON_SUCCESS,
        priority=1,
    ),
    EdgeSpec(
        id="opportunities-to-scoring",
        source="opportunity-generation",
        target="scoring",
        condition=EdgeCondition.ON_SUCCESS,
        priority=1,
    ),
]

# Graph configuration
entry_node: str = "market-signals"
entry_points: dict[str, str] = {"start": "market-signals"}
pause_nodes: list[str] = []
terminal_nodes: list[str] = ["scoring"]


class StartupOpportunityScannerAgent:
    """
    Startup Opportunity Scanner Agent — 4-node pipeline.

    Flow: market-signals -> trend-analysis -> opportunity-generation -> scoring

    Scans a domain for market signals, identifies trends, generates startup
    ideas, and scores them to deliver the top 5 opportunities.
    """

    def __init__(self, config: RuntimeConfig | None = None) -> None:
        """Initialize the agent.

        Args:
            config: Optional runtime configuration. Defaults to default_config.
        """
        self.config = config or default_config
        self.goal = goal
        self.nodes = nodes
        self.edges = edges
        self.entry_node = entry_node
        self.entry_points = entry_points
        self.pause_nodes = pause_nodes
        self.terminal_nodes = terminal_nodes
        self._executor: GraphExecutor | None = None
        self._graph: GraphSpec | None = None
        self._event_bus: EventBus | None = None
        self._tool_registry: ToolRegistry | None = None

    def _build_graph(self) -> GraphSpec:
        """Build the GraphSpec for the opportunity scanning pipeline.

        Returns:
            A GraphSpec defining the agent's logic.
        """
        return GraphSpec(
            id="startup-opportunity-scanner-graph",
            goal_id=self.goal.id,
            version="1.0.0",
            entry_node=self.entry_node,
            entry_points=self.entry_points,
            terminal_nodes=self.terminal_nodes,
            pause_nodes=self.pause_nodes,
            nodes=self.nodes,
            edges=self.edges,
            default_model=self.config.model,
            max_tokens=self.config.max_tokens,
            loop_config={
                "max_iterations": 100,
                "max_tool_calls_per_turn": 30,
                "max_history_tokens": 32000,
            },
        )

    def _setup(self) -> GraphExecutor:
        """Set up the executor with all components.

        Returns:
            An initialized GraphExecutor instance.
        """
        from pathlib import Path

        storage_path = Path.home() / ".hive" / "agents" / "startup_opportunity_scanner"
        storage_path.mkdir(parents=True, exist_ok=True)

        self._event_bus = EventBus()
        self._tool_registry = ToolRegistry()

        mcp_config_path = Path(__file__).parent / "mcp_servers.json"
        if mcp_config_path.exists():
            self._tool_registry.load_mcp_config(mcp_config_path)

        llm = LiteLLMProvider(
            model=self.config.model,
            api_key=self.config.api_key,
            api_base=self.config.api_base,
        )

        tool_executor = self._tool_registry.get_executor()
        tools = list(self._tool_registry.get_tools().values())

        self._graph = self._build_graph()
        runtime = Runtime(storage_path)

        self._executor = GraphExecutor(
            runtime=runtime,
            llm=llm,
            tools=tools,
            tool_executor=tool_executor,
            event_bus=self._event_bus,
            storage_path=storage_path,
            loop_config=self._graph.loop_config,
        )

        return self._executor

    async def start(self) -> None:
        """Set up the agent (initialize executor and tools)."""
        if self._executor is None:
            self._setup()

    async def stop(self) -> None:
        """Clean up resources."""
        self._executor = None
        self._event_bus = None

    async def trigger_and_wait(
        self,
        entry_point: str,
        input_data: dict[str, Any],
        timeout: float | None = None,
        session_state: dict[str, Any] | None = None,
    ) -> ExecutionResult | None:
        """Execute the graph and wait for completion.

        Args:
            entry_point: The graph entry point to trigger.
            input_data: Data to pass to the entry node.
            timeout: Optional execution timeout.
            session_state: Optional initial session state.

        Returns:
            The execution result, or None if it timed out.
        """
        if self._executor is None:
            raise RuntimeError("Agent not started. Call start() first.")
        if self._graph is None:
            raise RuntimeError("Graph not built. Call start() first.")

        return await self._executor.execute(
            graph=self._graph,
            goal=self.goal,
            input_data=input_data,
            session_state=session_state,
        )

    async def run(
        self, context: dict[str, Any], session_state: dict[str, Any] | None = None
    ) -> ExecutionResult:
        """Run the agent (convenience method for single execution).

        Args:
            context: The input context for the agent.
            session_state: Optional initial session state.

        Returns:
            The final execution result.
        """
        await self.start()
        try:
            result = await self.trigger_and_wait(
                "start", context, session_state=session_state
            )
            return result or ExecutionResult(success=False, error="Execution timeout")
        finally:
            await self.stop()

    def info(self) -> dict[str, Any]:
        """Get agent information for introspection."""
        return {
            "name": metadata.name,
            "version": metadata.version,
            "description": metadata.description,
            "goal": {
                "name": self.goal.name,
                "description": self.goal.description,
            },
            "nodes": [n.id for n in self.nodes],
            "edges": [e.id for e in self.edges],
            "entry_node": self.entry_node,
            "entry_points": self.entry_points,
            "pause_nodes": self.pause_nodes,
            "terminal_nodes": self.terminal_nodes,
            "client_facing_nodes": [n.id for n in self.nodes if n.client_facing],
        }

    def validate(self) -> dict[str, Any]:
        """Validate agent structure for missing nodes or invalid edges.

        Returns:
            A dict with 'valid' (bool), 'errors' (list), and 'warnings' (list).
        """
        errors: list[str] = []
        warnings: list[str] = []

        node_ids = {node.id for node in self.nodes}
        for edge in self.edges:
            if edge.source not in node_ids:
                errors.append(f"Edge {edge.id}: source '{edge.source}' not found")
            if edge.target not in node_ids:
                errors.append(f"Edge {edge.id}: target '{edge.target}' not found")

        if self.entry_node not in node_ids:
            errors.append(f"Entry node '{self.entry_node}' not found")

        for terminal in self.terminal_nodes:
            if terminal not in node_ids:
                errors.append(f"Terminal node '{terminal}' not found")

        for ep_id, node_id in self.entry_points.items():
            if node_id not in node_ids:
                errors.append(
                    f"Entry point '{ep_id}' references unknown node '{node_id}'"
                )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }


# Create default instance
default_agent: StartupOpportunityScannerAgent = StartupOpportunityScannerAgent()
