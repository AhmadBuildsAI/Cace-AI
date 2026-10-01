from pydantic import BaseModel
from typing import Dict, List, Optional

class GraphNodeItem(BaseModel):
    id: str
    node_type: str
    label: str
    confidence: float
    required_role: Optional[str]
    properties: Dict

class GraphEdgeItem(BaseModel):
    id: str
    source_id: str
    target_id: str
    edge_type: str
    confidence: float

class GraphResponse(BaseModel):
    nodes: List[GraphNodeItem]
    edges: List[GraphEdgeItem]
    node_type_counts: Dict[str, int]
    edge_type_counts: Dict[str, int]
