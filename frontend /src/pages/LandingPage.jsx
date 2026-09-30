import React from 'react';
import { Link } from 'react-router-dom';
import { 
  FileText, 
  Sparkles, 
  Upload, 
  CheckCircle2, 
  ShieldCheck, 
  TrendingUp, 
  Code2, 
  ArrowRight,
  Cpu,
  Layers,
  Download
} from 'lucide-react';

export default function LandingPage() {
  const steps = [
    { num: '01', title: 'Upload & Parse', desc: 'PyMuPDF & python-docx extract machine-readable text page-by-page' },
    { num: '02', title: 'Hybrid Structuring', desc: 'Deterministic regex + LLM extraction with strict Pydantic validation' },
    { num: '03', title: 'Dual-Engine Match', desc: 'Exact alias dictionary + sentence-transformers semantic cosine similarity' },
    { num: '04', title: 'Evidence-Based Suggestions', desc: 'Zero-hallucination AI recommendations with dual evidence verification' },
    { num: '05', title: 'Interactive Editor & PDF', desc: 'User-controlled editing and ATS-compliant ReportLab PDF generation' },
  ];

  const features = [
    {
      icon: TrendingUp,
      title: 'Explainable ATS Compatibility Score',
      desc: 'No black-box mystery numbers. Get a calculated 0-100 score broken down by required skills (40%), experience relevance (25%), semantic fit (20%), and preferred skills (15%).',
    },
    {
      icon: Cpu,
      title: 'Semantic Alignment via Embeddings',
      desc: 'Powered by sentence-transformers/all-MiniLM-L6-v2. Matches conceptual achievements like "FastAPI microservices" to "REST API architecture".',
    },
    {
      icon: ShieldCheck,
      title: 'Anti-Hallucination AI Guarantee',
      desc: 'Strictly prohibited from fabricating candidate skills, dates, metrics, or credentials. Prompts candidates for real quantifiable impact instead.',
    },
    {
      icon: Download,
      title: 'Machine-Readable PDF Generator',
      desc: 'Exports clean single-column ATS resumes using ReportLab with native text vectors, clickable links, and standardized typography.',
    },
  ];

  return (
    <div className="space-y-24 py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      {/* Hero Section */}
      <section className="text-center space-y-8 pt-8">
        <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Next-Generation Career Engineering & ATS Optimization</span>
        </div>

        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold text-white tracking-tight leading-[1.1] max-w-4xl mx-auto">
          Screen Resumes with{' '}
          <span className="gradient-text">Explainable AI & Precision NLP</span>
        </h1>

        <p className="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
          Upload your resume, paste any target Job Description, and receive an algorithmic ATS score, verified skill gap analysis, and hallucination-free suggestions.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <Link
            to="/upload"
            className="w-full sm:w-auto flex items-center justify-center space-x-2 px-8 py-3.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-semibold shadow-lg shadow-indigo-500/30 hover:shadow-indigo-500/50 transition-all text-sm group"
          >
            <Upload className="w-4 h-4 group-hover:-translate-y-0.5 transition-transform" />
            <span>Upload Resume Now</span>
            <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
          </Link>

          <Link
            to="/dashboard"
            className="w-full sm:w-auto flex items-center justify-center space-x-2 px-8 py-3.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-slate-200 border border-slate-700/80 font-semibold transition-all text-sm"
          >
            <span>Open Dashboard</span>
          </Link>
        </div>
      </section>

      {/* Visual Pipeline Section */}
      <section className="space-y-8">
        <div className="text-center space-y-2">
          <h2 className="text-2xl sm:text-3xl font-bold text-white">The Engineering Pipeline</h2>
          <p className="text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
            A deterministic, schema-validated hybrid architecture designed for enterprise reliability
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {steps.map((s, idx) => (
            <div
              key={s.num}
              className="glass-card glass-card-hover p-5 rounded-2xl border border-slate-800 flex flex-col justify-between"
            >
              <div>
                <span className="text-2xl font-black text-indigo-400/40 block mb-2">{s.num}</span>
                <h3 className="text-sm font-bold text-white mb-2">{s.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{s.desc}</p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
                <span>Phase {idx + 1}</span>
                <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Feature Highlights Grid */}
      <section className="space-y-8">
        <div className="text-center space-y-2">
          <h2 className="text-2xl sm:text-3xl font-bold text-white">Core Architectural Innovations</h2>
          <p className="text-xs sm:text-sm text-slate-400">Built to solve real recruiting flaws</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feat) => {
            const Icon = feat.icon;
            return (
              <div
                key={feat.title}
                className="glass-card glass-card-hover p-6 rounded-2xl border border-slate-800 flex items-start space-x-4"
              >
                <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 shrink-0">
                  <Icon className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white mb-2">{feat.title}</h3>
                  <p className="text-xs text-slate-300 leading-relaxed">{feat.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
