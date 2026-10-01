from sqlalchemy import Column, String, Float, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from ..core.database import Base
import uuid

class GraphNode(Base):
    __tablename__ = "graph_nodes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_type = Column(String(50), nullable=False, index=True)
    label = Column(String(255), nullable=False)
    properties = Column(JSONB, nullable=False, default=dict)
    
    confidence = Column(Float, nullable=False, default=1.0)
    source = Column(String(255), nullable=True)
    valid_from = Column(DateTime, nullable=True)
    valid_to = Column(DateTime, nullable=True)
    
    required_role = Column(String(50), nullable=True)  # role-based access
    
    created_at = Column(DateTime, server_default=func.now())
