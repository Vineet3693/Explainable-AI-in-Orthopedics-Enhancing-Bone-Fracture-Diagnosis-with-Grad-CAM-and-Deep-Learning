import axios from 'axios';
import type { PredictionResult, QAMessage } from '@types/index';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor for auth token
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Handle unauthorized
            localStorage.removeItem('authToken');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export const apiService = {
    // Prediction endpoints
    async predictImage(file: File): Promise<PredictionResult> {
        const formData = new FormData();
        formData.append('file', file);

        const { data } = await api.post('/api/v1/predict', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return data;
    },

    async validateImage(file: File): Promise<{ valid: boolean; message?: string }> {
        const formData = new FormData();
        formData.append('file', file);

        const { data } = await api.post('/api/v1/validate/image', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return data;
    },

    // Report endpoints
    async generateReport(predictionId: string): Promise<{ reportUrl: string }> {
        const { data } = await api.post('/api/v1/reports/generate', { predictionId });
        return data;
    },

    async getReport(reportId: string): Promise<Blob> {
        const { data } = await api.get(`/api/v1/reports/${reportId}`, {
            responseType: 'blob',
        });
        return data;
    },

    // Q&A endpoints
    async askQuestion(question: string, context?: string): Promise<QAMessage> {
        const { data } = await api.post('/api/v1/qa/ask', { question, context });
        return data;
    },

    // History endpoints
    async getHistory(limit = 50): Promise<any[]> {
        const { data } = await api.get('/api/v1/history', { params: { limit } });
        return data;
    },

    async getHistoryItem(id: string): Promise<any> {
        const { data } = await api.get(`/api/v1/history/${id}`);
        return data;
    },

    // Health check
    async healthCheck(): Promise<{ status: string }> {
        const { data } = await api.get('/api/v1/health');
        return data;
    },
};

export default api;
