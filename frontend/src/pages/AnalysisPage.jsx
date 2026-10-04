import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useResume } from '../hooks/useResume';
import { useToast } from '../components/Toast';
import { api } from '../services/api';
import ScoreGauge from '../components/ScoreGauge';
import SkillBadge from '../components/SkillBadge';
import RecommendationCard from '../components/RecommendationCard';
import { 
  Sparkles, 
  FileText, 
  CheckCircle2, 
  XCircle, 
  TrendingUp, 
  Loader2, 
  Edit3, 
  Download, 
  ArrowRight, 
  Flame, 
  AlertTriangle, 
  Zap,
  Target,
  Upload,
  Link2,
  Globe,
  Briefcase,
  GraduationCap,
  Award,
  Layers,
  HelpCircle,
  BookOpen,
  ListChecks
} from 'lucide-react';

const SAMPLE_JDS = [
  {
    title: 'Senior Python & FastAPI Engineer',
    text: `Senior Backend Developer
TechForward Inc. - Remote / San Francisco, CA

About the Role:
We are seeking an experienced Backend Software Engineer to build resilient distributed systems and API architectures.

Key Responsibilities:
- Design, build, and maintain high-volume RESTful APIs and microservices in Python.
- Optimize database schemas and queries in PostgreSQL.
- Implement containerized deployments using Docker and Kubernetes.
- Collaborate with frontend engineers using React to integrate scalable endpoints.

Required Qualifications & Skills:
- 3+ years of professional backend software engineering experience.
- Strong proficiency in Python and modern frameworks like FastAPI or Django.
- Solid experience with relational databases, specifically PostgreSQL.
- Practical experience with Docker and REST APIs.

Preferred Qualifications:
- Experience with Redis caching and asynchronous queues.
- Familiarity with Kubernetes, AWS cloud infrastructure, and CI/CD pipelines.
- Bachelor's degree in Computer Science or related STEM field.`
  },
  {
    title: 'Full Stack React & Node Developer',
    text: `Full Stack Software Engineer
WebCloud Solutions

Responsibilities:
- Build responsive frontend web applications using React, TypeScript, and Tailwind CSS.
- Develop scalable backend REST APIs using Node.js and Express or NestJS.
- Design database architectures in PostgreSQL or MongoDB.
- Write unit tests and maintain CI/CD pipelines with GitHub Actions.

Required Skills:
- React, JavaScript / TypeScript, Node.js, HTML5, CSS3, SQL.
- Strong understanding of state management (Redux or Context API).

Preferred Skills:
- Docker, AWS, GraphQL, Next.js.`
  }
];

