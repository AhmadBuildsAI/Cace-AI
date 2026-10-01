import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import toast from 'react-hot-toast';
import StatCard from './StatCard';
import { getSecurityDashboard } from '../services/cace';
import { SecurityDashboard } from '../types';

const SEV_COLORS: Record<string, string> = {
  HIGH: 'bg-red-100 text-red-700',
  MEDIUM: 'bg-yellow-100 text-yellow-700',
  LOW: 'bg-blue-100 text-blue-700',
};

const SecurityCenter: React.FC = () => {
  const [data, setData] = useState<SecurityDashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSecurityDashboard()
      .then(setData)
      .catch(() => toast.error('Failed to load security dashboard'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-center py-12 text-gray-500">Loading...</div>;
  if (!data) return null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Security Center</h1>
        <p className="text-gray-500 text-sm">
          Threat detection events from the Security Agent
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard title="Total Events" value={data.total_events} icon="🛡️" color="red" />
        <StatCard title="Blocked" value={data.blocked_count} icon="⛔" color="slate" />
        <StatCard title="Threat Types" value={data.threat_distribution.length} icon="🎯" color="yellow" />
      </div>

      {data.threat_distribution.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="font-semibold text-gray-800 mb-3">Threat Distribution</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={data.threat_distribution}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="threat_type" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#dc2626" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-3">Recent Events</h3>
        {data.recent_events.length === 0 ? (
          <p className="text-sm text-green-600 py-6 text-center">
            ✅ No security events. All queries were clean.
          </p>
        ) : (
          <div className="space-y-3">
            {data.recent_events.map((e) => (
              <div key={e.id} className="border border-gray-100 rounded-lg p-4">
                <div className="flex justify-between items-start mb-1">
                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-bold px-2 py-0.5 rounded ${SEV_COLORS[e.severity] || SEV_COLORS.LOW}`}>
                      {e.severity}
                    </span>
                    <span className="text-sm font-medium text-gray-800 font-mono">{e.threat_type}</span>
                    <span className="text-xs text-gray-500">confidence {(e.confidence * 100).toFixed(0)}%</span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(e.created_at).toLocaleString()}
                  </span>
                </div>
                {e.reasoning && <p className="text-sm text-gray-700">{e.reasoning}</p>}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-xl p-5">
        <p className="text-sm text-blue-800">
          <strong>What's detected:</strong> prompt injection, context bombing, data exfiltration attempts, privilege escalation.
          The Security Agent combines deterministic regex patterns with LLM-based semantic detection.
        </p>
      </div>
    </div>
  );
};

export default SecurityCenter;
