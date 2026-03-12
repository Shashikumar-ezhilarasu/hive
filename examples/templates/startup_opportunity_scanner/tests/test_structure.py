"""Structural tests for Startup Opportunity Scanner."""

from startup_opportunity_scanner import (
    default_agent,
    goal,
    nodes,
    edges,
    entry_node,
    entry_points,
    terminal_nodes,
)


class TestGoalDefinition:
    """Test the agent goal is correctly defined."""

    def test_goal_exists(self):
        assert goal is not None
        assert goal.id == "startup-opportunity-scan"

    def test_goal_has_success_criteria(self):
        assert len(goal.success_criteria) == 5

    def test_success_criteria_weights_sum_to_one(self):
        total = sum(sc.weight for sc in goal.success_criteria)
        assert abs(total - 1.0) < 0.01

    def test_goal_has_constraints(self):
        assert len(goal.constraints) == 4
        constraint_ids = {c.id for c in goal.constraints}
        assert "c-no-fabrication" in constraint_ids
        assert "c-source-attribution" in constraint_ids
        assert "c-pinecone-optional" in constraint_ids


class TestNodeStructure:
    """Test node definitions."""

    def test_four_nodes(self):
        assert len(nodes) == 4

    def test_node_ids(self):
        node_ids = [n.id for n in nodes]
        assert node_ids == [
            "market-signals",
            "trend-analysis",
            "opportunity-generation",
            "scoring",
        ]

    def test_market_signals_node(self):
        node = nodes[0]
        assert node.id == "market-signals"
        assert node.client_facing is False
        assert "web_search" in node.tools
        assert "web_scrape" in node.tools
        assert "research_brief" in node.input_keys
        assert "market_signals" in node.output_keys
        assert "signal_summary" in node.output_keys

    def test_trend_analysis_node(self):
        node = nodes[1]
        assert node.id == "trend-analysis"
        assert node.client_facing is False
        assert "web_search" in node.tools
        assert "market_signals" in node.input_keys
        assert "trends" in node.output_keys

    def test_opportunity_generation_node(self):
        node = nodes[2]
        assert node.id == "opportunity-generation"
        assert node.client_facing is False
        assert "market_signals" in node.input_keys
        assert "trends" in node.input_keys
        assert "opportunities" in node.output_keys

    def test_scoring_node_is_client_facing(self):
        node = nodes[3]
        assert node.id == "scoring"
        assert node.client_facing is True
        assert "serve_file_to_user" in node.tools
        assert "top_opportunities" in node.output_keys
        assert "delivery_status" in node.output_keys

    def test_pinecone_tools_are_optional(self):
        """Pinecone tools are listed but agent does not require them."""
        for node in nodes:
            # Pinecone tools can appear in tool lists, but the agent must
            # still function without Pinecone credentials.
            if "pinecone_query_vectors" in node.tools:
                assert node.node_type == "event_loop"


class TestEdgeStructure:
    """Test edge definitions form a valid pipeline."""

    def test_three_edges(self):
        assert len(edges) == 3

    def test_linear_pipeline(self):
        assert edges[0].source == "market-signals"
        assert edges[0].target == "trend-analysis"
        assert edges[1].source == "trend-analysis"
        assert edges[1].target == "opportunity-generation"
        assert edges[2].source == "opportunity-generation"
        assert edges[2].target == "scoring"

    def test_all_edges_on_success(self):
        for edge in edges:
            assert edge.condition.value == "on_success"


class TestGraphConfiguration:
    """Test graph-level configuration."""

    def test_entry_node(self):
        assert entry_node == "market-signals"

    def test_entry_points(self):
        assert entry_points == {"start": "market-signals"}

    def test_terminal_nodes(self):
        assert terminal_nodes == ["scoring"]


class TestAgentClass:
    """Test the agent class itself."""

    def test_default_agent_created(self):
        assert default_agent is not None

    def test_validate_passes(self):
        result = default_agent.validate()
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_agent_info(self):
        info = default_agent.info()
        assert info["name"] == "Startup Opportunity Scanner"
        assert info["version"] == "1.0.0"
        assert "market-signals" in info["nodes"]
        assert "trend-analysis" in info["nodes"]
        assert "opportunity-generation" in info["nodes"]
        assert "scoring" in info["nodes"]

    def test_client_facing_nodes(self):
        info = default_agent.info()
        assert info["client_facing_nodes"] == ["scoring"]

    def test_edge_count(self):
        info = default_agent.info()
        assert len(info["edges"]) == 3


class TestRunnerLoad:
    """Test AgentRunner can load the agent."""

    def test_agent_runner_load_succeeds(self, runner_loaded):
        assert runner_loaded is not None
