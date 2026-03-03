"use client";

import { useState } from "react";
import { useAuth } from "../../components/AuthProvider";
import Link from "next/link";
import { Mail, Lock, ArrowRight, Loader2 } from "lucide-react";
import { Logo } from "@/components/ui/Logo";

export default function LoginPage() {
    const { login } = useAuth();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);
        try {
            await login(email, password);
        } catch (err: any) {
            setError("Invalid credentials. Please checking your email and password.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center relative overflow-hidden bg-background font-sans selection:bg-primary/20">
            {/* Background Effects */}
            <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-primary/20 rounded-full blur-[120px] animate-pulse-slow" />
            <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-accent/20 rounded-full blur-[100px] animate-pulse-slow" style={{ animationDelay: '2s' }} />

            <div className="relative z-10 w-full max-w-md px-4 animate-in fade-in slide-in-from-bottom-5 duration-700">
                {/* Logo */}
                <div className="flex justify-center mb-8">
                    <Logo className="scale-125" />
                </div>

                {/* Login Card */}
                <div className="glass p-8 rounded-3xl shadow-2xl border border-white/10 backdrop-blur-xl bg-card/60">
                    <div className="text-center mb-8">
                        <h2 className="text-2xl font-bold tracking-tight">
                            Welcome Back
                        </h2>
                        <p className="text-muted-foreground mt-2 text-sm">
                            Enter your credentials to access your workspace
                        </p>
                    </div>

                    {error && (
                        <div className="mb-6 p-4 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-sm flex items-center gap-2 animate-in fade-in">
                            <div className="w-1.5 h-1.5 rounded-full bg-destructive" />
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div className="space-y-2">
                            <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider ml-1">
                                Email
                            </label>
                            <div className="relative group">
                                <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors">
                                    <Mail className="w-5 h-5" />
                                </div>
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full bg-secondary/50 border border-border rounded-xl py-3 pl-10 pr-4 text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all duration-200"
                                    placeholder="name@example.com"
                                    required
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider ml-1">
                                Password
                            </label>
                            <div className="relative group">
                                <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors">
                                    <Lock className="w-5 h-5" />
                                </div>
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full bg-secondary/50 border border-border rounded-xl py-3 pl-10 pr-4 text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all duration-200"
                                    placeholder="••••••••"
                                    required
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full group relative flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 transition-all duration-300 shadow-lg shadow-primary/25 disabled:opacity-50 disabled:cursor-not-allowed mt-2"
                        >
                            {loading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <>
                                    <span className="font-semibold">Sign In</span>
                                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                                </>
                            )}
                        </button>
                    </form>

                    <div className="mt-6 text-center">
                        <p className="text-sm text-muted-foreground">
                            Don't have an account?{" "}
                            <Link href="/signup" className="text-primary hover:text-primary/80 font-medium transition-colors hover:underline underline-offset-4">
                                Sign up
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
