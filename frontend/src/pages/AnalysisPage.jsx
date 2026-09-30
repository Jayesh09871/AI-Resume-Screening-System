import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useResume } from '../hooks/useResume';
import { useToast } from '../components/Toast';
import { api } from '../services/api';
import BaseAtsScoreCard from '../components/BaseAtsScoreCard';
import ScoreGauge from '../components/ScoreGauge';
import SkillBadge from '../components/SkillBadge';
import RecommendationCard from '../components/RecommendationCard';
import { 
  Sparkles, 
  Send, 
  FileText, 
  CheckCircle2, 
  XCircle, 
  TrendingUp, 
  Loader2, 
  Edit3, 
  Download, 
  Search, 
  BookOpen, 
  ArrowRight, 
  Flame, 
  AlertTriangle, 
  Zap,
  Target,
  Upload
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
    baseAtsScore,
    refreshBaseScore,
    isAnalyzing, 
    setIsAnalyzing 
  } = useResume();
  const { addToast } = useToast();
  const [jdText, setJdText] = useState(currentJd || '');
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState('classic_ats');

  // Auto-refresh baseline score if resume is present but base score is missing
  useEffect(() => {
    if (currentResume?.data && !baseAtsScore) {
      refreshBaseScore();
    }
  }, [currentResume, baseAtsScore]);

  // Sync state if currentJd changes externally
  useEffect(() => {
    setJdText(currentJd || '');
  }, [currentJd]);

  const handleRunAnalysis = async () => {
    if (!jdText.trim() || jdText.length < 20) {
      addToast('Please enter a descriptive Job Description (at least 20 characters).', 'error');
      return;
    }
    if (!currentResume) {
      addToast('No resume loaded. Please upload or create a resume first.', 'error');
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
      addToast('Role-specific ATS Analysis and semantic matching completed!', 'success');
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
  const linguistic = currentAnalysis?.linguistic_analysis;

  if (!currentResume) {
    return (
      <div className="max-w-4xl mx-auto py-16 px-4">
        <div className="glass-card rounded-2xl p-10 border border-slate-800 text-center space-y-4 max-w-md mx-auto">
          <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mx-auto">
            <FileText className="w-7 h-7" />
          </div>
          <div className="space-y-1">
            <h2 className="text-xl font-bold text-white">No Resume Loaded</h2>
            <p className="text-xs text-slate-400">
              Please upload or select an existing resume to view its ATS score and match against job descriptions.
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
    <div className="max-w-7xl mx-auto py-10 px-4 space-y-12">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-extrabold text-white tracking-tight">
          AI Resume Screening & Dual-ATS Intelligence
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 max-w-2xl mx-auto">
          View your resume's standalone ATS quality score first, and optionally match against a target Job Description.
        </p>
      </div>

      {/* PART 1: Baseline Resume ATS Quality Score (No JD Required!) */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-indigo-500"></span>
          <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">
            Part 1 &bull; Standalone Resume ATS Score
          </span>
        </div>

        <BaseAtsScoreCard
          baseScore={baseAtsScore}
          onDownloadPdf={handleDownloadPdf}
          isExportingPdf={isExportingPdf}
          selectedTemplate={selectedTemplate}
          setSelectedTemplate={setSelectedTemplate}
        />
      </div>

      {/* PART 2: Target Job Description Match (Optional) */}
      <div className="space-y-6 pt-4 border-t border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rounded-full bg-purple-500"></span>
              <span className="text-xs font-bold text-purple-400 uppercase tracking-wider">
                Part 2 &bull; Match Against a Job Description (Optional)
              </span>
            </div>
            <h2 className="text-2xl font-black text-white tracking-tight">
              Targeted Role Screening
            </h2>
            <p className="text-xs text-slate-400 max-w-2xl">
              Want to see how you match a specific opening? Paste a Job Description to compute role-specific keyword overlap, missing skills, and semantic alignment.
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
              <FileText className="w-4 h-4 text-purple-400" />
              <span>Target Job Description Requirements</span>
            </span>
            <span>Active Resume: <strong className="text-slate-200">{currentResume?.data?.name || 'Resume'}</strong></span>
          </div>

          <textarea
            rows={6}
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            placeholder="Paste full job description requirements here (Role responsibilities, required qualifications, preferred tech stack)..."
            className="w-full bg-slate-900/80 border border-slate-800 rounded-xl p-4 text-xs text-slate-200 placeholder:text-slate-600 focus:outline-hidden focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-all font-mono leading-relaxed"
          />

          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-1">
            <span className="text-xs text-slate-500">
              {jdText.length} characters entered {jdText.length > 0 && jdText.length < 20 && '(min 20 characters)'}
            </span>

            <div className="flex items-center space-x-3 w-full sm:w-auto">
              {jdText && (
                <button
                  onClick={() => { setJdText(''); setCurrentJd(''); }}
                  className="w-full sm:w-auto px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 text-xs font-semibold transition-colors"
                >
                  Clear JD
                </button>
              )}

              <button
                onClick={handleRunAnalysis}
                disabled={isAnalyzing || !jdText.trim() || jdText.length < 20}
                className="w-full sm:w-auto flex items-center justify-center space-x-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 text-white text-xs font-bold shadow-lg shadow-purple-500/25 transition-all disabled:opacity-50"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Screening against JD...</span>
                  </>
                ) : (
                  <>
                    <Target className="w-4 h-4" />
                    <span>Run JD Match Screening</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Analysis Results Display */}
      {matchData && (
        <div className="space-y-8 animate-fade-in">
          {/* Dedicated Section Header: ATS Score with JD */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl bg-gradient-to-r from-indigo-950/60 via-purple-950/40 to-slate-900 border border-indigo-500/30 shadow-lg">
            <div className="space-y-1">
              <div className="inline-flex items-center space-x-2 px-2.5 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[11px] font-semibold">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Screening Complete</span>
              </div>
              <h2 className="text-xl font-black text-white tracking-tight">
                ATS Compatibility & Score with Job Description
              </h2>
              <p className="text-xs text-slate-400">
                Evaluation of candidate profile against the targeted job requirements
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

          {/* 1. Score Gauge Card */}
          <ScoreGauge breakdown={matchData.breakdown} />

          {/* 2. Linguistic & Recruiter Quality Card */}
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

              <p className="text-xs text-slate-300 bg-slate-900/40 p-3 rounded-xl border border-slate-800/60">
                <strong>Recruiter Feedback:</strong> {linguistic.overall_feedback}
              </p>
            </div>
          )}

          {/* 3. Skills Coverage Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Matched Required Skills */}
            <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  <h3 className="text-sm font-bold text-white">Matched Required Skills</h3>
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

            {/* Missing Required Skills with Quick-Add */}
            <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <XCircle className="w-5 h-5 text-rose-400" />
                  <h3 className="text-sm font-bold text-white">Missing Required Skills</h3>
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

          {/* 5. AI Evidence-Based Recommendations */}
          {currentAnalysis?.suggestions && currentAnalysis.suggestions.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-white">
                    Actionable Improvement Recommendations
                  </h3>
                  <p className="text-xs text-slate-400">
                    Dual-evidence verified &bull; Zero fabricated credentials
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
        </div>
      )}
    </div>
  );
}
