import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useResume } from '../hooks/useResume';
import { useToast } from '../components/Toast';
import { api } from '../services/api';
import { 
  Save, 
  Download, 
  Plus, 
  Trash2, 
  User, 
  Briefcase, 
  GraduationCap, 
  Code, 
  Award, 
  Layers, 
  Loader2,
  Check,
  FileText
} from 'lucide-react';

export default function EditorPage() {
  const navigate = useNavigate();
  const { currentResume, updateStructuredResume } = useResume();
  const { addToast } = useToast();

  const [formData, setFormData] = useState(() => {
    return currentResume?.data || {
      name: '',
      email: '',
      phone: '',
      location: '',
      summary: '',
      skills: [],
      experience: [],
      education: [],
      projects: [],
      certifications: [],
      achievements: [],
      links: [],
    };
  });

  const [newSkill, setNewSkill] = useState('');
  const [newCert, setNewCert] = useState('');
  const [newLink, setNewLink] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  const handleFieldChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  // Skill management
  const addSkill = () => {
    if (newSkill.trim() && !formData.skills.includes(newSkill.trim())) {
      setFormData((prev) => ({ ...prev, skills: [...prev.skills, newSkill.trim()] }));
      setNewSkill('');
    }
  };

  const removeSkill = (skillToRemove) => {
    setFormData((prev) => ({
      ...prev,
      skills: prev.skills.filter((s) => s !== skillToRemove),
    }));
  };

  // Experience management
  const addExperience = () => {
    const newItem = {
      title: 'Software Engineer',
      company: 'Tech Company',
      location: 'City, State',
      start_date: '2022',
      end_date: 'Present',
      highlights: ['Developed key features and improved test coverage.'],
    };
    setFormData((prev) => ({ ...prev, experience: [newItem, ...prev.experience] }));
  };

  const updateExperienceItem = (index, field, value) => {
    const updated = [...formData.experience];
    updated[index][field] = value;
    setFormData((prev) => ({ ...prev, experience: updated }));
  };

  const removeExperience = (index) => {
    setFormData((prev) => ({
      ...prev,
      experience: prev.experience.filter((_, i) => i !== index),
    }));
  };

  const addExperienceHighlight = (expIdx) => {
    const updated = [...formData.experience];
    updated[expIdx].highlights.push('Accomplished a key objective with high quality.');
    setFormData((prev) => ({ ...prev, experience: updated }));
  };

  const updateExperienceHighlight = (expIdx, hlIdx, value) => {
    const updated = [...formData.experience];
    updated[expIdx].highlights[hlIdx] = value;
    setFormData((prev) => ({ ...prev, experience: updated }));
  };

  const removeExperienceHighlight = (expIdx, hlIdx) => {
    const updated = [...formData.experience];
    updated[expIdx].highlights = updated[expIdx].highlights.filter((_, i) => i !== hlIdx);
    setFormData((prev) => ({ ...prev, experience: updated }));
  };

  // Education management
  const addEducation = () => {
    const newItem = {
      degree: 'B.S. in Computer Science',
      institution: 'University Name',
      location: '',
      graduation_year: '2023',
      gpa: '3.8',
    };
    setFormData((prev) => ({ ...prev, education: [...prev.education, newItem] }));
  };

  const updateEducationItem = (index, field, value) => {
    const updated = [...formData.education];
    updated[index][field] = value;
    setFormData((prev) => ({ ...prev, education: updated }));
  };

  const removeEducation = (index) => {
    setFormData((prev) => ({
      ...prev,
      education: prev.education.filter((_, i) => i !== index),
    }));
  };

  const [selectedTemplate, setSelectedTemplate] = useState('classic_ats');

  // Save changes
  const handleSave = async () => {
    setIsSaving(true);
    try {
      await updateStructuredResume(formData);
      addToast('Resume changes saved and version updated!', 'success');
    } catch (err) {
      addToast(`Error saving resume: ${err.message}`, 'error');
    } finally {
      setIsSaving(false);
    }
  };

  // Download PDF
  const handleDownloadPdf = async () => {
    if (!currentResume?.id) {
      addToast('Please upload or save the resume to the database first.', 'error');
      return;
    }
    setIsExporting(true);
    try {
      // First persist any current edits
      await updateStructuredResume(formData);
      await api.downloadResumePdf(
        currentResume.id,
        `${formData.name.replace(' ', '_') || 'Resume'}_${selectedTemplate}.pdf`,
        selectedTemplate
      );
      addToast(`ATS PDF (${selectedTemplate}) generated and downloaded!`, 'success');
    } catch (err) {
      addToast(`PDF error: ${err.message}`, 'error');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto py-10 px-4 space-y-8">
      {/* Header and Action Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            ATS Resume Builder & Editor
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Tailor, verify, and export your machine-readable resume without blackbox alterations
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5 w-full sm:w-auto">
          <select
            value={selectedTemplate}
            onChange={(e) => setSelectedTemplate(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-xs text-indigo-300 font-semibold rounded-xl px-3 py-2.5 focus:outline-hidden focus:border-indigo-500 cursor-pointer shadow-xs"
          >
            <option value="classic_ats">Template: Classic ATS (Standard)</option>
            <option value="modern_tech">Template: Modern Tech (Indigo)</option>
            <option value="executive">Template: Executive (Navy Serif)</option>
          </select>

          <button
            onClick={handleSave}
            disabled={isSaving}
            className="flex items-center justify-center space-x-1.5 px-3.5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-all shadow-md shadow-indigo-600/20"
          >
            {isSaving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
            <span>Save</span>
          </button>

          <button
            onClick={handleDownloadPdf}
            disabled={isExporting}
            className="flex items-center justify-center space-x-1.5 px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-all shadow-lg shadow-emerald-600/25"
          >
            {isExporting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />}
            <span>Export PDF</span>
          </button>
        </div>
      </div>

      {/* Editor Sections */}
      <div className="space-y-6">
        {/* 1. Personal Information */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center space-x-2 border-b border-slate-800/80 pb-3">
            <User className="w-4 h-4 text-indigo-400" />
            <h3 className="text-sm font-bold text-white">Personal Contact Details</h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-slate-400 mb-1 font-medium">Full Name</label>
              <input
                type="text"
                value={formData.name || ''}
                onChange={(e) => handleFieldChange('name', e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-hidden focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-slate-400 mb-1 font-medium">Email Address</label>
              <input
                type="email"
                value={formData.email || ''}
                onChange={(e) => handleFieldChange('email', e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-hidden focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-slate-400 mb-1 font-medium">Phone Number</label>
              <input
                type="text"
                value={formData.phone || ''}
                onChange={(e) => handleFieldChange('phone', e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-hidden focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-slate-400 mb-1 font-medium">Location (City, State / Country)</label>
              <input
                type="text"
                value={formData.location || ''}
                onChange={(e) => handleFieldChange('location', e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-hidden focus:border-indigo-500"
              />
            </div>
          </div>
        </div>

        {/* 2. Professional Summary */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center space-x-2 border-b border-slate-800/80 pb-3">
            <FileText className="w-4 h-4 text-indigo-400" />
            <h3 className="text-sm font-bold text-white">Professional Summary / Objective</h3>
          </div>
          <textarea
            rows={4}
            value={formData.summary || ''}
            onChange={(e) => handleFieldChange('summary', e.target.value)}
            placeholder="Write a concise overview of your technical background..."
            className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3.5 text-xs text-white focus:outline-hidden focus:border-indigo-500 leading-relaxed font-sans"
          />
        </div>

        {/* 3. Technical Skills */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center space-x-2 border-b border-slate-800/80 pb-3">
            <Code className="w-4 h-4 text-indigo-400" />
            <h3 className="text-sm font-bold text-white">Technical Skills</h3>
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="text"
              placeholder="Add skill (e.g. Docker, TypeScript, PostgreSQL)"
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
              className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-hidden focus:border-indigo-500"
            />
            <button
              onClick={addSkill}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center space-x-1"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add</span>
            </button>
          </div>

          <div className="flex flex-wrap gap-2 pt-2">
            {formData.skills.map((skill) => (
              <span
                key={skill}
                className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-lg text-xs font-medium bg-indigo-500/10 border border-indigo-500/20 text-indigo-300"
              >
                <span>{skill}</span>
                <button
                  onClick={() => removeSkill(skill)}
                  className="text-indigo-400 hover:text-rose-400 transition-colors ml-1"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* 4. Professional Experience */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <div className="flex items-center space-x-2">
              <Briefcase className="w-4 h-4 text-indigo-400" />
              <h3 className="text-sm font-bold text-white">Work Experience</h3>
            </div>
            <button
              onClick={addExperience}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 text-xs font-semibold transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Position</span>
            </button>
          </div>

          <div className="space-y-6">
            {formData.experience.map((exp, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-3"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-indigo-400">Position #{idx + 1}</span>
                  <button
                    onClick={() => removeExperience(idx)}
                    className="text-slate-400 hover:text-rose-400 p-1"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <input
                    type="text"
                    placeholder="Job Title"
                    value={exp.title}
                    onChange={(e) => updateExperienceItem(idx, 'title', e.target.value)}
                    className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white"
                  />
                  <input
                    type="text"
                    placeholder="Company Name"
                    value={exp.company}
                    onChange={(e) => updateExperienceItem(idx, 'company', e.target.value)}
                    className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white"
                  />
                  <input
                    type="text"
                    placeholder="Start Date"
                    value={exp.start_date || ''}
                    onChange={(e) => updateExperienceItem(idx, 'start_date', e.target.value)}
                    className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white"
                  />
                  <input
                    type="text"
                    placeholder="End Date (or Present)"
                    value={exp.end_date || ''}
                    onChange={(e) => updateExperienceItem(idx, 'end_date', e.target.value)}
                    className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white"
                  />
                </div>

                {/* Bullets */}
                <div className="space-y-2 pt-2">
                  <div className="flex items-center justify-between">
                    <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                      Key Highlights & Accomplishments
                    </label>
                    <button
                      onClick={() => addExperienceHighlight(idx)}
                      className="text-[11px] text-indigo-400 hover:underline flex items-center space-x-1"
                    >
                      <Plus className="w-3 h-3" />
                      <span>Add Bullet</span>
                    </button>
                  </div>

                  {exp.highlights?.map((hl, hlIdx) => (
                    <div key={hlIdx} className="flex items-center space-x-2">
                      <input
                        type="text"
                        value={hl}
                        onChange={(e) => updateExperienceHighlight(idx, hlIdx, e.target.value)}
                        className="flex-1 bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200"
                      />
                      <button
                        onClick={() => removeExperienceHighlight(idx, hlIdx)}
                        className="text-slate-500 hover:text-rose-400 p-1"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 5. Education */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <div className="flex items-center space-x-2">
              <GraduationCap className="w-4 h-4 text-indigo-400" />
              <h3 className="text-sm font-bold text-white">Education</h3>
            </div>
            <button
              onClick={addEducation}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 text-xs font-semibold transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Degree</span>
            </button>
          </div>

          <div className="space-y-4">
            {formData.education.map((edu, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-3"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-indigo-400">Education #{idx + 1}</span>
                  <button
                    onClick={() => removeEducation(idx)}
                    className="text-slate-400 hover:text-rose-400 p-1"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <input
                    type="text"
                    placeholder="Degree / Program"
                    value={edu.degree}
                    onChange={(e) => updateEducationItem(idx, 'degree', e.target.value)}
                    className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white"
                  />
                  <input
                    type="text"
                    placeholder="Institution / University"
                    value={edu.institution}
                    onChange={(e) => updateEducationItem(idx, 'institution', e.target.value)}
                    className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white"
                  />
                  <input
                    type="text"
                    placeholder="Graduation Year"
                    value={edu.graduation_year || ''}
                    onChange={(e) => updateEducationItem(idx, 'graduation_year', e.target.value)}
                    className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white"
                  />
                  <input
                    type="text"
                    placeholder="GPA / Honors (Optional)"
                    value={edu.gpa || ''}
                    onChange={(e) => updateEducationItem(idx, 'gpa', e.target.value)}
                    className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
