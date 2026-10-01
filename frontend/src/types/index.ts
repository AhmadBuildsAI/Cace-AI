export interface GraphNode {
  id: string;
  node_type: string;
  label: string;
  confidence: number;
  required_role: string | null;
  properties: Record<string, any>;
}

export interface GraphEdge {
  id: string;
  source_id: string;
  target_id: string;
  edge_type: string;
  confidence: number;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  node_type_counts: Record<string, number>;
  edge_type_counts: Record<string, number>;
}

export interface Citation {
  node_id: string;
  label: string;
  quote: string;
}

export interface AgentStep {
  step: number;
  agent_name: string;
  input_summary: string;
  output: Record<string, any>;
  latency_ms: number;
}

export interface QueryResponse {
  query_id: string;
  query_ref: string;
  original_query: string;
  sanitized_query: string | null;
  final_answer: string | null;
  confidence: number | null;
  validation_passed: string | null;
  threat_detected: string | null;
  citations: Citation[];
  context_nodes: Record<string, any>[];
  agent_steps: AgentStep[];
  latency_ms: number;
  created_at: string;
}

export interface QueryListItem {
  id: string;
  query_ref: string;
  query_snippet: string;
  confidence: number | null;
  validation_passed: string | null;
  threat_detected: string | null;
  latency_ms: number | null;
  created_at: string;
}

export interface SecurityEventItem {
  id: string;
  threat_type: string;
  severity: string;
  confidence: number;
  reasoning: string | null;
  blocked: string;
  created_at: string;
}

export interface SecurityDashboard {
  total_events: number;
  blocked_count: number;
  threat_distribution: { threat_type: string; count: number }[];
  recent_events: SecurityEventItem[];
}

export interface DashboardData {
  total_queries: number;
  blocked_queries: number;
  validation_passed: number;
  validation_failed: number;
  avg_confidence: number;
  avg_latency_ms: number;
  graph_node_count: number;
  recent_queries: {
    ref: string;
    snippet: string;
    confidence: number | null;
    validation_passed: string | null;
    threat_detected: string | null;
    created_at: string;
  }[];
}
