import React, { useState } from 'react';
import { 
  Lightbulb, 
  ChevronDown, 
  ChevronUp, 
  ArrowRight, 
  CheckCircle, 
  FileCheck, 
  Target,
  Copy,
  Check
} from 'lucide-react';

export default function RecommendationCard({ suggestion, onApply }) {
  const [expanded, setExpanded] = useState(true);
  const [copied, setCopied] = useState(false);

  const categoryStyles = {
    keyword: {
      label: 'Keyword Alignment',
      badge: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    },
    summary: {
      label: 'Summary Pitch',
      badge: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    },
    experience_bullet: {
      label: 'Bullet Point Strength',
      badge: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
    },
    project: {
      label: 'Project Relevance',
      badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    },
    skill_priority: {
      label: 'Skill Prioritization',
      badge: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    },
  };

  const style = categoryStyles[suggestion.category] || {
    label: 'Recommendation',
    badge: 'bg-slate-800 text-slate-300 border-slate-700',
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(suggestion.recommendation);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="glass-card rounded-xl border border-slate-800/90 overflow-hidden hover:border-slate-700 transition-all">
      {/* Header */}
      <div 
        onClick={() => setExpanded(!expanded)}
        className="p-4 flex items-start justify-between cursor-pointer select-none bg-slate-900/40 hover:bg-slate-900/60 transition-colors"
      >
        <div className="flex items-start space-x-3 pr-4">
          <div className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 shrink-0 mt-0.5">
            <Lightbulb className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2 mb-1">
              <span className={`text-[10px] font-semibold px-2 py-0.5 rounded border uppercase tracking-wider ${style.badge}`}>
                {style.label}
              </span>
            </div>
            <h4 className="text-sm font-semibold text-white leading-snug">
              {suggestion.recommendation}
            </h4>
          </div>
        </div>

        <button className="text-slate-400 hover:text-white p-1">
          {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      {/* Expanded Content with Evidence */}
      {expanded && (
        <div className="p-4 border-t border-slate-800/60 bg-slate-950/40 space-y-3 text-xs">
          {/* Reason */}
          <div>
            <span className="font-semibold text-slate-400 block mb-1">Why this matters:</span>
            <p className="text-slate-300 leading-relaxed bg-slate-900/40 p-2.5 rounded-lg border border-slate-800/60">
              {suggestion.reason}
            </p>
          </div>

          {/* Evidence Grid: Resume Evidence vs JD Requirement */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
            {/* Resume Evidence */}
            <div className="p-2.5 rounded-lg bg-slate-900/70 border border-slate-800">
              <div className="flex items-center space-x-1.5 text-indigo-400 font-semibold mb-1">
                <FileCheck className="w-3.5 h-3.5" />
                <span>Current Resume Evidence</span>
              </div>
              <p className="text-slate-300 italic text-[11px] leading-relaxed">
                "{suggestion.resume_evidence}"
              </p>
            </div>

            {/* JD Requirement */}
            <div className="p-2.5 rounded-lg bg-slate-900/70 border border-slate-800">
              <div className="flex items-center space-x-1.5 text-purple-400 font-semibold mb-1">
                <Target className="w-3.5 h-3.5" />
                <span>Target JD Requirement</span>
              </div>
              <p className="text-slate-300 italic text-[11px] leading-relaxed">
                "{suggestion.related_jd_requirement}"
              </p>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center justify-end space-x-2 pt-2">
            <button
              onClick={handleCopy}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors text-xs font-medium"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy Suggestion'}</span>
            </button>
            {onApply && (
              <button
                onClick={() => onApply(suggestion)}
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition-colors text-xs font-semibold shadow-xs"
              >
                <span>Edit in Resume</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
