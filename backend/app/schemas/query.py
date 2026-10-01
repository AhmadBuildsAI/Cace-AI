from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class QueryRequest(BaseModel):
    query: str = Field(min_length=3, max_length=2000)

class Citation(BaseModel):
    node_id: str
    label: str
    quote: str

class AgentStep(BaseModel):
    step: int
    agent_name: str
    input_summary: str
    output: Dict
    latency_ms: float

class QueryResponse(BaseModel):
    query_id: str
    query_ref: str
    original_query: str
    sanitized_query: Optional[str]
    final_answer: Optional[str]
    confidence: Optional[float]
    validation_passed: Optional[str]
    threat_detected: Optional[str]
    citations: List[Citation]
    context_nodes: List[Dict]
    agent_steps: List[AgentStep]
    latency_ms: float
    created_at: str

class QueryListItem(BaseModel):
    id: str
    query_ref: str
    query_snippet: str
    confidence: Optional[float]
    validation_passed: Optional[str]
    threat_detected: Optional[str]
    latency_ms: Optional[float]
    created_at: str
