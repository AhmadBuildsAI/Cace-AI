import React from 'react';
import { Citation } from '../types';

interface Props {
  citation: Citation;
}

const CitationCard: React.FC<Props> = ({ citation }) => (
  <div className="border-l-4 border-indigo-400 bg-indigo-50 rounded-r-lg p-3">
    <p className="text-sm font-medium text-indigo-900">{citation.label}</p>
    {citation.quote && (
      <p className="text-xs text-indigo-700 italic mt-1">"{citation.quote}"</p>
    )}
    <p className="text-xs text-gray-500 mt-1 font-mono">node: {citation.node_id.slice(0, 12)}...</p>
  </div>
);

export default CitationCard;
