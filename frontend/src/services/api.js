import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL,
});

// Interceptors for logging
api.interceptors.request.use(
    (config) => {
        console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
        return config;
    },
    (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
    }
);

api.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        console.error('API Response Error:', error.response || error.message);
        return Promise.reject(error);
    }
);

// Helpers
export const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

// API Services
export const systemAPI = {
    getHealth: () => api.get('/system/health'),
    getStats: () => api.get('/system/stats'),
};

export const documentAPI = {
    upload: (file, onProgress) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post('/documents/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            onUploadProgress: (progressEvent) => {
                if (onProgress) {
                    const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    onProgress(percentCompleted);
                }
            },
        });
    },
    list: () => api.get('/documents/list'),
    delete: (id) => api.delete(`/documents/${id}`),
};

export const queryAPI = {
    ask: (question, documentIds, conversationId) => api.post('/query/ask', {
        question,
        document_ids: documentIds?.length > 0 ? documentIds : null,
        conversation_id: conversationId || null,
    }),
};



export const observabilityAPI = {
    getMetrics: (windowHours = 24) => api.get(`/observability/metrics?window_hours=${windowHours}`),
    getLogs: (limit = 50) => api.get(`/observability/logs?limit=${limit}`),
    getPrompts: (templateKey) => api.get('/observability/prompts', { params: templateKey ? { template_key: templateKey } : {} }),
    createPromptVersion: (payload) => api.post('/observability/prompts', payload),
};

export default api;
