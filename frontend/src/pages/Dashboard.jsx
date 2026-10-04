import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useResume } from '../hooks/useResume';
import { api } from '../services/api';
import { useToast } from '../components/Toast';
import ScoreGauge from '../components/ScoreGauge';
import SkillBadge from '../components/SkillBadge';
import { 
  FileText, 
  Upload, 
  Sparkles, 
  CheckCircle2, 
  XCircle, 
  TrendingUp, 
  History, 
  ArrowRight,
  Edit3,
  Clock,
  ExternalLink,
  Wand2,
  Trash2
} from 'lucide-react';
import { formatDate } from '../utils/formatters';

export default function Dashboard() {
  const navigate = useNavigate();
  const { 
    currentResume, 
    currentAnalysis, 
    setCurrentResume, 
    setCurrentAnalysis, 
    setCurrentJd,
    baseAtsScore,
    clearResume,
    clearIfActive
  } = useResume();
  const { addToast } = useToast();
  const [historyItems, setHistoryItems] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoadingHistory(true);
    try {
      const data = await api.getHistory();
      const items = Array.isArray(data) ? data : [];
      setHistoryItems(items);

      // Verify active resume still exists on backend if it has an ID
      if (currentResume?.id) {
        try {
          await api.getResume(currentResume.id);
        } catch (resumeErr) {
          if (resumeErr.response?.status === 404 || resumeErr.status === 404) {
            console.warn('Active resume was deleted on server, clearing dashboard state.');
            clearResume();
            return;
          }
        }
      }

      // If active analysis was deleted from history, clear it
      if (currentAnalysis) {
        const activeAnalysisId = currentAnalysis.id || currentAnalysis.analysis_id;
        if (activeAnalysisId && !items.some((item) => item.id === activeAnalysisId)) {
          setCurrentAnalysis(null);
        }
      }
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleDeleteHistory = async (historyId, resumeId, e) => {
    e.stopPropagation();
    try {
      await api.deleteHistoryItem(historyId);
      setHistoryItems((prev) => prev.filter((item) => item.id !== historyId));
      clearIfActive(historyId, resumeId);
      if ((Array.isArray(historyItems) ? historyItems.length : 0) <= 1) {
        clearResume();
      }
      addToast('Screening record and resume removed.', 'info');
    } catch (err) {
      addToast(`Delete failed: ${err.message}`, 'error');
    }
  };

  const loadPastAnalysis = async (historyItem) => {
    try {
      const fullAnalysis = await api.getAnalysis(historyItem.id);
      setCurrentAnalysis(fullAnalysis);

      if (historyItem.resume_id) {
        const fullResume = await api.getResume(historyItem.resume_id);
        setCurrentResume({
          id: fullResume.id,
          title: fullResume.title,
          data: fullResume.structured_data,
        });
      }
      addToast(`Loaded analysis report #${historyItem.id}!`, 'info');
      navigate('/analysis');
    } catch (err) {
      addToast(`Failed to load analysis: ${err.message}`, 'error');
    }
  };

  const matchData = currentAnalysis?.match_data;
  const breakdown = matchData?.breakdown;

  return (
    <div className="max-w-7xl mx-auto py-10 px-4 space-y-10">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Recruiting Intelligence Dashboard</h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Real-time ATS screening metrics, skill gaps, and evidence-grounded resume optimization
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <Link
            to="/upload"
            className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700/80 hover:bg-slate-800 text-slate-200 text-xs font-semibold transition-colors"
          >
            <Upload className="w-4 h-4 text-indigo-400" />
            <span>Upload New Resume</span>
          </Link>

          <Link
            to="/analysis"
            className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white text-xs font-bold shadow-lg shadow-indigo-500/25 transition-all"
          >
            <Sparkles className="w-4 h-4" />
            <span>Target New JD</span>
          </Link>
        </div>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>ATS Compatibility</span>
            <TrendingUp className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-black text-white">
            {breakdown ? `${breakdown.overall_score}%` : '--'}
          </div>
          <p className="text-[11px] text-slate-500">
            {breakdown ? 'Target JD Match Score' : 'Pending Job Description'}
          </p>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Matched Required Skills</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400">
            {matchData ? matchData.matched_required_skills.length : '--'}
          </div>
          <p className="text-[11px] text-slate-500">
            {matchData ? 'Core competencies verified' : 'Pending Job Description'}
          </p>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Missing Required Skills</span>
            <XCircle className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-black text-rose-400">
            {matchData ? matchData.missing_required_skills.length : '--'}
          </div>
          <p className="text-[11px] text-slate-500">
            {matchData ? 'Immediate tailoring gaps' : 'Pending Job Description'}
          </p>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>AI Suggestions</span>
            <Sparkles className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-black text-purple-400">
            {currentAnalysis?.suggestions?.length || (breakdown ? 0 : '--')}
          </div>
          <p className="text-[11px] text-slate-500">
            {currentAnalysis ? 'Tailoring tips for target role' : 'Pending Job Description'}
          </p>
        </div>
      </div>

      {/* Main Analysis Overview or Empty State */}
      {breakdown ? (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rounded-full bg-purple-500"></span>
              <span>Target Role JD Compatibility Results</span>
            </h3>
            <Link to="/analysis" className="text-xs text-indigo-400 hover:underline flex items-center space-x-1">
              <span>View Full Report</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <ScoreGauge breakdown={breakdown} />

          {/* Quick Skills View */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white uppercase tracking-wider">
                  Top Matched Skills
                </span>
                <Link to="/analysis" className="text-xs text-indigo-400 hover:underline flex items-center space-x-1">
                  <span>View All</span>
                  <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {(Array.isArray(matchData.matched_required_skills) ? matchData.matched_required_skills : []).slice(0, 8).map((s) => (
                  <SkillBadge key={s} skill={s} status="matched" />
                ))}
              </div>
            </div>

            <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white uppercase tracking-wider">
                  Key Skills to Add
                </span>
                <Link to="/editor" className="text-xs text-indigo-400 hover:underline flex items-center space-x-1">
                  <span>Open Editor</span>
                  <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {(Array.isArray(matchData.missing_required_skills) ? matchData.missing_required_skills : []).slice(0, 8).map((s) => (
                  <SkillBadge key={s} skill={s} status="missing_required" />
                ))}
              </div>
            </div>
          </div>
        </div>
      ) : currentResume ? (
        <div className="glass-card rounded-2xl p-8 border border-slate-800 text-center space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mx-auto">
            <Sparkles className="w-6 h-6" />
          </div>
          <div className="max-w-md mx-auto space-y-1.5">
            <h3 className="text-base font-bold text-white">
              Resume Ready: {currentResume.data?.name || currentResume.title || 'Loaded Resume'}
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Step 2 Required: Enter your target Job Description to generate ATS score, match percentage, skill gap breakdown, and interview prep questions.
            </p>
          </div>
          <Link
            to="/analysis"
            className="inline-flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white text-xs font-bold shadow-lg shadow-indigo-500/30 transition-all"
          >
            <Sparkles className="w-4 h-4" />
            <span>Enter Job Description & Analyze &rarr;</span>
          </Link>
        </div>
      ) : (
        <div className="glass-card rounded-2xl p-10 border border-slate-800 text-center space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mx-auto">
            <Upload className="w-7 h-7" />
          </div>
          <div className="max-w-md mx-auto space-y-1">
            <h3 className="text-base font-bold text-white">Step 1: Upload Resume</h3>
            <p className="text-xs text-slate-400">
              Upload your resume in PDF or DOCX format, then enter a job description to screen your profile.
            </p>
          </div>
          <Link
            to="/upload"
            className="inline-flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition-all"
          >
            <Upload className="w-4 h-4" />
            <span>Upload Resume Now</span>
          </Link>
        </div>
      )}

      {/* Recent Analysis History Table */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <div className="flex items-center space-x-2">
            <History className="w-4 h-4 text-indigo-400" />
            <h3 className="text-sm font-bold text-white">Recent Screening History</h3>
          </div>
          <Link to="/history" className="text-xs text-indigo-400 hover:underline flex items-center space-x-1">
            <span>Full History</span>
            <ArrowRight className="w-3 h-3" />
          </Link>
        </div>

        {Array.isArray(historyItems) && historyItems.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-slate-400 border-b border-slate-800">
                  <th className="pb-3 font-semibold">Resume Title</th>
                  <th className="pb-3 font-semibold">Target Job Role</th>
                  <th className="pb-3 font-semibold">ATS Score</th>
                  <th className="pb-3 font-semibold">Matched</th>
                  <th className="pb-3 font-semibold">Date</th>
                  <th className="pb-3 font-semibold text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {(Array.isArray(historyItems) ? historyItems : []).slice(0, 5).map((item) => (
                  <tr key={item.id} className="hover:bg-slate-900/40 transition-colors">
                    <td className="py-3 font-medium text-slate-200">{item.resume_title}</td>
                    <td className="py-3 text-slate-300">{item.jd_title}</td>
                    <td className="py-3">
                      <span className="font-bold text-indigo-400">{item.overall_score}%</span>
                    </td>
                    <td className="py-3 text-emerald-400 font-medium">{item.matched_skills_count} skills</td>
                    <td className="py-3 text-slate-500">{formatDate(item.created_at)}</td>
                    <td className="py-3 text-right">
                      <div className="flex items-center justify-end space-x-3">
                        <button
                          onClick={() => loadPastAnalysis(item)}
                          className="text-indigo-400 hover:text-indigo-300 font-medium inline-flex items-center space-x-1"
                          title="View Analysis"
                        >
                          <span>View</span>
                          <ExternalLink className="w-3 h-3" />
                        </button>
                        <button
                          onClick={(e) => handleDeleteHistory(item.id, item.resume_id, e)}
                          className="text-slate-500 hover:text-rose-400 transition-colors p-1"
                          title="Delete from history"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-xs text-slate-400 italic py-4 text-center">
            {loadingHistory ? 'Loading history...' : 'No historical analyses found yet.'}
          </p>
        )}
      </div>
    </div>
  );
}
