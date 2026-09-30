
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Sparkles, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { useResume } from '../hooks/useResume';
import { useToast } from '../components/Toast';
import { api } from '../services/api';

console.log("INTERVIEW PAGE API:", api);
console.log("INTERVIEW PAGE METHOD:", typeof api.generateInterviewPrep);

export default function InterviewPrepPage() {
  const { currentResume, currentJd, setCurrentJd } = useResume();
  const { showToast } = useToast();

  const [jdText, setJdText] = useState(currentJd || '');
  const [questions, setQuestions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const resumeData = currentResume?.data;

  const handleGenerate = async () => {
    if (!resumeData && !currentResume?.id) {
      setError('Please upload your resume before generating interview questions.');
      return;
    }

    if (jdText.trim().length < 10) {
      setError('Please enter a valid Job Description (at least 10 characters).');
      return;
    }

    if (typeof api?.generateInterviewPrep !== 'function') {
      setError(
        'Interview Prep API function is not available. Please restart the frontend development server and refresh the page.'
      );
      console.error('Available API methods:', Object.keys(api || {}));
      console.error('generateInterviewPrep:', api?.generateInterviewPrep);
      return;
    }

    setLoading(true);
    setError('');
    setQuestions(null);

    try {
      const result = await api.generateInterviewPrep({
        resumeId: currentResume?.id,
        resumeData,
        jdText: jdText.trim(),
      });

      setQuestions(result);
      setCurrentJd(jdText.trim());
      showToast?.('Interview questions generated successfully!', 'success');
    } catch (err) {
      console.error('Interview Prep generation error:', err);
      setError(err.message || 'Failed to generate interview questions.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-10">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-12 h-12 rounded-xl bg-indigo-500/20 flex items-center justify-center">
            <BookOpen className="w-6 h-6 text-indigo-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">Interview Preparation</h1>
            <p className="text-slate-400 text-sm">
              Generate personalized questions using your resume and Job Description.
            </p>
          </div>
        </div>
      </div>

      {!resumeData && !currentResume?.id ? (
        <div className="glass-card rounded-2xl p-8 text-center">
          <AlertCircle className="w-10 h-10 text-amber-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-white mb-2">Resume Required</h2>
          <p className="text-slate-400 mb-5">
            Upload and parse your resume first to prepare personalized interview questions.
          </p>
          <Link
            to="/upload"
            className="inline-flex items-center gap-2 px-5 py-3 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium"
          >
            <Sparkles className="w-4 h-4" />
            Upload Resume
          </Link>
        </div>
      ) : (
        <>
          <div className="glass-card rounded-2xl p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-white">Your Resume</h2>
              <span className="text-xs px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Resume Available
              </span>
            </div>

            <p className="text-slate-300">
              {currentResume?.title || resumeData?.name || 'Uploaded Resume'}
            </p>

            <label className="block text-sm font-medium text-slate-300 mt-6 mb-2">
              Job Description
            </label>

            <textarea
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              rows={8}
              placeholder="Paste the job description here..."
              className="w-full rounded-xl bg-slate-900/70 border border-slate-700 p-4 text-slate-200 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-y"
            />

            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mt-4">
              <p className="text-xs text-slate-500">
                The generator creates 5 technical and 3 behavioral questions.
              </p>

              <button
                onClick={handleGenerate}
                disabled={loading}
                className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-50 text-white font-semibold transition"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Generate Questions
                  </>
                )}
              </button>
            </div>
          </div>

          {error && (
            <div className="mb-6 p-4 rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-300">
              {error}
            </div>
          )}

          {questions && (
            <div className="space-y-8">
              <QuestionSection
                title="Technical Questions"
                subtitle="5 questions based on your resume and the target role"
                items={questions.technical_questions}
                color="indigo"
              />

              <QuestionSection
                title="Behavioral Questions"
                subtitle="3 questions based on your experience"
                items={questions.behavioral_questions}
                color="purple"
              />

              <button
                onClick={handleGenerate}
                disabled={loading}
                className="inline-flex items-center gap-2 px-5 py-3 rounded-lg border border-slate-700 text-slate-300 hover:bg-slate-800"
              >
                <RefreshCw className="w-4 h-4" />
                Generate Again
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function QuestionSection({ title, subtitle, items = [], color }) {
  return (
    <section>
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-white">{title}</h2>
        <p className="text-sm text-slate-400 mt-1">{subtitle}</p>
      </div>

      <div className="space-y-4">
        {items.map((item, index) => (
          <article
            key={`${title}-${index}`}
            className="glass-card rounded-2xl p-5 sm:p-6"
          >
            <div className="flex items-start gap-3">
              <span className={`flex-shrink-0 w-8 h-8 rounded-lg bg-${color}-500/20 text-${color}-300 flex items-center justify-center font-semibold text-sm`}>
                {index + 1}
              </span>

              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-semibold text-white">
                  {item.question}
                </h3>

                <div className="mt-5">
                  <h4 className="text-sm font-semibold text-emerald-400 mb-2">
                    Suggested Answer
                  </h4>
                  <p className="text-slate-300 text-sm leading-7 whitespace-pre-line">
                    {item.suggested_answer}
                  </p>
                </div>

                <div className="mt-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                  <h4 className="text-sm font-semibold text-amber-400 mb-2">
                    Preparation Tips
                  </h4>
                  <p className="text-sm text-slate-300 leading-6 whitespace-pre-line">
                    {item.tips}
                  </p>
                </div>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
