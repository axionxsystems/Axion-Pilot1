"use client";

import { useState } from "react";
import { useAuth } from "../../components/AuthProvider";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Mail, Lock, ArrowRight, Loader2, ShieldCheck, KeyRound } from "lucide-react";
import { Logo } from "@/components/ui/Logo";

export default function LoginPage() {
    const { loginStep1, loginStep2, user } = useAuth();
    const router = useRouter();

    // Step 1: Credentials
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    
    // Step 2: OTP
    const [isOtpStep, setIsOtpStep] = useState(false);
    const [otp, setOtp] = useState("");

    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const [resendTimer, setResendTimer] = useState(0);
    const [successMessage, setSuccessMessage] = useState("");

    const startResendTimer = () => {
        setResendTimer(60);
        const timer = setInterval(() => {
            setResendTimer((prev) => {
                if (prev <= 1) {
                    clearInterval(timer);
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);
    };

    // Initial Login Step
    const handleStep1 = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);
        try {
            const res = await loginStep1(email, password);
            if (res.message) setSuccessMessage(res.message);
            if (res.requires_otp) {
                setIsOtpStep(true);
            }
        } catch (err: any) {
            setError(err.message || "Invalid email or password.");
        } finally {
            setLoading(false);
        }
    };

    // OTP Verify Step
    const handleStep2 = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);
        try {
            await loginStep2(email, otp);
            // loginStep2 sets the token and calls refreshUser, which updates the user context.
            // We need a brief moment for state to propagate, so we read the user directly.
            const userData = await import("../../services/api").then(m => m.api.getMe());
            if (userData.is_admin) {
                router.push("/dashboard/admin");
            } else {
                router.push("/dashboard");
            }
        } catch (err: any) {
            setError(err.message || "Invalid or expired code.");
        } finally {
            setLoading(false);
        }
    };

    const handleResendOtp = async () => {
        if (resendTimer > 0) return;
        setError("");
        setLoading(true);
        try {
            const res = await loginStep1(email, password);
            if (res.message) setSuccessMessage(res.message);
            startResendTimer();
        } catch (err: any) {
            setError("Failed to resend code.");
        } finally {
            setLoading(false);
        }
    };

    const handleBackToLogin = () => {
        setIsOtpStep(false);
        setOtp("");
        setError("");
    };

    return (
        <div className="min-h-screen flex items-center justify-center relative overflow-hidden bg-background font-sans selection:bg-primary/20">
            {/* Background Effects */}
            <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-primary/20 rounded-full blur-[120px] animate-pulse-slow" />
            <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-accent/20 rounded-full blur-[100px] animate-pulse-slow" style={{ animationDelay: '2s' }} />

            <div className="relative z-10 w-full max-w-md px-4 animate-in fade-in slide-in-from-bottom-5 duration-700">
                <div className="flex justify-center mb-8">
                    <Logo className="scale-125" />
                </div>

                <div className="glass p-8 rounded-3xl shadow-2xl border border-white/10 backdrop-blur-xl bg-card/60">
                    <div className="text-center mb-8">
                        <h2 className="text-2xl font-bold tracking-tight">
                            {isOtpStep ? "Security Verification" : "Welcome Back"}
                        </h2>
                        <p className="text-muted-foreground mt-2 text-sm">
                            {isOtpStep 
                                ? (successMessage || `A verification code was sent to ${email}`)
                                : "Enter your credentials to access your workspace"
                            }
                        </p>
                    </div>

                    {error && (
                        <div className="mb-6 p-4 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-sm flex items-center gap-2 animate-in fade-in">
                            <div className="w-1.5 h-1.5 rounded-full bg-destructive" />
                            {error}
                        </div>
                    )}

                    {!isOtpStep ? (
                        <form onSubmit={handleStep1} className="space-y-5">
                            <div className="space-y-2">
                                <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider ml-1">Email</label>
                                <div className="relative group">
                                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors">
                                        <Mail className="w-5 h-5" />
                                    </div>
                                    <input
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        className="w-full bg-secondary/50 border border-border rounded-xl py-3 pl-10 pr-4 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 transition-all duration-200"
                                        placeholder="name@example.com"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <div className="flex justify-between items-center px-1">
                                    <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Password</label>
                                    <Link href="/forgot-password" title="Recover Password" className="text-xs text-primary hover:underline underline-offset-4">Forgot?</Link>
                                </div>
                                <div className="relative group">
                                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors">
                                        <Lock className="w-5 h-5" />
                                    </div>
                                    <input
                                        type="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className="w-full bg-secondary/50 border border-border rounded-xl py-3 pl-10 pr-4 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 transition-all duration-200"
                                        placeholder="••••••••"
                                        required
                                    />
                                </div>
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full group relative flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 transition-all duration-300 shadow-lg shadow-primary/25 disabled:opacity-50 mt-2"
                            >
                                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <>
                                    <span className="font-semibold">Sign In</span>
                                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                                </>}
                            </button>
                        </form>
                    ) : (
                        <div className="space-y-5 animate-in slide-in-from-right-4 duration-500">
                            {successMessage && successMessage.includes("[DEV]") && (
                                <div className="p-5 rounded-xl bg-amber-500/15 border-2 border-amber-500/40 text-center">
                                    <p className="text-xs font-bold text-amber-400 uppercase tracking-wider mb-2">⚡ Dev Mode — Your OTP</p>
                                    <p className="text-4xl font-mono font-black tracking-[0.4em] text-amber-300">
                                        {successMessage.match(/\d{6}/)?.[0] || ""}
                                    </p>
                                    <p className="text-xs text-amber-400/70 mt-2">Copy this code into the field below</p>
                                </div>
                            )}
                            {successMessage && !successMessage.includes("[DEV]") && (
                                <div className="p-4 rounded-xl bg-primary/10 border border-primary/20 text-primary text-sm flex items-start gap-3">
                                    <ShieldCheck className="w-4 h-4 mt-0.5 flex-shrink-0" />
                                    <p>{successMessage}</p>
                                </div>
                            )}

                            <form onSubmit={handleStep2} className="space-y-5">
                            <div className="space-y-2">
                                <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider ml-1 text-center block">Security Code</label>
                                <div className="relative group">
                                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors">
                                        <ShieldCheck className="w-5 h-5" />
                                    </div>
                                    <input
                                        type="text"
                                        value={otp}
                                        onChange={(e) => setOtp(e.target.value)}
                                        className="w-full bg-secondary/70 border border-primary/30 rounded-xl py-4 pl-10 pr-4 text-center text-xl font-mono tracking-[0.5em] focus:outline-none focus:ring-2 focus:ring-primary/40 transition-all"
                                        placeholder="000000"
                                        maxLength={6}
                                        required
                                        autoFocus
                                    />
                                </div>
                                <p className="text-[10px] text-muted-foreground text-center mt-2">The code expires in 5 minutes.</p>
                            </div>

                            <div className="flex flex-col gap-3">
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="w-full group relative flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-primary text-primary-foreground shadow-lg hover:bg-primary/90 transition-all font-semibold"
                                >
                                    {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <>
                                        <span>Verify & Continue</span>
                                        <ShieldCheck className="w-5 h-5" />
                                    </>}
                                </button>

                                <div className="flex items-center justify-between px-1">
                                    <button
                                        type="button"
                                        disabled={resendTimer > 0 || loading}
                                        onClick={handleResendOtp}
                                        className="text-xs text-primary hover:underline underline-offset-4 disabled:text-muted-foreground disabled:no-underline transition-all"
                                    >
                                        {resendTimer > 0 ? `Resend in ${resendTimer}s` : "Resend Code"}
                                    </button>
                                    
                                    <button 
                                        type="button" 
                                        onClick={handleBackToLogin}
                                        className="text-xs text-muted-foreground hover:text-foreground transition-colors"
                                    >
                                        Back to login
                                    </button>
                                </div>
                            </div>
                        </form>
                    </div>
                )}

                    {!isOtpStep && (
                        <div className="mt-6 text-center">
                            <p className="text-sm text-muted-foreground">
                                Don't have an account?{" "}
                                <Link href="/signup" title="Create Account" className="text-primary hover:text-primary/80 font-medium transition-colors hover:underline underline-offset-4">Sign up</Link>
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
