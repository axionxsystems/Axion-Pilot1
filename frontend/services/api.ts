
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export interface User {
    id: number;
    email: string;
    is_active: boolean;
    plan: string;
    created_at: string;
    is_admin: boolean;
    name?: string;
    mobile?: string;
    avatar_url?: string;
}

export interface ProjectRequest {
    api_key: string;
    ai_provider?: string;
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
    // ── Auth ────────────────────────────────────────────────────────────────

    // Step 1: Submit email + password → triggers OTP to be sent
    loginStep1: async (email: string, password: string) => {
        const formData = new URLSearchParams();
        formData.append('username', email);
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
        return res.json(); // { requires_otp: true, message: "..." }
    },

    // Step 2: Submit OTP → receives JWT access token
    loginStep2: async (email: string, otp: string) => {
        const res = await fetch(`${API_BASE_URL}/auth/login/verify-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, otp }),
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'OTP verification failed');
        }
        return res.json(); // { access_token, token_type }
    },

    forgotPassword: async (email: string) => {
        const res = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email }),
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Request failed');
        }
        return res.json();
    },

    resetPassword: async (email: string, otp: string, new_password: string) => {
        const res = await fetch(`${API_BASE_URL}/auth/reset-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, otp, new_password }),
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Password reset failed');
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

    verifySignup: async (email: string, emailOtp: string, mobileOtp: string) => {
        const res = await fetch(`${API_BASE_URL}/auth/verify-signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, email_otp: emailOtp, mobile_otp: mobileOtp }),
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Verification failed');
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

    logoutAllDevices: async () => {
        const res = await fetch(`${API_BASE_URL}/users/me/logout-all`, {
            method: 'POST',
            headers: authHeaders(),
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Logout from all devices failed');
        }
        return res.json();
    },

    deleteAccount: async () => {
        const res = await fetch(`${API_BASE_URL}/users/me`, {
            method: 'DELETE',
            headers: authHeaders(),
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Account deletion failed');
        }
        return res.json();
    },

    // ── Project ─────────────────────────────────────────────────────────────
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

    // ── Viva ────────────────────────────────────────────────────────────────
    chatViva: async (apiKey: string, history: any[], projectData: any) => {
        const response = await fetch(`${API_BASE_URL}/viva/ask`, {
            method: "POST",
            headers: authHeaders(), // Authentication REQUIRED now
            body: JSON.stringify({
                api_key: apiKey,
                messages: history,
                project_data: projectData
            }),
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || "Viva chat failed");
        }
        return response.json();
    },

    // ── Downloads ───────────────────────────────────────────────────────────
    downloadReport: async (projectId: number | string) => {
        const id = typeof projectId === 'object' ? (projectId as any).id : projectId;
        const response = await fetch(`${API_BASE_URL}/projects/download/report/${id}`, {
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Report download failed");
        return response.blob();
    },

    downloadPPT: async (projectId: number | string) => {
        const id = typeof projectId === 'object' ? (projectId as any).id : projectId;
        const response = await fetch(`${API_BASE_URL}/projects/download/ppt/${id}`, {
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("PPT download failed");
        return response.blob();
    },

    downloadCode: async (projectId: number | string) => {
        const id = typeof projectId === 'object' ? (projectId as any).id : projectId;
        const response = await fetch(`${API_BASE_URL}/projects/download/code/${id}`, {
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Failed to download code");
        return response.blob();
    },

    downloadFullProject: async (projectId: number | string) => {
        const id = typeof projectId === 'object' ? (projectId as any).id : projectId;
        const response = await fetch(`${API_BASE_URL}/projects/download/full/${id}`, {
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Failed to download full project");
        return response.blob();
    },

    // ── Admin ───────────────────────────────────────────────────────────────
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

    getAdminChartProjectsPerDay: async () => {
        const response = await fetch(`${API_BASE_URL}/admin/charts/projects-per-day`, {
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Failed to fetch chart data");
        return response.json();
    },

    getAdminChartProjectsPerDomain: async () => {
        const response = await fetch(`${API_BASE_URL}/admin/charts/projects-per-domain`, {
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Failed to fetch domain chart data");
        return response.json();
    },

    getAdminChartProjectsPerDifficulty: async () => {
        const response = await fetch(`${API_BASE_URL}/admin/charts/projects-per-difficulty`, {
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Failed to fetch difficulty chart data");
        return response.json();
    },

    getAdminModerationProjects: async (status: string) => {
        const response = await fetch(`${API_BASE_URL}/admin/moderation?status=${status}`, {
            headers: authHeaders(),
        });
        if (!response.ok) throw new Error("Failed to fetch moderation projects");
        return response.json();
    },

    updateAdminProjectStatus: async (projectId: number, status: string) => {
        const response = await fetch(`${API_BASE_URL}/admin/projects/${projectId}/status`, {
            method: "PUT",
            headers: authHeaders(),
            body: JSON.stringify({ status }),
        });
        if (!response.ok) throw new Error("Failed to update project status");
        return response.json();
    },

    getPublicTemplates: async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/templates/public`, {
                headers: authHeaders(),
            });
            if (!response.ok) return [];
            return response.json();
        } catch {
            return [];
        }
    },

    // ── Admin Infrastructure ────────────────────────────────────────────────
    getInfrastructureStatus: async () => {
        const response = await fetch(`${API_BASE_URL}/admin/infrastructure/status`, {
            headers: authHeaders(),
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to fetch infrastructure status");
        }
        return response.json();
    },

    updateInfrastructureConfig: async (serviceId: string, config: any) => {
        const response = await fetch(`${API_BASE_URL}/admin/infrastructure/config`, {
            method: 'PUT',
            headers: authHeaders(),
            body: JSON.stringify({ service_id: serviceId, config }),
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to update configuration");
        }
        return response.json();
    },

    rotateServiceKeys: async (serviceId: string) => {
        const response = await fetch(`${API_BASE_URL}/admin/infrastructure/rotate`, {
            method: 'POST',
            headers: authHeaders(),
            body: JSON.stringify({ service_id: serviceId }),
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Rotation failed");
        }
        return response.json();
    },
};
