import React, { useEffect, useMemo } from 'react';
import ReactFlow, {
  Background, Controls, MiniMap, Node, Edge, useNodesState, useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { GraphResponse } from '../types';

interface Props {
  data: GraphResponse;
}

const TYPE_COLORS: Record<string, string> = {
  business_entity: '#3b82f6',
  process_step: '#8b5cf6',
  rule: '#ef4444',
  role: '#f59e0b',
  temporal_marker: '#06b6d4',
  source_provenance: '#64748b',
  confidence_score: '#10b981',
  relationship: '#ec4899',
};

const GraphViewer: React.FC<Props> = ({ data }) => {
  const initialNodes: Node[] = useMemo(() => {
    const nodes = data.nodes.slice(0, 80);
    const radius = 420;
    return nodes.map((n, i) => {
      const angle = (i / nodes.length) * 2 * Math.PI;
      return {
        id: n.id,
        data: { label: n.label.slice(0, 30) },
        position: {
          x: 550 + Math.cos(angle) * radius,
          y: 450 + Math.sin(angle) * radius,
        },
        style: {
          background: TYPE_COLORS[n.node_type] || '#6b7280',
          color: 'white',
          border: 'none',
          borderRadius: 8,
          fontSize: 9,
          padding: 6,
          width: 110,
          textAlign: 'center' as const,
        },
      };
    });
  }, [data.nodes]);

  const initialEdges: Edge[] = useMemo(
    () => data.edges.slice(0, 200).map((e) => ({
      id: e.id,
      source: e.source_id,
      target: e.target_id,
      animated: false,
      style: { stroke: '#94a3b8', strokeWidth: 1 },
      label: e.edge_type,
      labelStyle: { fontSize: 8 },
    })),
    [data.edges]
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  return (
    <div style={{ height: 700 }} className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Background color="#e2e8f0" gap={20} />
        <MiniMap />
        <Controls />
      </ReactFlow>
    </div>
  );
};

export default GraphViewer;
