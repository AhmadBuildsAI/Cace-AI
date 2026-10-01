import React from 'react';
import { AgentStep } from '../types';

interface Props {
  step: AgentStep;
}

const AGENT_COLORS: Record<string, string> = {
  security: 'bg-red-50 border-red-200',
  retrieval: 'bg-blue-50 border-blue-200',
  reasoning: 'bg-indigo-50 border-indigo-200',
  validation: 'bg-green-50 border-green-200',
};

const AGENT_ICONS: Record<string, string> = {
  security: '🛡️',
  retrieval: '🔍',
  reasoning: '🧠',
  validation: '✅',
};

const AgentStepCard: React.FC<Props> = ({ step }) => (
  <div className={`border rounded-lg p-4 ${AGENT_COLORS[step.agent_name] || 'bg-gray-50 border-gray-200'}`}>
    <div className="flex justify-between items-start mb-2">
      <div className="flex items-center gap-2">
        <span className="text-xl">{AGENT_ICONS[step.agent_name] || '⚙️'}</span>
        <span className="font-semibold text-sm uppercase">{step.agent_name} agent</span>
      </div>
      <span className="text-xs text-gray-500">{step.latency_ms.toFixed(0)} ms</span>
    </div>
    <p className="text-xs text-gray-600 mb-2">Input: {step.input_summary}</p>
    <pre className="text-xs bg-white/60 rounded p-2 overflow-x-auto max-h-40">
      {JSON.stringify(step.output, null, 2)}
    </pre>
  </div>
);

export default AgentStepCard;
