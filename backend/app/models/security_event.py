from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from ..core.database import Base
import uuid

class SecurityEvent(Base):
    __tablename__ = "security_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey("query_logs.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    threat_type = Column(String(80), nullable=False, index=True)
    severity = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=True)
    evidence = Column(JSONB, nullable=True)
    blocked = Column(String(10), nullable=False, default="true")
    
    created_at = Column(DateTime, server_default=func.now(), index=True)
