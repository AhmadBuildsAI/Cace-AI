from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from ..core.database import Base
import uuid

class GraphEdge(Base):
    __tablename__ = "graph_edges"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("graph_nodes.id"), nullable=False, index=True)
    target_id = Column(UUID(as_uuid=True), ForeignKey("graph_nodes.id"), nullable=False, index=True)
    edge_type = Column(String(50), nullable=False, index=True)
    properties = Column(JSONB, nullable=False, default=dict)
    confidence = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime, server_default=func.now())
