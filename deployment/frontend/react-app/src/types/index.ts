/**
 * Type definitions for Fracture Detection AI
 */

export interface PredictionResult {
    prediction: 'fracture' | 'normal';
    confidence: number;
    fractureType?: string;
    location?: string;
    severity?: 'mild' | 'moderate' | 'severe';
    gradcamUrl?: string;
    timestamp: string;
}

export interface AnalysisHistory {
    id: string;
    imageUrl: string;
    result: PredictionResult;
    createdAt: string;
    patientId?: string;
}

export interface QAMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
}

export interface User {
    id: string;
    email: string;
    name: string;
    role: 'doctor' | 'radiologist' | 'admin';
}

export interface UploadProgress {
    progress: number;
    status: 'idle' | 'uploading' | 'processing' | 'complete' | 'error';
    error?: string;
}
