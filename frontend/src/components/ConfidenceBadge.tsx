import React from 'react';

interface Props {
  value: number | null;
}

const ConfidenceBadge: React.FC<Props> = ({ value }) => {
  if (value === null || value === undefined) return <span className="text-xs text-gray-400">—</span>;
  const pct = Math.round(value * 100);
  const cls =
    pct >= 75 ? 'bg-green-100 text-green-700' :
    pct >= 50 ? 'bg-yellow-100 text-yellow-700' :
    'bg-red-100 text-red-700';
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-bold ${cls}`}>
      {pct}% confidence
    </span>
  );
};

export default ConfidenceBadge;
