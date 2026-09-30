import React from 'react';
import { FileText, Cpu, ShieldCheck, Heart } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t border-slate-900 bg-slate-950/60 py-8 px-4 text-xs text-slate-400 mt-auto">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 rounded-lg bg-indigo-600 flex items-center justify-center text-white">
            <FileText className="w-3.5 h-3.5" />
          </div>
          <span className="font-semibold text-slate-200">AI-Resume-Screening-System</span>
          <span className="text-slate-500">|</span>
          <span>ATS Screening & PDF Generation</span>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-6 text-slate-400">
          <span className="flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-indigo-400" />
            Groq LLaMA 3.3 & all-MiniLM-L6-v2
          </span>
          <span className="flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            Zero Fake Metrics Guarantee
          </span>
        </div>

        <div className="text-slate-500 text-center md:text-right">
          Explainable AI-Powered Career Toolkit &copy; {new Date().getFullYear()}
        </div>
      </div>
    </footer>
  );
}
