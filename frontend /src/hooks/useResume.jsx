import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

const ResumeContext = createContext(null);

export function ResumeProvider({ children }) {
  const [currentResume, setCurrentResume] = useState(() => {
    const saved = localStorage.getItem('currentResume');
    return saved ? JSON.parse(saved) : null;
  });

  const [currentJd, setCurrentJd] = useState(() => {
    return localStorage.getItem('currentJd') || '';
  });

  const [currentAnalysis, setCurrentAnalysis] = useState(() => {
    const saved = localStorage.getItem('currentAnalysis');
    return saved ? JSON.parse(saved) : null;
  });

  const [baseAtsScore, setBaseAtsScore] = useState(() => {
    const saved = localStorage.getItem('baseAtsScore');
    return saved ? JSON.parse(saved) : null;
  });

  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    if (currentResume) {
      localStorage.setItem('currentResume', JSON.stringify(currentResume));
    } else {
      localStorage.removeItem('currentResume');
    }
  }, [currentResume]);

  useEffect(() => {
    if (currentJd) {
      localStorage.setItem('currentJd', currentJd);
    } else {
      localStorage.removeItem('currentJd');
    }
  }, [currentJd]);

  useEffect(() => {
    if (currentAnalysis) {
      localStorage.setItem('currentAnalysis', JSON.stringify(currentAnalysis));
    } else {
      localStorage.removeItem('currentAnalysis');
    }
  }, [currentAnalysis]);

  useEffect(() => {
    if (baseAtsScore) {
      localStorage.setItem('baseAtsScore', JSON.stringify(baseAtsScore));
    } else {
      localStorage.removeItem('baseAtsScore');
    }
  }, [baseAtsScore]);

  const setResumeData = (resumeData, resumeId = null, title = 'Current Resume', baseScore = null) => {
    setCurrentResume({
      id: resumeId,
      title,
      data: resumeData,
    });
    if (baseScore) {
      setBaseAtsScore(baseScore);
    }
    // Reset previous JD and JD analysis so old results don't show on a newly uploaded resume
    setCurrentJd('');
    setCurrentAnalysis(null);
  };

  const refreshBaseScore = async (data = null, id = null) => {
    const resumeToScore = data || currentResume?.data;
    const targetId = id || currentResume?.id;
    if (resumeToScore) {
      try {
        const score = await api.getBaseAtsScore(targetId, resumeToScore);
        setBaseAtsScore(score);
        return score;
      } catch (err) {
        console.error('Failed to compute base ATS score:', err);
      }
    }
  };

  const updateStructuredResume = async (newData) => {
    if (currentResume?.id) {
      try {
        const res = await api.updateResume(currentResume.id, {
          title: currentResume.title,
          structured_data: newData,
        });
        setCurrentResume((prev) => ({
          ...prev,
          data: res.structured_data,
        }));
        return res;
      } catch (err) {
        console.error('Failed to sync resume to server:', err);
      }
    }
    // Update local state directly
    setCurrentResume((prev) => ({
      ...prev,
      data: newData,
    }));
  };

  return (
    <ResumeContext.Provider
      value={{
        currentResume,
        setCurrentResume,
        setResumeData,
        updateStructuredResume,
        currentJd,
        setCurrentJd,
        currentAnalysis,
        setCurrentAnalysis,
        baseAtsScore,
        setBaseAtsScore,
        refreshBaseScore,
        isAnalyzing,
        setIsAnalyzing,
      }}
    >
      {children}
    </ResumeContext.Provider>
  );
}

export function useResume() {
  const context = useContext(ResumeContext);
  if (!context) {
    throw new Error('useResume must be used within a ResumeProvider');
  }
  return context;
}
