import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import UploadPage from './pages/UploadPage';
import AnalysisPage from './pages/AnalysisPage';
import EditorPage from './pages/EditorPage';
import HistoryPage from './pages/HistoryPage';
import InterviewPrepPage from './pages/InterviewPrepPage';
import { ResumeProvider } from './hooks/useResume';
import { ToastProvider } from './components/Toast';

export default function App() {
  return (
    <ToastProvider>
      <ResumeProvider>
        <Router>
          <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100">
            <Navbar />
            <main className="flex-1">
              <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/upload" element={<UploadPage />} />
                <Route path="/analysis" element={<AnalysisPage />} />
                <Route path="/editor" element={<EditorPage />} />
                <Route path="/history" element={<HistoryPage />} />
                <Route path="/interview-prep" element={<InterviewPrepPage />} />
              </Routes>
            </main>
            <Footer />
          </div>
        </Router>
      </ResumeProvider>
    </ToastProvider>
  );
}
