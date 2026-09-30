import React from 'react';
import { Check, X, Plus, Sparkles } from 'lucide-react';

export default function SkillBadge({ skill, status = 'matched', onAdd }) {
  if (status === 'matched') {
    return (
      <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-lg text-xs font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 shadow-xs">
        <Check className="w-3.5 h-3.5 text-emerald-400" />
        <span>{skill}</span>
      </span>
    );
  }

  if (status === 'missing_required') {
    return (
      <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-lg text-xs font-semibold bg-rose-500/10 text-rose-300 border border-rose-500/20 shadow-xs">
        <X className="w-3.5 h-3.5 text-rose-400" />
        <span>{skill}</span>
        {onAdd && (
          <button
            onClick={() => onAdd(skill)}
            title="Add to resume"
            className="hover:bg-rose-500/20 rounded p-0.5 transition-colors"
          >
            <Plus className="w-3 h-3 text-rose-400" />
          </button>
        )}
      </span>
    );
  }

  if (status === 'missing_preferred') {
    return (
      <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-lg text-xs font-semibold bg-amber-500/10 text-amber-300 border border-amber-500/20 shadow-xs">
        <Plus className="w-3.5 h-3.5 text-amber-400" />
        <span>{skill}</span>
        {onAdd && (
          <button
            onClick={() => onAdd(skill)}
            title="Add to resume"
            className="hover:bg-amber-500/20 rounded p-0.5 transition-colors"
          >
            <Plus className="w-3 h-3 text-amber-400" />
          </button>
        )}
      </span>
    );
  }

  // Neutral / default
  return (
    <span className="inline-flex items-center space-x-1 px-3 py-1 rounded-lg text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">
      <span>{skill}</span>
    </span>
  );
}
