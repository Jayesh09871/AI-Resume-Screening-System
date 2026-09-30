import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000,
});

// Interceptor for friendly error messages
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.message ||
      'An unexpected error occurred with the server.';
    return Promise.reject(new Error(message));
  }
);

export const api = {
  // Health
  checkHealth: async () => {
    const res = await apiClient.get('/health');
    return res.data;
  },

  // Resumes
  uploadResume: async (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post('/resumes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
    return res.data;
  },

  getResume: async (id) => {
    const res = await apiClient.get(`/resumes/${id}`);
    return res.data;
  },

  updateResume: async (id, payload) => {
    const res = await apiClient.put(`/resumes/${id}`, payload);
    return res.data;
  },

  deleteResume: async (id) => {
    const res = await apiClient.delete(`/resumes/${id}`);
    return res.data;
  },

  getBaseAtsScore: async (resumeId, resumeData = null) => {
    if (resumeId) {
      const res = await apiClient.get(`/resumes/${resumeId}/base-score`);
      return res.data;
    } else if (resumeData) {
      const res = await apiClient.post('/resumes/base-score', resumeData);
      return res.data;
    }
  },

  downloadResumePdf: async (id, filename = 'resume.pdf', template = 'classic_ats') => {
    const response = await apiClient.post(`/resumes/${id}/pdf?template=${template}`, null, {
      responseType: 'blob',
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },

  // Analysis
  analyzeResume: async ({ resumeId, resumeData, jdText }) => {
    const payload = {
      resume_id: resumeId || null,
      resume_data: resumeData || null,
      jd_text: jdText,
    };
    const res = await apiClient.post('/analyze', payload);
    return res.data;
  },

  improveBullet: async (bulletText, targetRole = '', context = '') => {
    const res = await apiClient.post('/improve', {
      bullet_text: bulletText,
      target_role: targetRole,
      context,
    });
    return res.data;
  },

  getAnalysis: async (id) => {
    const res = await apiClient.get(`/analyses/${id}`);
    return res.data;
  },

  scrapeJobDescription: async (url) => {
    const res = await apiClient.post('/scrape-jd', { url });
    return res.data;
  },

   // Interview Preparation
generateInterviewPrep: async (payload) => {
    const response = await apiClient.post(
        '/interview-prep',
        payload,
        { timeout: 120000 }
    );

    return response.data;
},

  // History
  getHistory: async () => {
    const res = await apiClient.get('/history');
    return res.data;
  },

  deleteHistoryItem: async (id) => {
    const res = await apiClient.delete(`/history/${id}`);
    return res.data;
  },
};

console.log("API MODULE LOADED:", Object.keys(api));
console.log("INTERVIEW PREP METHOD:", typeof api.generateInterviewPrep);
export default api;
