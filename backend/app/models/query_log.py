from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from ..core.database import Base
import uuid

class QueryLog(Base):
    __tablename__ = "query_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_ref = Column(String(20), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    user_role = Column(String(50), nullable=False)
    
    original_query = Column(Text, nullable=False)
    sanitized_query = Column(Text, nullable=True)
    final_answer = Column(Text, nullable=True)
    
    confidence = Column(Float, nullable=True)
    validation_passed = Column(String(20), nullable=True)
    threat_detected = Column(String(50), nullable=True)
    
    citations = Column(JSONB, nullable=True)
    context_node_ids = Column(JSONB, nullable=True)
    
    latency_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
