import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { useResume } from '../hooks/useResume';
import { useToast } from '../components/Toast';
import { formatDate } from '../utils/formatters';
import { 
  History, 
  Trash2, 
  ExternalLink, 
  Download, 
  TrendingUp, 
  CheckCircle2, 
  XCircle, 
  Loader2 
} from 'lucide-react';

export default function HistoryPage() {
  const navigate = useNavigate();
  const { setCurrentResume, setCurrentAnalysis } = useResume();
  const { addToast } = useToast();
  const [historyItems, setHistoryItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await api.getHistory();
      setHistoryItems(data);
    } catch (err) {
      addToast(`Failed to load history: ${err.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenAnalysis = async (item) => {
    try {
      const fullAnalysis = await api.getAnalysis(item.id);
      setCurrentAnalysis(fullAnalysis);

      if (item.resume_id) {
        const fullResume = await api.getResume(item.resume_id);
        setCurrentResume({
          id: fullResume.id,
          title: fullResume.title,
          data: fullResume.structured_data,
        });
      }
      navigate('/analysis');
    } catch (err) {
      addToast(`Error loading analysis: ${err.message}`, 'error');
    }
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    try {
      await api.deleteHistoryItem(id);
      setHistoryItems((prev) => prev.filter((item) => item.id !== id));
      addToast('Analysis record deleted.', 'info');
    } catch (err) {
      addToast(`Delete failed: ${err.message}`, 'error');
    }
  };

  return (
    <div className="max-w-7xl mx-auto py-10 px-4 space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Analysis History</h1>
        <p className="text-xs sm:text-sm text-slate-400">
          Review and compare all past resume screenings and ATS evaluation reports
        </p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20 text-slate-400">
          <Loader2 className="w-8 h-8 animate-spin" />
        </div>
      ) : historyItems.length === 0 ? (
        <div className="glass-card rounded-2xl p-12 text-center border border-slate-800 space-y-3">
          <History className="w-10 h-10 text-slate-600 mx-auto" />
          <h3 className="text-base font-bold text-white">No Previous Analyses</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            You haven't run any resume screenings yet. Upload a resume and match against a job description.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {historyItems.map((item) => (
            <div
              key={item.id}
              onClick={() => handleOpenAnalysis(item)}
              className="glass-card glass-card-hover rounded-2xl p-5 border border-slate-800 cursor-pointer space-y-4 flex flex-col justify-between"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>Report #{item.id}</span>
                  <span>{formatDate(item.created_at)}</span>
                </div>

                <h3 className="text-base font-bold text-white line-clamp-1">
                  {item.resume_title}
                </h3>
                <p className="text-xs text-indigo-300 font-medium line-clamp-1">
                  Target: {item.jd_title}
                </p>
              </div>

              {/* Score and Stats */}
              <div className="grid grid-cols-3 gap-2 py-3 border-y border-slate-800/80 text-center">
                <div>
                  <span className="text-[10px] text-slate-400 block">ATS Score</span>
                  <span className="text-lg font-black text-white">{item.overall_score}%</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block">Matched</span>
                  <span className="text-lg font-black text-emerald-400">{item.matched_skills_count}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block">Missing</span>
                  <span className="text-lg font-black text-rose-400">{item.missing_skills_count}</span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-between pt-1">
                <span className="text-xs text-indigo-400 font-semibold flex items-center space-x-1">
                  <span>View Breakdown</span>
                  <ExternalLink className="w-3 h-3" />
                </span>

                <button
                  onClick={(e) => handleDelete(item.id, e)}
                  title="Delete from history"
                  className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
