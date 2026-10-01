"""Graph query helpers."""
from typing import List, Dict, Optional
import networkx as nx
from sqlalchemy.orm import Session
from ..models.graph_node import GraphNode
from ..models.graph_edge import GraphEdge
from ..schemas.graph import GraphNodeItem, GraphEdgeItem, GraphResponse


def get_full_graph(db: Session, user_role: str, max_nodes: int = 200) -> GraphResponse:
    nodes = db.query(GraphNode).limit(max_nodes).all()
    # Role filtering
    visible_nodes = [
        n for n in nodes
        if not n.required_role or n.required_role == user_role or user_role == "admin"
    ]
    visible_ids = {n.id for n in visible_nodes}
    
    edges = db.query(GraphEdge).all()
    visible_edges = [e for e in edges if e.source_id in visible_ids and e.target_id in visible_ids]
    
    node_type_counts: Dict[str, int] = {}
    for n in visible_nodes:
        node_type_counts[n.node_type] = node_type_counts.get(n.node_type, 0) + 1
    
    edge_type_counts: Dict[str, int] = {}
    for e in visible_edges:
        edge_type_counts[e.edge_type] = edge_type_counts.get(e.edge_type, 0) + 1
    
    return GraphResponse(
        nodes=[
            GraphNodeItem(
                id=str(n.id),
                node_type=n.node_type,
                label=n.label,
                confidence=n.confidence,
                required_role=n.required_role,
                properties=n.properties or {},
            ) for n in visible_nodes
        ],
        edges=[
            GraphEdgeItem(
                id=str(e.id),
                source_id=str(e.source_id),
                target_id=str(e.target_id),
                edge_type=e.edge_type,
                confidence=e.confidence,
            ) for e in visible_edges
        ],
        node_type_counts=node_type_counts,
        edge_type_counts=edge_type_counts,
    )


def traverse_context(db: Session, start_node_id: str, max_depth: int = 2, user_role: str = "analyst") -> Dict:
    """Role-aware NetworkX traversal over the persisted CKG."""
    nodes = db.query(GraphNode).all()
    visible = [
        n for n in nodes
        if not n.required_role or n.required_role == user_role or user_role == "admin"
    ]
    visible_ids = {str(n.id) for n in visible}
    edges = [
        e for e in db.query(GraphEdge).all()
        if str(e.source_id) in visible_ids and str(e.target_id) in visible_ids
    ]
    graph = nx.DiGraph()
    graph.add_nodes_from(visible_ids)
    graph.add_edges_from((str(e.source_id), str(e.target_id), {"edge_type": e.edge_type}) for e in edges)
    if str(start_node_id) not in graph:
        return {"start_node_id": start_node_id, "nodes": [], "edges": []}
    reachable = nx.single_source_shortest_path_length(graph, str(start_node_id), cutoff=max_depth)
    node_map = {str(n.id): n for n in visible}
    result_nodes = [
        {
            "id": nid,
            "label": node_map[nid].label,
            "node_type": node_map[nid].node_type,
            "confidence": node_map[nid].confidence,
        }
        for nid in reachable
        if nid in node_map
    ]
    result_edges = [
        {"source_id": u, "target_id": v, "edge_type": data.get("edge_type", "")}
        for u, v, data in graph.edges(data=True)
        if u in reachable and v in reachable
    ]
    return {"start_node_id": start_node_id, "nodes": result_nodes, "edges": result_edges}
