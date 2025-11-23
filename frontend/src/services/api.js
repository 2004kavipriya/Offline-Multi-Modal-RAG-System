/**
 * API service for communicating with the backend
 */

import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * Upload a file
 */
export const uploadFile = async (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/upload/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
            if (onProgress) {
                const percentCompleted = Math.round(
                    (progressEvent.loaded * 100) / progressEvent.total
                );
                onProgress(percentCompleted);
            }
        },
    });

    return response.data;
};

/**
 * Upload multiple files
 */
export const uploadMultipleFiles = async (files, onProgress) => {
    const formData = new FormData();
    files.forEach((file) => {
        formData.append('files', file);
    });

    const response = await api.post('/upload/batch', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
            if (onProgress) {
                const percentCompleted = Math.round(
                    (progressEvent.loaded * 100) / progressEvent.total
                );
                onProgress(percentCompleted);
            }
        },
    });

    return response.data;
};

/**
 * Perform semantic search
 */
export const search = async (query, documentTypes = null, topK = 5) => {
    const response = await api.post('/search/', {
        query,
        document_types: documentTypes,
        top_k: topK,
    });

    return response.data;
};

/**
 * Perform cross-modal search
 */
export const crossModalSearch = async (query, topK = 5) => {
    const response = await api.post('/search/cross-modal', {
        query,
        top_k: topK,
    });

    return response.data;
};

/**
 * Perform RAG query
 */
export const ragQuery = async (query, documentTypes = null, topK = 5) => {
    const response = await api.post('/query/', {
        query,
        document_types: documentTypes,
        top_k: topK,
    });

    return response.data;
};

/**
 * Check system health
 */
export const checkHealth = async () => {
    const response = await api.get('/health');
    return response.data;
};

/**
 * Check LLM health
 */
export const checkLLMHealth = async () => {
    const response = await api.get('/query/health');
    return response.data;
};

/**
 * Get all uploaded documents
 */
export const getDocuments = async () => {
    const response = await api.get('/documents/');
    return response.data;
};

/**
 * Get a specific document by ID
 */
export const getDocument = async (documentId) => {
    const response = await api.get(`/documents/${documentId}`);
    return response.data;
};

/**
 * Delete a document by ID
 */
export const deleteDocument = async (documentId) => {
    const response = await api.delete(`/documents/${documentId}`);
    return response.data;
};

export default api;
