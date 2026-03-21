"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, User } from "../services/api";

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (email: string, password: string) => Promise<void>;
    signup: (email: string, password: string, full_name?: string, mobile?: string) => Promise<void>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType>({} as any);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const initAuth = async () => {
            const token = localStorage.getItem("token");
            if (token) {
                try {
                    const userData = await api.getMe();
                    setUser(userData);
                } catch (e) {
                    logout();
                }
            }
            setLoading(false);
        };
        initAuth();
    }, []);

    const login = async (email: string, password: string) => {
        try {
            const data = await api.login(email, password);
            localStorage.setItem("token", data.access_token);
            const userData = await api.getMe();
            setUser(userData);
            if (userData.is_admin) {
                router.push("/dashboard/admin");
            } else {
                router.push("/dashboard");
            }
        } catch (error: any) {
            console.error("Login failed:", error);
            throw error;
        }
    };

    const signup = async (email: string, password: string, full_name?: string, mobile?: string) => {
        try {
            await api.signup(email, password, full_name, mobile);
            await login(email, password);
        } catch (error: any) {
            console.error("Signup failed:", error);
            throw error;
        }
    };

    const logout = () => {
        localStorage.removeItem("token");
        setUser(null);
        router.push("/login"); // Redirect to login
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);
