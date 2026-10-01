from pydantic import BaseModel
from typing import List, Optional

class SecurityEventItem(BaseModel):
    id: str
    threat_type: str
    severity: str
    confidence: float
    reasoning: Optional[str]
    blocked: str
    created_at: str

class SecurityDashboard(BaseModel):
    total_events: int
    blocked_count: int
    threat_distribution: List[dict]
    recent_events: List[SecurityEventItem]
