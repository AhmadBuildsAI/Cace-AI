from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from ..core.database import Base
import uuid

class AgentTrace(Base):
    __tablename__ = "agent_traces"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey("query_logs.id"), nullable=False, index=True)
    step = Column(Integer, nullable=False)
    agent_name = Column(String(50), nullable=False)
    
    input_summary = Column(Text, nullable=True)
    output_json = Column(JSONB, nullable=False)
    latency_ms = Column(Float, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
