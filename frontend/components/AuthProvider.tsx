"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, User } from "../services/api";

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (email, password) => Promise<void>;
    signup: (email, password) => Promise<void>;
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

    const login = async (email, password) => {
        const data = await api.login(email, password);
        localStorage.setItem("token", data.access_token);
        const userData = await api.getMe();
        setUser(userData);
        router.push("/dashboard");
    };

    const signup = async (email, password) => {
        await api.signup(email, password);
        await login(email, password);
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
