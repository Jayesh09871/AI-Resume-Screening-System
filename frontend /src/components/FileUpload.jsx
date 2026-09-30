import React, { useState, useRef } from 'react';
import { 
  UploadCloud, 
  FileText, 
  AlertCircle, 
  CheckCircle2, 
  Loader2, 
  FileCheck,
  FileCode,
  Layers
} from 'lucide-react';
import { api } from '../services/api';
import { useToast } from './Toast';

export default function FileUpload({ onUploadComplete }) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [fileDetails, setFileDetails] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const fileInputRef = useRef(null);
  const { addToast } = useToast();

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const validateClientSide = (file) => {
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!['pdf', 'docx'].includes(ext)) {
      throw new Error(`File format .${ext} is unsupported. Please upload a PDF or DOCX file.`);
    }
    const maxBytes = 10 * 1024 * 1024; // 10MB
    if (file.size > maxBytes) {
      throw new Error(`File size is ${Math.round(file.size / (1024 * 1024))}MB. Limit is 10MB.`);
    }
    if (file.size === 0) {
      throw new Error('The selected file is empty (0 bytes).');
    }
  };

  const processFile = async (file) => {
    setErrorMsg('');
    try {
      validateClientSide(file);
    } catch (err) {
      setErrorMsg(err.message);
      addToast(err.message, 'error');
      return;
    }

    setFileDetails({
      name: file.name,
      size: `${(file.size / 1024).toFixed(1)} KB`,
      type: file.name.endsWith('.pdf') ? 'PDF' : 'DOCX',
    });

    setIsUploading(true);
    setUploadProgress(10);

    try {
      const response = await api.uploadResume(file, (progressEvent) => {
        const percent = Math.round((progressEvent.loaded * 90) / progressEvent.total);
        setUploadProgress(percent);
      });

      setUploadProgress(100);
      addToast('Resume uploaded and parsed successfully!', 'success');
      if (onUploadComplete) {
        onUploadComplete(response);
      }
    } catch (err) {
      setErrorMsg(err.message);
      addToast(`Upload failed: ${err.message}`, 'error');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  return (
    <div className="w-full space-y-4">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative cursor-pointer rounded-2xl border-2 border-dashed p-8 sm:p-12 text-center transition-all duration-200 ${
          isDragging
            ? 'border-indigo-500 bg-indigo-500/10 scale-[1.01]'
            : 'border-slate-700/80 bg-slate-900/40 hover:border-slate-500 hover:bg-slate-900/60'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          onChange={handleFileSelect}
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform">
            {isUploading ? (
              <Loader2 className="w-8 h-8 animate-spin" />
            ) : (
              <UploadCloud className="w-8 h-8" />
            )}
          </div>

          <div>
            <h3 className="text-base font-semibold text-white">
              {isUploading ? 'Extracting Resume Data...' : 'Drop your resume here or browse files'}
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Supports ATS-friendly PDF and Word DOCX (up to 10MB)
            </p>
          </div>

          {/* Supported tags */}
          <div className="flex items-center space-x-2 text-[11px] text-slate-400">
            <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono">
              .PDF (PyMuPDF)
            </span>
            <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono">
              .DOCX (python-docx)
            </span>
          </div>

          {/* Upload Progress Bar */}
          {isUploading && (
            <div className="w-full max-w-xs space-y-1.5 pt-2">
              <div className="flex justify-between text-xs font-semibold text-slate-300">
                <span>Parsing sections & metadata...</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Error message */}
      {errorMsg && (
        <div className="flex items-start space-x-2.5 p-3.5 rounded-xl bg-rose-950/60 border border-rose-500/30 text-rose-200 text-xs">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          <span>{errorMsg}</span>
        </div>
      )}
    </div>
  );
}
