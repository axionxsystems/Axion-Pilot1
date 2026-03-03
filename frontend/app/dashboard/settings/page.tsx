"use client";

import { useState } from "react";
import AuthGuard from "../../../components/AuthGuard";
import { useAuth } from "../../../components/AuthProvider";
import { api } from "../../../services/api";
import Link from "next/link";
import { Sparkles, LogOut, User, Key, ShieldCheck, CheckCircle2, ChevronLeft, Loader2 } from "lucide-react";

export default function SettingsPage() {
    const { user, logout } = useAuth();
    const [currentPassword, setCurrentPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

    const handlePasswordUpdate = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setMessage(null);
        try {
            await api.updatePassword(currentPassword, newPassword);
            setMessage({ type: 'success', text: 'Password updated successfully!' });
            setCurrentPassword("");
            setNewPassword("");
        } catch (err: any) {
            setMessage({ type: 'error', text: err.message });
        } finally {
            setLoading(false);
        }
    };

    return (
        <AuthGuard>
            <main className="min-h-screen bg-background text-foreground relative overflow-hidden font-sans selection:bg-primary/20">
                {/* Background Effects */}
                <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-primary/10 rounded-full blur-[120px] pointer-events-none animate-pulse-slow" />

                {/* Navbar */}
                <nav className="fixed top-0 left-0 right-0 z-50 glass-subtle border-b border-white/5 px-8 py-4">
                    <div className="max-w-4xl mx-auto flex justify-between items-center">
                        <Link href="/dashboard" className="flex items-center gap-2 group text-muted-foreground hover:text-white transition-colors">
                            <ChevronLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
                            Back to Dashboard
                        </Link>

                        <div className="flex items-center gap-2">
                            <span className="text-xl font-bold tracking-tight">
                                Project<span className="gradient-text">Pilot</span>
                            </span>
                        </div>
                    </div>
                </nav>

                <div className="max-w-2xl mx-auto px-6 pt-32 pb-20 relative z-10 animate-fade-in-up">
                    <h1 className="text-3xl font-bold mb-8 gradient-text">Account Settings</h1>

                    {/* Profile Section */}
                    <div className="glass p-8 rounded-3xl border border-white/10 shadow-2xl mb-8">
                        <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                            <User className="w-5 h-5 text-primary" />
                            Profile Details
                        </h2>

                        <div className="space-y-4">
                            <div className="p-4 bg-white/5 rounded-xl border border-white/5 flex items-center justify-between">
                                <div>
                                    <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Email Address</p>
                                    <p className="text-white font-medium">{user?.email}</p>
                                </div>
                                <ShieldCheck className="w-5 h-5 text-emerald-500" />
                            </div>

                            <div className="p-4 bg-white/5 rounded-xl border border-white/5 flex items-center justify-between">
                                <div>
                                    <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Current Plan</p>
                                    <p className="text-white font-medium capitalize flex items-center gap-2">
                                        {user?.plan || 'Free'}
                                        <span className="text-xs bg-primary/20 text-primary px-2 py-0.5 rounded border border-primary/20">Active</span>
                                    </p>
                                </div>
                                <Sparkles className="w-5 h-5 text-accent" />
                            </div>
                        </div>
                    </div>

                    {/* Password Section */}
                    <div className="glass p-8 rounded-3xl border border-white/10 shadow-2xl">
                        <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                            <Key className="w-5 h-5 text-accent" />
                            Change Password
                        </h2>

                        {message && (
                            <div className={`mb-6 p-4 rounded-xl text-sm flex items-center gap-2 animate-fade-in ${message.type === 'success'
                                    ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400'
                                    : 'bg-destructive/10 border border-destructive/20 text-destructive'
                                }`}>
                                {message.type === 'success' && <CheckCircle2 className="w-4 h-4" />}
                                {message.text}
                            </div>
                        )}

                        <form onSubmit={handlePasswordUpdate} className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider ml-1">
                                    Current Password
                                </label>
                                <input
                                    type="password"
                                    value={currentPassword}
                                    onChange={(e) => setCurrentPassword(e.target.value)}
                                    className="w-full bg-white/5 border border-white/10 rounded-xl py-3 px-4 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all duration-200"
                                    required
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider ml-1">
                                    New Password
                                </label>
                                <input
                                    type="password"
                                    value={newPassword}
                                    onChange={(e) => setNewPassword(e.target.value)}
                                    className="w-full bg-white/5 border border-white/10 rounded-xl py-3 px-4 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all duration-200"
                                    required
                                />
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full group relative flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-white/10 hover:bg-white/15 border border-white/10 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed mt-2"
                            >
                                {loading ? (
                                    <Loader2 className="w-5 h-5 animate-spin text-white" />
                                ) : (
                                    <span className="font-semibold text-white">Update Password</span>
                                )}
                            </button>
                        </form>
                    </div>

                    <button
                        onClick={logout}
                        className="w-full mt-8 py-3 text-destructive hover:bg-destructive/10 rounded-xl transition-colors text-sm font-medium flex items-center justify-center gap-2"
                    >
                        <LogOut className="w-4 h-4" />
                        Sign Out
                    </button>
                </div>
            </main>
        </AuthGuard>
    );
}
