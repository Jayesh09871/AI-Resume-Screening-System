import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FileUpload from '../components/FileUpload';
import { useResume } from '../hooks/useResume';
import { 
  FileCheck, 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  Sparkles, 
  Edit3, 
  AlertTriangle, 
  CheckCircle2, 
  Layers 
} from 'lucide-react';

export default function UploadPage() {
  const navigate = useNavigate();
  const { setResumeData } = useResume();
  const [uploadResult, setUploadResult] = useState(null);

  const handleUploadSuccess = (response) => {
    setUploadResult(response);
    setResumeData(
      response.structured_data,
      response.resume_id,
      response.structured_data?.name || `Resume #${response.resume_id}`
    );
  };

  return (
    <div className="max-w-4xl mx-auto py-10 px-4 space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Upload & Parse Resume</h1>
        <p className="text-xs sm:text-sm text-slate-400">
          Upload your existing resume in PDF or DOCX format for instant ATS parsing and extraction
        </p>
      </div>

      {/* Upload Zone */}
      <FileUpload onUploadComplete={handleUploadSuccess} />

      {/* Extracted Overview Card */}
      {uploadResult && (
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-6 animate-fade-in">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                <FileCheck className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">
                  {uploadResult.structured_data?.name || 'Candidate Resume'}
                </h3>
                <p className="text-xs text-slate-400">
                  {uploadResult.page_count} page(s) extracted successfully &bull; ID #{uploadResult.resume_id}
                </p>
              </div>
            </div>

            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 flex items-center space-x-1.5">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Validated with Pydantic</span>
            </span>
          </div>

          {/* Warnings if any */}
          {uploadResult.warnings && uploadResult.warnings.length > 0 && (
            <div className="p-3.5 rounded-xl bg-amber-950/40 border border-amber-500/30 text-amber-200 text-xs space-y-1">
              <div className="flex items-center space-x-1.5 font-semibold text-amber-400">
                <AlertTriangle className="w-4 h-4" />
                <span>Extraction Notices:</span>
              </div>
              <ul className="list-disc pl-5 space-y-0.5 text-[11px]">
                {uploadResult.warnings.map((w, i) => (
                  <li key={i}>{w}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Basic Info Pill Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center space-x-2.5">
              <Mail className="w-4 h-4 text-indigo-400 shrink-0" />
              <div className="overflow-hidden">
                <span className="text-[10px] text-slate-400 block font-medium">Email</span>
                <span className="text-slate-200 truncate block">
                  {uploadResult.structured_data?.email || 'Not detected'}
                </span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center space-x-2.5">
              <Phone className="w-4 h-4 text-indigo-400 shrink-0" />
              <div className="overflow-hidden">
                <span className="text-[10px] text-slate-400 block font-medium">Phone</span>
                <span className="text-slate-200 truncate block">
                  {uploadResult.structured_data?.phone || 'Not detected'}
                </span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center space-x-2.5">
              <MapPin className="w-4 h-4 text-indigo-400 shrink-0" />
              <div className="overflow-hidden">
                <span className="text-[10px] text-slate-400 block font-medium">Location</span>
                <span className="text-slate-200 truncate block">
                  {uploadResult.structured_data?.location || 'Not specified'}
                </span>
              </div>
            </div>
          </div>

          {/* Detected Sections */}
          <div>
            <span className="text-xs font-semibold text-slate-400 block mb-2">Detected Sections:</span>
            <div className="flex flex-wrap gap-2">
              {uploadResult.detected_sections.map((sec) => (
                <span
                  key={sec}
                  className="px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-800/80 border border-slate-700/80 text-slate-200 flex items-center space-x-1"
                >
                  <Layers className="w-3 h-3 text-indigo-400" />
                  <span>{sec}</span>
                </span>
              ))}
            </div>
          </div>

          {/* Skills preview */}
          {uploadResult.structured_data?.skills && (
            <div>
              <span className="text-xs font-semibold text-slate-400 block mb-2">Extracted & Normalized Skills:</span>
              <div className="flex flex-wrap gap-1.5">
                {uploadResult.structured_data.skills.slice(0, 15).map((skill, idx) => (
                  <span
                    key={idx}
                    className="px-2.5 py-1 rounded-lg text-xs font-medium bg-indigo-500/10 border border-indigo-500/20 text-indigo-300"
                  >
                    {skill}
                  </span>
                ))}
                {uploadResult.structured_data.skills.length > 15 && (
                  <span className="px-2 py-1 text-xs text-slate-400">
                    +{uploadResult.structured_data.skills.length - 15} more
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Step 1 Complete / Next Step CTA */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-gradient-to-r from-indigo-950/50 via-slate-900 to-purple-950/40 border border-indigo-500/30">
            <div className="flex items-center space-x-3.5">
              <div className="w-12 h-12 rounded-xl bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 flex items-center justify-center font-black text-sm shrink-0">
                Step 1
              </div>
              <div>
                <h4 className="text-sm font-bold text-white flex items-center space-x-2">
                  <span>Resume Extracted & Ready</span>
                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">
                    Step 1 Done
                  </span>
                </h4>
                <p className="text-xs text-slate-400">
                  Next: Enter your target Job Description in Step 2 to compute ATS match score, missing skills, and interview prep.
                </p>
              </div>
            </div>

            <button
              onClick={() => navigate('/analysis')}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white text-xs font-bold transition-all shadow-md shadow-indigo-500/30 flex items-center justify-center space-x-1.5 shrink-0"
            >
              <Sparkles className="w-4 h-4" />
              <span>Proceed to Step 2: Enter Job Description &rarr;</span>
            </button>
          </div>

          {/* Action buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-end gap-3 pt-4 border-t border-slate-800">
            <button
              onClick={() => navigate('/editor')}
              className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center justify-center space-x-2 transition-colors"
            >
              <Edit3 className="w-4 h-4" />
              <span>Review & Edit Resume</span>
            </button>

            <button
              onClick={() => navigate('/analysis')}
              className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold flex items-center justify-center space-x-2 shadow-lg shadow-indigo-600/30 transition-all"
            >
              <Sparkles className="w-4 h-4" />
              <span>Enter Job Description & Analyze</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
