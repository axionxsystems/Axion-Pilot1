"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, Branding, User } from "../services/api";

interface AuthContextType {
    user: User | null;
    branding: Branding | null;
    loading: boolean;
    loginStep1: (email: string, password: string) => Promise<{ requires_otp: boolean; message?: string }>;
    loginStep2: (email: string, otp: string) => Promise<void>;
    signup: (email: string, password: string, fullName: string, mobile?: string) => Promise<{ message?: string }>;
    verifySignup: (email: string, emailOtp: string, mobileOtp?: string) => Promise<void>;
    forgotPassword: (email: string) => Promise<{ message?: string }>;
    logout: () => void;
    refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({} as any);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [branding, setBranding] = useState<Branding | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    const updateBrandingStyles = (brandingData: Branding | null) => {
        if (typeof window === "undefined") return;
        const root = document.documentElement.style;
        root.setProperty("--brand-primary", brandingData?.primary_color || "#2563eb");
        root.setProperty("--brand-secondary", brandingData?.secondary_color || "#9333ea");
        root.setProperty("--brand-accent", brandingData?.accent_color || "#f97316");
    };

    const refreshUser = async () => {
        try {
            const userData = await api.getMe();
            setUser(userData);
            if (userData.org_id) {
                try {
                    const brandingData = await api.getOrgBranding(userData.org_id);
                    setBranding(brandingData);
                    updateBrandingStyles(brandingData);
                } catch (err) {
                    console.warn("Unable to load org branding", err);
                    setBranding(null);
                    updateBrandingStyles(null);
                }
            } else {
                setBranding(null);
                updateBrandingStyles(null);
            }
        } catch (e) {
            logout();
        }
    };

    useEffect(() => {
        const initAuth = async () => {
            const token = localStorage.getItem("token");
            if (token) {
                await refreshUser();
            }
            setLoading(false);
        };
        initAuth();
    }, []);

    const loginStep1 = async (email: string, password: string) => {
        return await api.loginStep1(email, password);
    };

    const loginStep2 = async (email: string, otp: string) => {
        const data = await api.loginStep2(email, otp);
        localStorage.setItem("token", data.access_token);
        await refreshUser();
    };

    const signup = async (email: string, password: string, fullName: string, mobile?: string) => {
        return await api.signup(email, password, fullName, mobile);
    };

    const forgotPassword = async (email: string) => {
        return await api.forgotPassword(email);
    };

    // mobileOtp is now optional / ignored by the backend — email OTP only
    const verifySignup = async (email: string, emailOtp: string, mobileOtp?: string) => {
        await api.verifySignup(email, emailOtp, mobileOtp || "bypass");
    };

    const logout = () => {
        localStorage.removeItem("token");
        setUser(null);
        router.push("/login");
    };

    return (
        <AuthContext.Provider value={{ 
            user,
            branding,
            loading, 
            loginStep1, 
            loginStep2, 
            signup, 
            verifySignup,
            forgotPassword,
            logout,
            refreshUser
        }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);
