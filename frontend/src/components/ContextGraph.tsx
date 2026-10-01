import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import GraphViewer from './GraphViewer';
import StatCard from './StatCard';
import { getGraph } from '../services/cace';
import { GraphResponse } from '../types';

const ContextGraph: React.FC = () => {
  const [data, setData] = useState<GraphResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getGraph()
      .then(setData)
      .catch(() => toast.error('Failed to load graph'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-center py-12 text-gray-500">Loading...</div>;
  if (!data) return null;

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Context Knowledge Graph</h1>
        <p className="text-gray-500 text-sm">
          {data.nodes.length} nodes · {data.edges.length} edges · filtered by your role
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {Object.entries(data.node_type_counts).map(([k, v]) => (
          <StatCard key={k} title={k.replace(/_/g, ' ')} value={v} color="indigo" />
        ))}
      </div>

      <GraphViewer data={data} />

      <div className="flex flex-wrap gap-4 text-xs">
        {[
          ['business_entity', '#3b82f6'],
          ['process_step', '#8b5cf6'],
          ['rule', '#ef4444'],
          ['role', '#f59e0b'],
        ].map(([label, color]) => (
          <span key={label} className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full" style={{ background: color }} />
            {label.replace(/_/g, ' ')}
          </span>
        ))}
      </div>
    </div>
  );
};

export default ContextGraph;