export default function AnalysisPage() {
  const navigate = useNavigate();
  const { 
    currentResume, 
    updateStructuredResume, 
    currentJd, 
    setCurrentJd, 
    currentAnalysis, 
    setCurrentAnalysis, 
    isAnalyzing, 
    setIsAnalyzing 
  } = useResume();
  const { addToast } = useToast();
  
  const [jdText, setJdText] = useState(currentJd || '');
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState('classic_ats');
  const [jobUrl, setJobUrl] = useState('');
  const [isScrapingUrl, setIsScrapingUrl] = useState(false);
  const [scrapedMeta, setScrapedMeta] = useState(null);

  // Sync state if currentJd changes externally
  useEffect(() => {
    if (currentJd && !jdText) {
      setJdText(currentJd);
    }
  }, [currentJd]);

  const handleFetchJdFromUrl = async () => {
    if (!jobUrl.trim()) {
      addToast('Please enter a job posting URL (e.g. Greenhouse, Lever, LinkedIn).', 'warning');
      return;
    }
    setIsScrapingUrl(true);
    setScrapedMeta(null);
    try {
      const data = await api.scrapeJobDescription(jobUrl.trim());
      setJdText(data.jd_text);
      setCurrentJd(data.jd_text);
      setScrapedMeta(data);
      addToast(
        `Extracted ${data.word_count} words${data.title ? ` for "${data.title}"` : ''}!`,
        'success'
      );
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Failed to fetch job description';
      addToast(`Scraper error: ${msg}`, 'error');
    } finally {
      setIsScrapingUrl(false);
    }
  };

  const handleRunAnalysis = async () => {
    if (!jdText.trim() || jdText.length < 20) {
      addToast('Please enter a descriptive Job Description (at least 20 characters).', 'error');
      return;
    }
    if (!currentResume) {
      addToast('No resume loaded. Please upload or select a resume first.', 'error');
      navigate('/upload');
      return;
    }

    setIsAnalyzing(true);
    setCurrentJd(jdText);

    try {
      const response = await api.analyzeResume({
        resumeId: currentResume.id,
        resumeData: currentResume.data,
        jdText: jdText,
      });

      setCurrentAnalysis(response);
      addToast('Resume vs Job Description ATS Analysis completed!', 'success');
    } catch (err) {
      addToast(`Analysis error: ${err.message}`, 'error');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!currentResume?.id) {
      addToast('Please save or update your resume before downloading PDF.', 'error');
      return;
    }
    setIsExportingPdf(true);
    try {
      await api.downloadResumePdf(
        currentResume.id,
        `${currentResume.data?.name || 'Resume'}_${selectedTemplate}.pdf`,
        selectedTemplate
      );
      addToast(`ATS PDF (${selectedTemplate}) downloaded successfully!`, 'success');
    } catch (err) {
      addToast(`PDF generation failed: ${err.message}`, 'error');
    } finally {
      setIsExportingPdf(false);
    }
  };

  const handleAddMissingSkill = async (skill) => {
    if (!currentResume?.data) return;
    if (!currentResume.data.skills?.includes(skill)) {
      const updatedSkills = [...(currentResume.data.skills || []), skill];
      const updatedResume = { ...currentResume.data, skills: updatedSkills };
      await updateStructuredResume(updatedResume);
      addToast(`Added "${skill}" to your resume!`, 'success');
    }
  };

  const matchData = currentAnalysis?.match_data;
  const breakdown = matchData?.breakdown;
  const linguistic = currentAnalysis?.linguistic_analysis;

  if (!currentResume) {
    return (
      <div className="max-w-4xl mx-auto py-16 px-4">
        <div className="glass-card rounded-2xl p-10 border border-slate-800 text-center space-y-4 max-w-md mx-auto">
          <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mx-auto">
            <FileText className="w-7 h-7" />
          </div>
          <div className="space-y-1">
            <h2 className="text-xl font-bold text-white">Step 1 Required: Upload Resume</h2>
            <p className="text-xs text-slate-400">
              Please upload your resume first. The Job Description and ATS score screening require an active candidate resume.
            </p>
          </div>
          <button
            onClick={() => navigate('/upload')}
            className="inline-flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition-all"
          >
            <Upload className="w-4 h-4" />
            <span>Upload Resume Now</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto py-10 px-4 space-y-8">
      {/* Visual Workflow Steps Bar */}
      <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80">
        <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center space-x-2">
            <span className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 font-bold flex items-center justify-center text-[11px] border border-emerald-500/30">
              ✓
            </span>
            <span className="font-semibold text-slate-200">Step 1: Upload Resume</span>
            <span className="text-[11px] text-slate-500">({currentResume.data?.name || currentResume.title || 'Loaded'})</span>
          </div>

          <div className="text-slate-600 hidden sm:block">&rarr;</div>

          <div className="flex items-center space-x-2">
            <span className={`w-6 h-6 rounded-full font-bold flex items-center justify-center text-[11px] border ${
              jdText.trim().length >= 20
                ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                : 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40'
            }`}>
              2
            </span>
            <span className={`font-semibold ${jdText.trim().length >= 20 ? 'text-slate-200' : 'text-indigo-300'}`}>
              Step 2: Enter Job Description
            </span>
          </div>

          <div className="text-slate-600 hidden sm:block">&rarr;</div>

          <div className="flex items-center space-x-2">
            <span className={`w-6 h-6 rounded-full font-bold flex items-center justify-center text-[11px] border ${
              matchData ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-slate-800 text-slate-400 border-slate-700'
            }`}>
              3-5
            </span>
            <span className={`font-semibold ${matchData ? 'text-slate-200' : 'text-slate-400'}`}>
              Analyze & View Results
            </span>
          </div>

          <div className="text-slate-600 hidden sm:block">&rarr;</div>

          <div className="flex items-center space-x-2">
            <span className="w-6 h-6 rounded-full bg-slate-800 text-slate-400 font-bold flex items-center justify-center text-[11px] border border-slate-700">
              6
            </span>
            <span className="font-semibold text-slate-400">Step 6: Interview Prep</span>
          </div>
        </div>
      </div>

      {/* STEP 2: Job Description Input (Mandatory First) */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-pulse"></span>
              <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">
                Step 2 &bull; Enter Job Description (Mandatory First)
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              Target Job Description
            </h1>
            <p className="text-xs text-slate-400 max-w-2xl">
              ATS score, match percentage, and gap analysis are calculated by comparing your resume against this job description.
            </p>
          </div>

          <div className="flex items-center space-x-2 text-xs">
            <span className="text-slate-500">Sample JDs:</span>
            {SAMPLE_JDS.map((sample, idx) => (
              <button
                key={idx}
                onClick={() => setJdText(sample.text)}
                className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-indigo-300 border border-slate-700 font-medium transition-colors text-[11px]"
              >
                {sample.title.split(' ')[0]}
              </button>
            ))}
          </div>
        </div>

        {/* Input Textarea Card */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-semibold text-slate-300 flex items-center space-x-1.5">
              <FileText className="w-4 h-4 text-indigo-400" />
              <span>Job Description Requirements</span>
            </span>
            <span>
              Active Resume: <strong className="text-slate-200">{currentResume?.data?.name || currentResume?.title || 'Resume'}</strong>
            </span>
          </div>

          {/* Auto-Fetch from Job URL */}
          <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2.5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-xs">
              <span className="font-semibold text-indigo-300 flex items-center space-x-1.5">
                <Link2 className="w-3.5 h-3.5 text-indigo-400" />
                <span>Auto-Fetch from Job URL</span>
              </span>
              <span className="text-[11px] text-slate-500">
                Supports Greenhouse, Lever, Ashby, LinkedIn, Indeed & Careers pages
              </span>
            </div>

            <div className="flex flex-col sm:flex-row items-center gap-2">
              <div className="relative flex-1 w-full">
                <Globe className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="url"
                  value={jobUrl}
                  onChange={(e) => setJobUrl(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter') handleFetchJdFromUrl(); }}
                  placeholder="Paste job posting link (e.g. https://boards.greenhouse.io/... or https://jobs.lever.co/...)"
                  className="w-full bg-slate-950/90 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-200 placeholder:text-slate-600 focus:outline-hidden focus:border-indigo-500 transition-all font-mono"
                />
              </div>

              <button
                type="button"
                onClick={handleFetchJdFromUrl}
                disabled={isScrapingUrl || !jobUrl.trim()}
                className="w-full sm:w-auto px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold flex items-center justify-center space-x-1.5 transition-colors shrink-0 shadow-xs"
              >
                {isScrapingUrl ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Extracting JD...</span>
                  </>
                ) : (
                  <>
                    <Download className="w-3.5 h-3.5" />
                    <span>Fetch JD</span>
                  </>
                )}
              </button>
            </div>

            {scrapedMeta && (
              <div className="text-[11px] text-emerald-400 flex items-center space-x-2 pt-1">
                <span>&check; Cleaned text extracted</span>
                {scrapedMeta.company && <span>&bull; Company: {scrapedMeta.company}</span>}
                {scrapedMeta.title && <span>&bull; Role: {scrapedMeta.title}</span>}
              </div>
            )}
          </div>

          {/* Textarea */}
          <div className="relative">
            <textarea
              rows={8}
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              placeholder="Paste the full job description here (responsibilities, required skills, preferred qualifications, experience requirements)..."
              className="w-full p-4 rounded-xl bg-slate-900/60 border border-slate-800 focus:border-indigo-500 focus:outline-hidden text-xs text-slate-200 leading-relaxed font-mono transition-colors resize-y"
            />
          </div>

          {/* Step 3: Run Analysis Footer */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2">
            <div className="text-xs text-slate-400">
              <span>{jdText.length} characters</span>
              {jdText.length > 0 && jdText.length < 20 && (
                <span className="text-rose-400 ml-2">(Need at least 20 characters to run screening)</span>
              )}
            </div>

            <div className="flex items-center space-x-3">
              {jdText && (
                <button
                  type="button"
                  onClick={() => setJdText('')}
                  className="text-xs text-slate-500 hover:text-slate-300 transition-colors"
                >
                  Clear JD
                </button>
              )}

              <button
                onClick={handleRunAnalysis}
                disabled={isAnalyzing || !jdText.trim() || jdText.length < 20}
                className="w-full sm:w-auto flex items-center justify-center space-x-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white text-xs font-bold shadow-lg shadow-indigo-500/25 transition-all disabled:opacity-50"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Screening Resume against JD...</span>
                  </>
                ) : (
                  <>
                    <Target className="w-4 h-4" />
                    <span>Step 3: Run Resume vs JD Analysis</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* AWAITING ANALYSIS STATE (No generic scores shown before JD!) */}
      {!matchData && (
        <div className="glass-card rounded-2xl p-8 border border-slate-800/80 text-center space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mx-auto">
            <Sparkles className="w-6 h-6" />
          </div>
          <div className="max-w-md mx-auto space-y-1.5">
            <h3 className="text-base font-bold text-white">Awaiting Job Description & Analysis</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Paste or fetch your Job Description above and click <strong>"Run Resume vs JD Analysis"</strong> to generate your ATS Score, Match Percentage, Skills Gap, Experience Alignment, and Interview Prep.
            </p>
          </div>
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-[11px] text-slate-400 font-medium">
            <span>Flow: Upload Resume &rarr; Enter JD &rarr; Run Analysis &rarr; View Results</span>
          </div>
        </div>
      )}

      {/* STEP 4 & 5: RESULTS DISPLAY (Only after JD analysis is run!) */}
      {matchData && breakdown && (
        <div className="space-y-8 animate-fade-in">
          {/* Header Banner */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl bg-gradient-to-r from-indigo-950/60 via-purple-950/40 to-slate-900 border border-indigo-500/30 shadow-lg">
            <div className="space-y-1">
              <div className="inline-flex items-center space-x-2 px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[11px] font-semibold">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Step 5: Screening & Scoring Complete</span>
              </div>
              <h2 className="text-xl font-black text-white tracking-tight">
                Resume–Job Description Match Analysis
              </h2>
              <p className="text-xs text-slate-400">
                Calculated strictly by comparing <strong className="text-slate-200">{currentResume?.data?.name || 'Resume'}</strong> against the provided Job Description.
              </p>
            </div>

            {/* Quick Template & PDF Export Actions */}
            <div className="flex flex-wrap items-center gap-2">
              <select
                value={selectedTemplate}
                onChange={(e) => setSelectedTemplate(e.target.value)}
                className="bg-slate-900 border border-slate-700 text-xs text-indigo-300 font-semibold rounded-xl px-3 py-2 focus:outline-hidden"
              >
                <option value="classic_ats">Classic ATS</option>
                <option value="modern_tech">Modern Tech</option>
                <option value="executive">Executive</option>
              </select>

              <button
                onClick={() => navigate('/editor')}
                className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-xs transition-colors"
              >
                <Edit3 className="w-3.5 h-3.5" />
                <span>Edit Resume</span>
              </button>

              <button
                onClick={handleDownloadPdf}
                disabled={isExportingPdf}
                className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors disabled:opacity-50"
              >
                {isExportingPdf ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />}
                <span>Export PDF</span>
              </button>
            </div>
          </div>

          {/* Key Metrics KPI Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            <div className="glass-card p-4 rounded-xl border border-indigo-500/30 bg-indigo-950/20 space-y-1">
              <span className="text-[11px] text-slate-400 font-medium block">ATS Compatibility</span>
              <div className="text-2xl font-black text-white">{breakdown.overall_score}%</div>
              <span className="text-[10px] text-indigo-300 font-medium">Overall Compatibility</span>
            </div>

            <div className="glass-card p-4 rounded-xl border border-purple-500/30 bg-purple-950/20 space-y-1">
              <span className="text-[11px] text-slate-400 font-medium block">Resume-JD Match</span>
              <div className="text-2xl font-black text-purple-300">{matchData.match_percentage || breakdown.overall_score}%</div>
              <span className="text-[10px] text-purple-400 font-medium">Weighted Fit</span>
            </div>

            <div className="glass-card p-4 rounded-xl border border-emerald-500/30 bg-emerald-950/20 space-y-1">
              <span className="text-[11px] text-slate-400 font-medium block">Required Skills</span>
              <div className="text-2xl font-black text-emerald-400">
                {matchData.matched_required_skills.length}/{matchData.required_skills?.length || (matchData.matched_required_skills.length + matchData.missing_required_skills.length)}
              </div>
              <span className="text-[10px] text-emerald-300 font-medium">{breakdown.required_skill_score}% Coverage</span>
            </div>

            <div className="glass-card p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[11px] text-slate-400 font-medium block">Experience Match</span>
              <div className="text-2xl font-black text-white">{matchData.experience_match?.score || breakdown.experience_relevance}%</div>
              <span className="text-[10px] text-indigo-300 font-medium">{matchData.experience_match?.status || 'Evaluated'}</span>
            </div>

            <div className="glass-card p-4 rounded-xl border border-slate-800 space-y-1 col-span-2 sm:col-span-1">
              <span className="text-[11px] text-slate-400 font-medium block">Education Match</span>
              <div className="text-2xl font-black text-white">{matchData.education_match?.score || 85}%</div>
              <span className="text-[10px] text-teal-300 font-medium">{matchData.education_match?.status || 'Evaluated'}</span>
            </div>
          </div>

          {/* 1. Score Gauge Breakdown */}
          <ScoreGauge breakdown={breakdown} />

          {/* 2. Candidate Strengths Against This JD */}
          {matchData.strengths && matchData.strengths.length > 0 && (
            <div className="glass-card rounded-2xl p-6 border border-emerald-500/30 bg-emerald-950/10 space-y-3">
              <div className="flex items-center space-x-2.5 text-emerald-400">
                <Award className="w-5 h-5 shrink-0" />
                <h3 className="text-base font-bold text-white">Candidate Strengths for this Role</h3>
              </div>
              <ul className="space-y-2 text-xs text-slate-300">
                {matchData.strengths.map((str, idx) => (
                  <li key={idx} className="flex items-start space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                    <span>{str}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* 3. Skills Coverage Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Required Skills from JD */}
            <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <ListChecks className="w-5 h-5 text-indigo-400" />
                  <h3 className="text-sm font-bold text-white">Required Skills from JD</h3>
                </div>
                <span className="text-xs font-bold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300">
                  {matchData.required_skills?.length || (matchData.matched_required_skills.length + matchData.missing_required_skills.length)} identified
                </span>
              </div>

              <div className="flex flex-wrap gap-2">
                {(matchData.required_skills?.length ? matchData.required_skills : [...matchData.matched_required_skills, ...matchData.missing_required_skills]).map((skill) => {
                  const isMatched = matchData.matched_required_skills.includes(skill);
                  return (
                    <span
                      key={skill}
                      className={`px-2.5 py-1 rounded-lg text-xs font-medium border flex items-center space-x-1 ${
                        isMatched
                          ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                          : 'bg-rose-500/10 text-rose-300 border-rose-500/30'
                      }`}
                    >
                      <span>{isMatched ? '✓' : '✗'}</span>
                      <span>{skill}</span>
                    </span>
                  );
                })}
              </div>
            </div>

            {/* Matched Required Skills */}
            <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  <h3 className="text-sm font-bold text-white">Matching Skills</h3>
                </div>
                <span className="text-xs font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">
                  {matchData.matched_required_skills.length} matched
                </span>
              </div>

              {matchData.matched_required_skills.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {matchData.matched_required_skills.map((skill) => (
                    <SkillBadge key={skill} skill={skill} status="matched" />
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400 italic">No direct required skill matches detected.</p>
              )}
            </div>
          </div>

          {/* Missing Required Skills with Quick-Add */}
          <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <XCircle className="w-5 h-5 text-rose-400" />
                <h3 className="text-sm font-bold text-white">Missing Skills from Job Description</h3>
              </div>
              <span className="text-xs font-bold px-2 py-0.5 rounded bg-rose-500/20 text-rose-300">
                {matchData.missing_required_skills.length} missing
              </span>
            </div>

            {matchData.missing_required_skills.length > 0 ? (
              <div>
                <div className="flex flex-wrap gap-2">
                  {matchData.missing_required_skills.map((skill) => (
                    <SkillBadge
                      key={skill}
                      skill={skill}
                      status="missing_required"
                      onAdd={handleAddMissingSkill}
                    />
                  ))}
                </div>
                <p className="text-[11px] text-slate-400 mt-3">
                  Tip: Click the <strong className="text-rose-300">+</strong> icon on any skill you have experience with to instantly add it to your resume.
                </p>
              </div>
            ) : (
              <p className="text-xs text-emerald-400 font-medium">
                &check; 100% of required skills are covered in your resume!
              </p>
            )}
          </div>

          {/* Experience Match & Education Match */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Experience Match */}
            <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                <div className="flex items-center space-x-2">
                  <Briefcase className="w-5 h-5 text-purple-400" />
                  <h3 className="text-sm font-bold text-white">Experience Match</h3>
                </div>
                <span className="text-xs font-bold px-2.5 py-0.5 rounded bg-purple-500/20 text-purple-300">
                  {matchData.experience_match?.status || 'Evaluated'} ({matchData.experience_match?.score || breakdown.experience_relevance}%)
                </span>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">
                {matchData.experience_match?.summary || 'Experience evaluated against job title and seniorities.'}
              </p>

              {matchData.experience_match?.recent_titles && matchData.experience_match.recent_titles.length > 0 && (
                <div className="pt-2">
                  <span className="text-[11px] font-semibold text-slate-400 block mb-1">Detected Candidate Roles:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {matchData.experience_match.recent_titles.map((t, idx) => (
                      <span key={idx} className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-[11px] text-slate-300 font-mono">
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {matchData.experience_match?.jd_requirements && (
                <div className="pt-2 text-[11px] text-slate-400 border-t border-slate-800/60">
                  <strong className="text-slate-300">JD Experience Requirement:</strong> {matchData.experience_match.jd_requirements.join(', ')}
                </div>
              )}
            </div>

            {/* Education Match */}
            <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                <div className="flex items-center space-x-2">
                  <GraduationCap className="w-5 h-5 text-teal-400" />
                  <h3 className="text-sm font-bold text-white">Education Match</h3>
                </div>
                <span className="text-xs font-bold px-2.5 py-0.5 rounded bg-teal-500/20 text-teal-300">
                  {matchData.education_match?.status || 'Evaluated'} ({matchData.education_match?.score || 90}%)
                </span>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">
                {matchData.education_match?.summary || 'Candidate degrees verified against education requirements.'}
              </p>

              {matchData.education_match?.degrees && matchData.education_match.degrees.length > 0 && (
                <div className="pt-2">
                  <span className="text-[11px] font-semibold text-slate-400 block mb-1">Degrees Found:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {matchData.education_match.degrees.map((d, idx) => (
                      <span key={idx} className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-[11px] text-teal-300 font-mono">
                        {d}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {matchData.education_match?.jd_requirements && (
                <div className="pt-2 text-[11px] text-slate-400 border-t border-slate-800/60">
                  <strong className="text-slate-300">JD Education Requirement:</strong> {matchData.education_match.jd_requirements.join(', ')}
                </div>
              )}
            </div>
          </div>

          {/* Preferred Skills & Keywords Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Preferred Skills */}
            <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-3">
              <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                Preferred Skills Breakdown
              </h4>
              <div className="space-y-2">
                <div className="flex flex-wrap gap-1.5">
                  {matchData.matched_preferred_skills.map((s) => (
                    <SkillBadge key={s} skill={s} status="matched" />
                  ))}
                  {matchData.missing_preferred_skills.map((s) => (
                    <SkillBadge
                      key={s}
                      skill={s}
                      status="missing_preferred"
                      onAdd={handleAddMissingSkill}
                    />
                  ))}
                  {matchData.matched_preferred_skills.length === 0 && matchData.missing_preferred_skills.length === 0 && (
                    <span className="text-xs text-slate-500 italic">No secondary preferred skills listed in JD.</span>
                  )}
                </div>
              </div>
            </div>

            {/* JD Keywords Found / Missing */}
            <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-3">
              <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                Domain Keyword Frequency
              </h4>
              <div className="flex flex-wrap gap-1.5 text-xs">
                {matchData.keywords_found.map((k) => (
                  <span key={k} className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-300 border border-blue-500/20 font-mono text-[11px]">
                    &check; {k}
                  </span>
                ))}
                {matchData.keywords_missing.map((k) => (
                  <span key={k} className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 font-mono text-[11px]">
                    &times; {k}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* 4. Semantic Alignment Section */}
          {matchData.semantic_matches && matchData.semantic_matches.length > 0 && (
            <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                <div className="flex items-center space-x-2.5">
                  <Sparkles className="w-5 h-5 text-indigo-400" />
                  <h3 className="text-base font-bold text-white">Semantic Requirement Alignment</h3>
                </div>
                <span className="text-xs text-slate-400 font-mono">
                  all-MiniLM-L6-v2 cosine distance
                </span>
              </div>

              <div className="space-y-3">
                {matchData.semantic_matches.map((item, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-2 text-xs"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-200">
                        Target Requirement: <span className="text-indigo-300">{item.jd_requirement}</span>
                      </span>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${
                          item.status === 'strong'
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                            : item.status === 'moderate'
                            ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                            : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                        }`}
                      >
                        {item.status} ({Math.round(item.similarity_score * 100)}% similarity)
                      </span>
                    </div>

                    <div className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800/80 text-slate-300 italic text-[11px]">
                      Closest Resume Statement: "{item.resume_evidence}"
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 5. Linguistic & Recruiter Quality Card */}
          {linguistic && (
            <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-3">
                <div className="flex items-center space-x-2.5">
                  <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
                    <Flame className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white">Linguistic & Recruiter Quality Analysis</h3>
                    <p className="text-xs text-slate-400">Evaluates action verbs, passive voice, and quantified business impact</p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <span className="text-xs text-slate-400 font-medium">Linguistic Score:</span>
                  <span className={`text-base font-black px-2.5 py-0.5 rounded-lg border ${
                    linguistic.linguistic_score >= 80
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      : linguistic.linguistic_score >= 60
                      ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                      : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                  }`}>
                    {linguistic.linguistic_score}%
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="flex items-center space-x-1.5 text-indigo-400 font-semibold mb-1">
                    <Zap className="w-3.5 h-3.5" />
                    <span>Strong Action Verbs ({linguistic.action_verbs_found.length})</span>
                  </div>
                  <div className="flex flex-wrap gap-1 mt-1.5">
                    {linguistic.action_verbs_found.slice(0, 8).map((v) => (
                      <span key={v} className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 font-mono text-[10px]">
                        {v}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="flex items-center space-x-1.5 text-emerald-400 font-semibold mb-1">
                    <TrendingUp className="w-3.5 h-3.5" />
                    <span>Quantified Impact</span>
                  </div>
                  <div className="text-base font-bold text-white mt-1">
                    {linguistic.quantified_ratio}% of bullets
                  </div>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    {linguistic.quantified_bullets_count} of {linguistic.total_bullets_count} bullets include quantifiable metrics
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="flex items-center space-x-1.5 text-rose-400 font-semibold mb-1">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>Passive Voice Flags ({linguistic.passive_phrases_detected.length})</span>
                  </div>
                  {linguistic.passive_phrases_detected.length > 0 ? (
                    <div className="space-y-1 mt-1">
                      {linguistic.passive_phrases_detected.map((p, idx) => (
                        <p key={idx} className="text-[11px] text-rose-300 font-mono truncate">
                          &bull; {p}
                        </p>
                      ))}
                    </div>
                  ) : (
                    <p className="text-[11px] text-emerald-400 mt-1">
                      &check; No weak passive phrases detected!
                    </p>
                  )}
                </div>
              </div>

              {linguistic.overall_feedback && (
                <p className="text-xs text-slate-300 bg-slate-900/40 p-3 rounded-xl border border-slate-800/60">
                  <strong>Recruiter Feedback:</strong> {linguistic.overall_feedback}
                </p>
              )}
            </div>
          )}

          {/* 6. AI Evidence-Based Recommendations */}
          {currentAnalysis?.suggestions && currentAnalysis.suggestions.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-white">
                    Actionable Improvement Suggestions
                  </h3>
                  <p className="text-xs text-slate-400">
                    Dual-evidence verified &bull; Suggestions to boost ATS match for this job description
                  </p>
                </div>
                <span className="text-xs text-purple-400 font-semibold px-2.5 py-1 rounded-full bg-purple-500/10 border border-purple-500/20">
                  {currentAnalysis.suggestions.length} Tailoring Tips
                </span>
              </div>

              <div className="space-y-3">
                {currentAnalysis.suggestions.map((sug, idx) => (
                  <RecommendationCard
                    key={idx}
                    suggestion={sug}
                    onApply={() => navigate('/editor')}
                  />
                ))}
              </div>
            </div>
          )}

          {/* STEP 6: Interview Preparation Generator CTA */}
          <div className="p-6 rounded-2xl bg-gradient-to-r from-purple-950/50 via-indigo-950/40 to-slate-900 border border-purple-500/30 space-y-4 shadow-xl">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="space-y-1.5">
                <div className="inline-flex items-center space-x-2 px-2.5 py-0.5 rounded-full bg-purple-500/20 border border-purple-500/30 text-purple-300 text-[11px] font-semibold">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Step 6: Interview Preparation</span>
                </div>
                <h3 className="text-lg font-bold text-white">
                  Generate Interview Preparation Questions & Answers
                </h3>
                <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">
                  Generate <strong>5 technical questions</strong> (probing matching & missing skills) and <strong>3 behavioral questions</strong> with concise suggested answers and tips, customized directly for this role.
                </p>
              </div>

              <button
                onClick={() => navigate('/interview-prep')}
                className="inline-flex items-center justify-center space-x-2 px-6 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-purple-500/30 transition-all shrink-0"
              >
                <BookOpen className="w-4 h-4" />
                <span>Start Interview Preparation &rarr;</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
