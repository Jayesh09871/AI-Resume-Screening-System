import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  FileText,
  Upload,
  BarChart3,
  Edit3,
  History,
  Sparkles,
  BookOpen,
  Menu,
  X,
} from 'lucide-react';
import { api } from '../services/api';

export default function Navbar() {
  const location = useLocation();
  const [health, setHealth] = useState({ status: 'checking', groq: false });
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    api.checkHealth()
      .then((data) => {
        setHealth({ status: 'online', groq: data.groq_configured });
      })
      .catch(() => {
        setHealth({ status: 'offline', groq: false });
      });
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  const navLinks = [
    { name: 'Dashboard', path: '/dashboard', icon: BarChart3 },
    { name: 'Upload', path: '/upload', icon: Upload },
    { name: 'Analysis', path: '/analysis', icon: Sparkles },
    { name: 'Editor', path: '/editor', icon: Edit3 },
    { name: 'Interview Prep', path: '/interview-prep', icon: BookOpen },
    { name: 'History', path: '/history', icon: History },
  ];

  return (
    <header className="sticky top-0 z-50 glass-card border-b border-slate-800/80 bg-slate-950/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-2 sm:gap-4">
        {/* Brand */}
        <Link to="/" className="flex items-center space-x-2.5 shrink-0 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-500 flex items-center justify-center shadow-md shadow-indigo-500/20 group-hover:scale-105 transition-transform duration-200">
            <FileText className="w-4 h-4 text-white" />
          </div>
          <div className="flex flex-col">
            <div className="flex items-center space-x-1.5 leading-none">
              <span className="font-bold text-base sm:text-lg text-white tracking-tight">AI Resume</span>
              <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                PRO
              </span>
            </div>
            <p className="hidden xl:block text-[11px] text-slate-400 mt-0.5 leading-none">Screening & ATS Builder</p>
          </div>
        </Link>

        {/* Desktop Navigation links */}
        <nav className="hidden lg:flex items-center space-x-1 bg-slate-900/60 p-1 rounded-xl border border-slate-800/60 shrink-0">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = location.pathname === link.path;

            return (
              <Link
                key={link.path}
                to={link.path}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-150 whitespace-nowrap ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-xs shadow-indigo-600/30'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{link.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Right Section: Status indicator + CTA + Mobile Toggle */}
        <div className="flex items-center space-x-2 sm:space-x-3 shrink-0">
          {/* Health indicator */}
          <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border bg-slate-900/80 border-slate-800 shrink-0 whitespace-nowrap">
            {health.status === 'online' ? (
              <>
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse shrink-0"></span>
                <span className="text-slate-300">Active</span>
                {health.groq && (
                  <span className="text-[9px] px-1.5 py-0.2 rounded font-semibold bg-purple-500/20 text-purple-300 border border-purple-500/30 ml-1">
                    Groq
                  </span>
                )}
              </>
            ) : health.status === 'checking' ? (
              <>
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse shrink-0"></span>
                <span className="text-slate-400">Connecting</span>
              </>
            ) : (
              <>
                <span className="w-1.5 h-1.5 rounded-full bg-rose-500 shrink-0"></span>
                <span className="text-rose-400">Offline</span>
              </>
            )}
          </div>

          {/* Quick CTA */}
          <Link
            to="/upload"
            className="flex items-center space-x-1.5 px-3 sm:px-3.5 py-1.5 sm:py-2 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white text-xs sm:text-sm font-semibold shadow-md shadow-indigo-500/25 transition-all duration-200 shrink-0 whitespace-nowrap"
          >
            <Upload className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Scan Resume</span>
            <span className="sm:hidden">Scan</span>
          </Link>

          {/* Mobile Menu Hamburger Button */}
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
            aria-label="Toggle Navigation Menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Dropdown Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t border-slate-800 bg-slate-950/95 backdrop-blur-xl px-4 py-4 space-y-3 animate-in fade-in slide-in-from-top-2 duration-150">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = location.pathname === link.path;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center space-x-2.5 px-3.5 py-2.5 rounded-xl text-xs sm:text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-indigo-600 text-white font-semibold shadow-xs'
                      : 'text-slate-300 hover:text-white hover:bg-slate-900 border border-slate-800/60'
                  }`}
                >
                  <Icon className="w-4 h-4 shrink-0 text-indigo-400" />
                  <span>{link.name}</span>
                </Link>
              );
            })}
          </div>

          {/* Mobile status row */}
          <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <span className="flex items-center space-x-1.5">
              <span className={`w-2 h-2 rounded-full ${health.status === 'online' ? 'bg-emerald-400' : 'bg-amber-400'}`}></span>
              <span>Backend API {health.status}</span>
            </span>
            {health.groq && (
              <span className="text-[10px] px-2 py-0.5 rounded font-semibold bg-purple-500/20 text-purple-300 border border-purple-500/30">
                Groq LLM Active
              </span>
            )}
          </div>
        </div>
      )}
    </header>
  );
}