import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import ConfidenceBadge from './ConfidenceBadge';
import { listQueries } from '../services/cace';
import { QueryListItem } from '../types';

const AgentTraces: React.FC = () => {
  const [queries, setQueries] = useState<QueryListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    listQueries()
      .then(setQueries)
      .catch(() => toast.error('Failed to load traces'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Agent Traces</h1>
        <p className="text-gray-500 text-sm">{queries.length} query runs</p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th className="px-4 py-3 text-left">Ref</th>
              <th className="px-4 py-3 text-left">Query</th>
              <th className="px-4 py-3 text-left">Confidence</th>
              <th className="px-4 py-3 text-left">Validation</th>
              <th className="px-4 py-3 text-left">Threat</th>
              <th className="px-4 py-3 text-left">Latency</th>
              <th className="px-4 py-3 text-left">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading ? (
              <tr><td colSpan={7} className="px-4 py-8 text-center text-gray-400">Loading...</td></tr>
            ) : queries.length === 0 ? (
              <tr><td colSpan={7} className="px-4 py-8 text-center text-gray-400">No queries yet</td></tr>
            ) : (
              queries.map((q) => (
                <tr key={q.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-mono text-xs">{q.query_ref}</td>
                  <td className="px-4 py-3 text-gray-700 truncate max-w-md">{q.query_snippet}</td>
                  <td className="px-4 py-3"><ConfidenceBadge value={q.confidence} /></td>
                  <td className="px-4 py-3 text-xs">
                    <span className={`px-2 py-0.5 rounded ${
                      q.validation_passed === 'pass' ? 'bg-green-100 text-green-700' :
                      q.validation_passed === 'fail' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-red-100 text-red-700'
                    }`}>
                      {q.validation_passed}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs">
                    {q.threat_detected ? (
                      <span className="px-2 py-0.5 rounded bg-red-100 text-red-700 font-bold">
                        🛡️ {q.threat_detected}
                      </span>
                    ) : '—'}
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-500">
                    {q.latency_ms ? `${q.latency_ms.toFixed(0)} ms` : '—'}
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => navigate(`/query?id=${q.id}`)}
                      className="text-indigo-600 hover:underline text-sm"
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AgentTraces;
