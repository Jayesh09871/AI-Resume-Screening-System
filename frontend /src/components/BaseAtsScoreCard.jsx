import React from 'react';
import { useNavigate } from 'react-router-dom';
import { getScoreColor } from '../utils/formatters';
import { 
  FileCheck, 
  Layers, 
  UserCheck, 
  Zap, 
  TrendingUp, 
  Award, 
  Edit3, 
  Download, 
  CheckCircle2, 
  ArrowUpRight,
  Info
} from 'lucide-react';

export default function BaseAtsScoreCard({ 
  baseScore, 
  onDownloadPdf, 
  isExportingPdf, 
  selectedTemplate, 
  setSelectedTemplate 
}) {
  const navigate = useNavigate();

  if (!baseScore) return null;

  const score = baseScore.overall_score || 0;
  const colorInfo = getScoreColor(score);

  // SVG Gauge calculations
  const radius = 64;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  const pillars = [
    {
      name: 'ATS Section Structure',
      score: baseScore.section_score,
      max: 25,
      icon: Layers,
      color: 'bg-indigo-500',
    },
    {
      name: 'Contact & Online Presence',
      score: baseScore.contact_score,
      max: 15,
      icon: UserCheck,
      color: 'bg-emerald-500',
    },
    {
      name: 'Action Verbs & Voice',
      score: baseScore.linguistic_score,
      max: 25,
      icon: Zap,
      color: 'bg-amber-500',
    },
    {
      name: 'Quantified Metrics & Impact',
      score: baseScore.quantified_impact_score,
      max: 20,
      icon: TrendingUp,
      color: 'bg-blue-500',
    },
    {
      name: 'Skills Breadth & Indexing',
      score: baseScore.skills_breadth_score,
      max: 15,
      icon: Award,
      color: 'bg-purple-500',
    },
  ];

  return (
    <div className="glass-card rounded-2xl p-6 sm:p-8 border border-slate-800 space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
        <div className="space-y-1">
          <div className="inline-flex items-center space-x-2 px-2.5 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[11px] font-semibold">
            <FileCheck className="w-3.5 h-3.5" />
            <span>Standalone Resume Evaluation</span>
          </div>
          <h2 className="text-xl font-black text-white tracking-tight">
            Resume Baseline ATS Quality Score
          </h2>
          <p className="text-xs text-slate-400 max-w-2xl">
            Evaluates your resume's structure, section completeness, action verbs, and ATS parseability <strong className="text-slate-200">without requiring any Job Description</strong>.
          </p>
        </div>

        {/* Quick Actions */}
        {onDownloadPdf && (
          <div className="flex flex-wrap items-center gap-2">
            {setSelectedTemplate && (
              <select
                value={selectedTemplate}
                onChange={(e) => setSelectedTemplate(e.target.value)}
                className="bg-slate-900 border border-slate-700 text-xs text-indigo-300 font-semibold rounded-xl px-3 py-2 focus:outline-hidden"
              >
                <option value="classic_ats">Classic ATS</option>
                <option value="modern_tech">Modern Tech</option>
                <option value="executive">Executive</option>
              </select>
            )}

            <button
              onClick={() => navigate('/editor')}
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-xs transition-colors"
            >
              <Edit3 className="w-3.5 h-3.5" />
              <span>Edit Resume</span>
            </button>

            <button
              onClick={onDownloadPdf}
              disabled={isExportingPdf}
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors disabled:opacity-50"
            >
              <Download className="w-3.5 h-3.5" />
              <span>{isExportingPdf ? 'Exporting...' : 'Export PDF'}</span>
            </button>
          </div>
        )}
      </div>

      {/* Main Gauge and Pillars */}
      <div className="flex flex-col lg:flex-row items-center gap-8">
        {/* Circular Gauge */}
        <div className="flex flex-col items-center justify-center shrink-0">
          <div className="relative w-44 h-44 flex items-center justify-center">
            <svg className="w-full h-full -rotate-90 transform" viewBox="0 0 160 160">
              <circle
                cx="80"
                cy="80"
                r={radius}
                stroke="#1e293b"
                strokeWidth="12"
                fill="transparent"
              />
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
              <span className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold mt-0.5">
                Resume ATS
              </span>
            </div>
          </div>
          <span
            className={`mt-2 px-3 py-1 rounded-full text-xs font-semibold ${colorInfo.bg} ${colorInfo.text} border ${colorInfo.border}`}
          >
            {colorInfo.label}
          </span>
        </div>

        {/* 5 Structural Pillars */}
        <div className="flex-1 w-full space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-semibold text-slate-300">Resume Health Pillars</span>
            <span>Based on ATS Parsing & Formatting Standards</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {pillars.map((p) => {
              const Icon = p.icon;
              const percent = Math.min(100, Math.round((p.score / p.max) * 100));
              return (
                <div
                  key={p.name}
                  className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-1.5"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Icon className="w-3.5 h-3.5 text-slate-400" />
                      <span className="text-xs font-medium text-slate-300">{p.name}</span>
                    </div>
                    <span className="text-xs font-bold text-white">
                      {p.score} <span className="text-slate-500 font-normal">/ {p.max}</span>
                    </span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${p.color} rounded-full transition-all duration-700`}
                      style={{ width: `${percent}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Strengths & Improvements */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
        {/* Strengths */}
        {baseScore.strengths && baseScore.strengths.length > 0 && (
          <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/20 space-y-2">
            <div className="flex items-center space-x-2 text-emerald-400 text-xs font-bold">
              <CheckCircle2 className="w-4 h-4" />
              <span>Resume Strengths Detected</span>
            </div>
            <ul className="space-y-1 text-xs text-slate-300">
              {baseScore.strengths.map((item, idx) => (
                <li key={idx} className="flex items-start space-x-2">
                  <span className="text-emerald-400 shrink-0">&bull;</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Improvements */}
        {baseScore.improvements && baseScore.improvements.length > 0 && (
          <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/20 space-y-2">
            <div className="flex items-center space-x-2 text-amber-400 text-xs font-bold">
              <ArrowUpRight className="w-4 h-4" />
              <span>Recommended Resume Fixes</span>
            </div>
            <ul className="space-y-1 text-xs text-slate-300">
              {baseScore.improvements.map((item, idx) => (
                <li key={idx} className="flex items-start space-x-2">
                  <span className="text-amber-400 shrink-0">&bull;</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Disclaimer */}
      <div className="flex items-center space-x-2 text-[11px] text-slate-500 pt-1">
        <Info className="w-3.5 h-3.5 shrink-0" />
        <span>
          This score measures baseline ATS compliance. To test your resume for a specific role or company, use the Job Description Matcher below.
        </span>
      </div>
    </div>
  );
}
