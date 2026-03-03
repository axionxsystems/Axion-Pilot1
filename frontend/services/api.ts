
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

export interface User {
    id: number;
    email: string;
    is_active: boolean;
    plan: string;
    created_at: string;
    name?: string;
    avatar_url?: string;
}

export interface ProjectRequest {
    api_key: string;
    domain: string;
    topic?: string;
    difficulty: string;
    tech_stack: string;
    year: string;
}

// Helper to get token
const getToken = () => typeof window !== 'undefined' ? localStorage.getItem('token') : null;

const authHeaders = () => ({
    "Content-Type": "application/json",
    "Authorization": `Bearer ${getToken()}`
})

export const api = {
    // Auth
    login: async (username: string, password: string) => {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const res = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData,
        });
        if (!res.ok) throw new Error('Login failed');
        return res.json();
    },

    signup: async (email: string, password: string) => {
        const res = await fetch(`${API_BASE_URL}/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Signup failed');
        }
        return res.json();
    },

    getMe: async () => {
        const res = await fetch(`${API_BASE_URL}/users/me`, {
            headers: authHeaders(),
        });
        if (!res.ok) throw new Error('Not authorized');
        return res.json();
    },

    updatePassword: async (currentPassword: string, newPassword: string) => {
        const res = await fetch(`${API_BASE_URL}/users/me/password`, {
            method: 'PUT',
            headers: authHeaders(),
            body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Password update failed');
        }
        return res.json();
    },

    // Project
    generateProject: async (data: ProjectRequest) => {
        const response = await fetch(`${API_BASE_URL}/projects/generate`, {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Generation failed");
        }
        return response.json();
    },

    // Viva
    chatViva: async (apiKey: string, history: any[], projectData: any) => {
        const response = await fetch(`${API_BASE_URL}/viva/ask`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                api_key: apiKey,
                messages: history,
                project_data: projectData
            }),
        });
        if (!response.ok) throw new Error("Viva chat failed");
        return response.json();
    },

    // Downloads
    downloadReport: async (projectData: any) => {
        const response = await fetch(`${API_BASE_URL}/projects/download/report`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(projectData),
        });
        if (!response.ok) throw new Error("Report download failed");
        return response.blob();
    },

    downloadPPT: async (projectData: any) => {
        const response = await fetch(`${API_BASE_URL}/projects/download/ppt`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(projectData),
        });
        if (!response.ok) throw new Error("PPT download failed");
        return response.blob();
    },

    downloadCode: async (projectData: any) => {
        const response = await fetch(`${API_BASE_URL}/projects/download/code`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(projectData),
        });
        if (!response.ok) throw new Error("Code download failed");
        return response.blob();
    }
};
