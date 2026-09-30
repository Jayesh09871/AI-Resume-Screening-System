import React from 'react';
import { getScoreColor } from '../utils/formatters';
import { ShieldAlert, CheckCircle2, TrendingUp, Sparkles, BookOpen } from 'lucide-react';

export default function ScoreGauge({ breakdown }) {
  if (!breakdown) return null;

  const score = breakdown.overall_score || 0;
  const colorInfo = getScoreColor(score);

  // SVG Gauge calculations
  const radius = 64;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  const metrics = [
    {
      name: 'Required Skills Match',
      weight: '40% weight',
      value: breakdown.required_skill_score || 0,
      icon: CheckCircle2,
      color: 'bg-indigo-500',
    },
    {
      name: 'Experience Relevance',
      weight: '25% weight',
      value: breakdown.experience_relevance || 0,
      icon: TrendingUp,
      color: 'bg-purple-500',
    },
    {
      name: 'Semantic Alignment',
      weight: '20% weight',
      value: breakdown.semantic_similarity || 0,
      icon: Sparkles,
      color: 'bg-blue-500',
    },
    {
      name: 'Preferred Skills Match',
      weight: '15% weight',
      value: breakdown.preferred_skill_score || 0,
      icon: BookOpen,
      color: 'bg-teal-500',
    },
  ];

  return (
    <div className="glass-card rounded-2xl p-6 border border-slate-800">
      <div className="flex flex-col md:flex-row items-center gap-8">
        {/* Circular Gauge */}
        <div className="flex flex-col items-center justify-center shrink-0">
          <div className="relative w-44 h-44 flex items-center justify-center">
            <svg className="w-full h-full -rotate-90 transform" viewBox="0 0 160 160">
              {/* Background circle */}
              <circle
                cx="80"
                cy="80"
                r={radius}
                stroke="#1e293b"
                strokeWidth="12"
                fill="transparent"
              />
              {/* Animated Progress circle */}
              <circle
                cx="80"
                cy="80"
                r={radius}
                stroke={colorInfo.stroke}
                strokeWidth="12"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="transparent"
                className="transition-all duration-1000 ease-out"
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center text-center">
              <span className={`text-4xl font-extrabold tracking-tight ${colorInfo.text}`}>
                {score}
              </span>
              <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold mt-0.5">
                ATS Score
              </span>
            </div>
          </div>
          <span
            className={`mt-2 px-3 py-1 rounded-full text-xs font-semibold ${colorInfo.bg} ${colorInfo.text} border ${colorInfo.border}`}
          >
            {colorInfo.label}
          </span>
        </div>

        {/* Sub-Metric Score Breakdown */}
        <div className="flex-1 w-full space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-semibold text-white">Score Breakdown & Weighting</h3>
            <span className="text-xs text-slate-400">Explainable Algorithmic Formula</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {metrics.map((m) => {
              const Icon = m.icon;
              return (
                <div
                  key={m.name}
                  className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 hover:border-slate-700/80 transition-all"
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="flex items-center space-x-2">
                      <Icon className="w-4 h-4 text-slate-400" />
                      <span className="text-xs font-medium text-slate-300">{m.name}</span>
                    </div>
                    <span className="text-xs font-bold text-white">{m.value}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${m.color} rounded-full transition-all duration-700`}
                      style={{ width: `${m.value}%` }}
                    />
                  </div>
                  <span className="text-[10px] text-slate-500 mt-1 block">{m.weight}</span>
                </div>
              );
            })}
          </div>

          {/* Mandatory ATS disclaimer */}
          <div className="flex items-start space-x-2 p-3 rounded-xl bg-slate-900/40 border border-slate-800/60 text-slate-400 text-xs">
            <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <p className="leading-relaxed text-[11px]">
              <strong className="text-slate-300">Disclaimer:</strong> {breakdown.disclaimer} This analysis scores structural keyword match, depth of experience, and semantic alignment to help you optimize before submitting.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
