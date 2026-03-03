"use client";

import { useState } from "react";
import { useAuth } from "../../components/AuthProvider";
import Link from "next/link";
import { Sparkles, Mail, Lock, ArrowRight, Loader2, UserPlus } from "lucide-react";

export default function RegisterPage() {
    const { signup } = useAuth();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);
        try {
            await signup(email, password);
        } catch (err: any) {
            setError(err.message || "Registration failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center relative overflow-hidden bg-background font-sans selection:bg-primary/20">
            {/* Background Effects */}
            <div className="absolute top-1/4 right-1/4 w-[500px] h-[500px] bg-accent/20 rounded-full blur-[120px] animate-pulse-slow" />
            <div className="absolute bottom-1/4 left-1/4 w-[400px] h-[400px] bg-primary/20 rounded-full blur-[100px] animate-pulse-slow" style={{ animationDelay: '2s' }} />

            {/* Grid Pattern */}
            <div className="absolute inset-0 bg-[linear-gradient(to_right,hsl(var(--border)/0.3)_1px,transparent_1px),linear-gradient(to_bottom,hsl(var(--border)/0.3)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_110%)] pointer-events-none" />

            <div className="relative z-10 w-full max-w-md px-4 animate-fade-in-up">
                {/* Logo */}
                <div className="flex justify-center mb-8">
                    <Link href="/" className="inline-flex items-center gap-3 group">
                        <div className="relative">
                            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg shadow-primary/30 group-hover:shadow-xl group-hover:shadow-primary/40 transition-all duration-300">
                                <Sparkles className="w-6 h-6 text-white" />
                            </div>
                        </div>
                        <span className="text-2xl font-bold text-foreground tracking-tight">
                            Project<span className="gradient-text">Pilot</span>
                        </span>
                    </Link>
                </div>

                {/* Register Card */}
                <div className="glass p-8 rounded-3xl shadow-2xl border border-white/10 backdrop-blur-xl">
                    <div className="text-center mb-8">
                        <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60">
                            Create Account
                        </h2>
                        <p className="text-muted-foreground mt-2 text-sm">
                            Join thousands of students building projects
                        </p>
                    </div>

                    {error && (
                        <div className="mb-6 p-4 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-sm flex items-center gap-2 animate-fade-in">
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
                                    className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all duration-200"
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
                                    className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all duration-200"
                                    placeholder="••••••••"
                                    required
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full group relative flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-gradient-to-r from-primary to-accent hover:opacity-90 transition-all duration-300 shadow-lg shadow-primary/25 disabled:opacity-50 disabled:cursor-not-allowed mt-2"
                        >
                            {loading ? (
                                <Loader2 className="w-5 h-5 animate-spin text-white" />
                            ) : (
                                <>
                                    <span className="font-semibold text-white">Get Started</span>
                                    <UserPlus className="w-5 h-5 text-white group-hover:translate-x-1 transition-transform" />
                                </>
                            )}
                        </button>
                    </form>

                    <div className="mt-6 text-center">
                        <p className="text-sm text-muted-foreground">
                            Already have an account?{" "}
                            <Link href="/login" className="text-primary hover:text-accent font-medium transition-colors hover:underline underline-offset-4">
                                Sign in
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
