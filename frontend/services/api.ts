
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export interface User {
    id: number;
    email: string;
    is_active: boolean;
    plan: string;
    created_at: string;
    is_admin: boolean;
    name?: string;
    avatar_url?: string;
}

export interface ProjectRequest {
    api_key: string;
    domain: string;
    topic?: string;
    description?: string;
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
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Login failed');
        }
        return res.json();
    },

    signup: async (email: string, password: string, full_name?: string, mobile?: string) => {
        const res = await fetch(`${API_BASE_URL}/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, full_name, mobile }),
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

    updateProfile: async (name: string) => {
        const res = await fetch(`${API_BASE_URL}/users/me`, {
            method: 'PUT',
            headers: authHeaders(),
            body: JSON.stringify({ name }),
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Profile update failed');
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

    getUserStats: async () => {
        const response = await fetch(`${API_BASE_URL}/projects/stats`, {
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Failed to fetch user stats");
        return response.json();
    },

    getProjectById: async (projectId: number) => {
        const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Failed to fetch project details");
        return response.json();
    },

    listProjects: async () => {
        const response = await fetch(`${API_BASE_URL}/projects/list`, {
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Failed to fetch projects");
        return response.json();
    },

    deleteProject: async (projectId: number) => {
        const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
            method: "DELETE",
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Failed to delete project");
        return response.json();
    },

    updateProject: async (projectId: number, updates: any) => {
        const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
            method: "PUT",
            headers: authHeaders(),
            body: JSON.stringify(updates),
        });
        if (!response.ok) throw new Error("Failed to update project");
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
            headers: authHeaders(),
            body: JSON.stringify(projectData),
        });
        if (!response.ok) throw new Error("Failed to download code");
        return response.blob();
    },

    downloadFullProject: async (projectData: any) => {
        const response = await fetch(`${API_BASE_URL}/projects/download/full`, {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify(projectData),
        });
        if (!response.ok) throw new Error("Failed to download full project");
        return response.blob();
    },

    // Admin Projects
    getAdminStats: async () => {
        const response = await fetch(`${API_BASE_URL}/admin/stats`, {
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Admin stats failed");
        return response.json();
    },

    getAdminActivity: async () => {
        const response = await fetch(`${API_BASE_URL}/admin/activity`, {
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Admin activity failed");
        return response.json();
    },

    getAdminChartProjectsPerDay: async () => {
        const response = await fetch(`${API_BASE_URL}/admin/charts/projects-per-day`, {
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Chart failed");
        return response.json();
    },

    getAdminChartProjectsPerDomain: async () => {
        const response = await fetch(`${API_BASE_URL}/admin/charts/projects-per-domain`, {
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Chart failed");
        return response.json();
    },

    getAdminChartProjectsPerDifficulty: async () => {
        const response = await fetch(`${API_BASE_URL}/admin/charts/projects-per-difficulty`, {
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Chart failed");
        return response.json();
    },

    // User Management
    adminListUsers: async () => {
        const response = await fetch(`${API_BASE_URL}/admin/users`, {
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Failed to fetch users");
        return response.json();
    },

    adminToggleUserStatus: async (userId: number) => {
        const response = await fetch(`${API_BASE_URL}/admin/users/${userId}/toggle-status`, {
            method: "POST",
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Failed to update status");
        return response.json();
    },

    adminDeleteUser: async (userId: number) => {
        const response = await fetch(`${API_BASE_URL}/admin/users/${userId}`, {
            method: "DELETE",
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Failed to delete user");
        return response.json();
    },

    // Global Project Monitoring
    adminListAllProjects: async () => {
        const response = await fetch(`${API_BASE_URL}/admin/projects`, {
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Failed to fetch all projects");
        return response.json();
    },

    adminDeleteProject: async (projectId: number) => {
        const response = await fetch(`${API_BASE_URL}/admin/projects/${projectId}`, {
            method: "DELETE",
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Failed to delete project");
        return response.json();
    },

    getPublicTemplates: async () => {
        const response = await fetch(`${API_BASE_URL}/projects/templates`, {
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Failed to fetch templates");
        return response.json();
    },

    // AI Settings
    getAdminAISettings: async () => {
        const response = await fetch(`${API_BASE_URL}/admin/settings/ai`, {
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Failed to fetch AI settings");
        return response.json();
    },

    updateAdminAISettings: async (config: any) => {
        const response = await fetch(`${API_BASE_URL}/admin/settings/ai`, {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify(config),
        });
        if (!response.ok) throw new Error("Failed to update AI settings");
        return response.json();
    },

    // Template Manager
    adminListTemplates: async () => {
        const response = await fetch(`${API_BASE_URL}/admin/templates`, {
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Failed to fetch templates");
        return response.json();
    },

    adminCreateTemplate: async (data: any) => {
        const response = await fetch(`${API_BASE_URL}/admin/templates`, {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error("Failed to create template");
        return response.json();
    },

    adminDeleteTemplate: async (templateId: number) => {
        const response = await fetch(`${API_BASE_URL}/admin/templates/${templateId}`, {
            method: "DELETE",
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Failed to delete template");
        return response.json();
    },

    // Moderation
    getAdminModerationProjects: async (status: string = "active") => {
        const response = await fetch(`${API_BASE_URL}/admin/moderation/projects?status=${status}`, {
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Failed to fetch flagged projects");
        return response.json();
    },

    updateAdminProjectStatus: async (projectId: number, status: string) => {
        const response = await fetch(`${API_BASE_URL}/admin/moderation/projects/${projectId}/status`, {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify({ status }),
        });
        if (!response.ok) throw new Error("Failed to update project status");
        return response.json();
    }
};
