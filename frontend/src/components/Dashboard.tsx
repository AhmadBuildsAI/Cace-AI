import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import StatCard from './StatCard';
import { getDashboard } from '../services/cace';
import { DashboardData } from '../types';

const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboard()
      .then(setData)
      .catch(() => toast.error('Failed to load dashboard'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-center py-12 text-gray-500">Loading...</div>;
  if (!data) return null;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">CACE-AI Dashboard</h1>
          <p className="text-gray-500 text-sm">
            Context-Aware, Continuous-Validation Enterprise AI
          </p>
        </div>
        <Link
          to="/query"
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
        >
          💬 Ask a Question
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Queries" value={data.total_queries} icon="💬" color="indigo" />
        <StatCard title="Blocked" value={data.blocked_queries} icon="🛡️" color="red" />
        <StatCard title="Validation Passed" value={data.validation_passed} icon="✅" color="green" />
        <StatCard title="Validation Failed" value={data.validation_failed} icon="⚠️" color="yellow" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard title="Avg Confidence" value={`${(data.avg_confidence * 100).toFixed(0)}%`} color="blue" icon="🎯" />
        <StatCard title="Avg Latency" value={`${data.avg_latency_ms.toFixed(0)} ms`} color="slate" icon="⏱️" />
        <StatCard title="CKG Nodes" value={data.graph_node_count} color="indigo" icon="🕸️" />
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-3">Recent Queries</h3>
        {data.recent_queries.length === 0 ? (
          <p className="text-sm text-gray-500 py-6 text-center">
            No queries yet. Try asking: "What are the approval rules for large orders?"
          </p>
        ) : (
          <div className="space-y-2">
            {data.recent_queries.map((q) => (
              <div key={q.ref} className="flex items-center justify-between p-3 border border-gray-100 rounded-lg">
                <div className="min-w-0">
                  <p className="text-sm font-medium text-gray-800 truncate">{q.snippet}</p>
                  <p className="text-xs text-gray-500">{q.ref}</p>
                </div>
                <div className="flex gap-2">
                  {q.threat_detected && (
                    <span className="px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs font-bold">
                      🛡️ {q.threat_detected}
                    </span>
                  )}
                  {q.confidence !== null && (
                    <span className="px-2 py-0.5 bg-indigo-100 text-indigo-700 rounded text-xs font-bold">
                      {(q.confidence * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-xl p-5">
        <p className="text-sm text-amber-800">
          ⚖️ <strong>Note:</strong> CACE-AI is a demonstration of a multi-agent context-aware architecture.
          It is not a production system. LLM-based validation may miss subtle contradictions.
        </p>
      </div>
    </div>
  );
};

export default Dashboard;
