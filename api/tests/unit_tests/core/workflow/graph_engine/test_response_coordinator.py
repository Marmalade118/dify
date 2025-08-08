from unittest.mock import Mock

from core.workflow.enums import NodeExecutionType, NodeType
from core.workflow.graph import Edge, Graph, Node
from core.workflow.graph_engine.output_registry import OutputRegistry
from core.workflow.graph_engine.response_coordinator import ResponseStreamCoordinator


class TestResponseStreamCoordinator:
    def test_register_builds_and_saves_paths_map(self):
        """Test that register method builds and saves paths map for response nodes."""
        # Create mock nodes
        start_node = Mock(spec=Node)
        start_node.id = "start"
        start_node.type_ = NodeType.START
        start_node.execution_type = NodeExecutionType.EXECUTABLE

        branch_node = Mock(spec=Node)
        branch_node.id = "if_else_1"
        branch_node.type_ = NodeType.IF_ELSE
        branch_node.execution_type = NodeExecutionType.BRANCH

        response_node = Mock(spec=Node)
        response_node.id = "response_1"
        response_node.type_ = NodeType.ANSWER
        response_node.execution_type = NodeExecutionType.RESPONSE

        # Create edges
        edge1 = Edge(id="e1", tail="start", head="if_else_1")
        edge2 = Edge(id="e2", tail="if_else_1", head="response_1", source_handle="true")

        # Build graph
        nodes: dict[str, Node] = {
            "start": start_node,
            "if_else_1": branch_node,
            "response_1": response_node,
        }

        edges = {"e1": edge1, "e2": edge2}

        in_edges = {
            "if_else_1": ["e1"],
            "response_1": ["e2"],
        }

        out_edges = {
            "start": ["e1"],
            "if_else_1": ["e2"],
        }

        graph = Graph(nodes=nodes, edges=edges, in_edges=in_edges, out_edges=out_edges, root_node=start_node)

        # Create coordinator
        registry = OutputRegistry()
        coordinator = ResponseStreamCoordinator(registry, graph)

        # Verify initial state
        assert "response_1" not in coordinator._response_nodes
        assert "response_1" not in coordinator._paths_maps

        # Register the response node
        coordinator.register("response_1")

        # Verify the node is registered
        assert "response_1" in coordinator._response_nodes

        # Verify the paths map is built and saved
        assert "response_1" in coordinator._paths_maps
        paths_map = coordinator._paths_maps["response_1"]

        # Verify the paths map content - should have one path with edge e2
        assert len(paths_map) == 1
        assert paths_map[0].contains_edge("e2")
