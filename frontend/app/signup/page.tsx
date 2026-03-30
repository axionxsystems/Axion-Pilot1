"use client";

import { useState, useMemo } from "react";
import { useAuth } from "../../components/AuthProvider";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
    Mail, Lock, Loader2, UserPlus, User, Phone,
    Eye, EyeOff, CheckCircle2, XCircle, ShieldCheck, KeyRound
} from "lucide-react";
import { Logo } from "@/components/ui/Logo";

const validateName = (v: string) =>
    v.trim().length >= 3 ? null : "Name must be at least 3 characters";

const validateEmail = (v: string) =>
    /^[^\s@]+@gmail\.com$/.test(v) ? null : "Only Gmail addresses are allowed";

const validateMobile = (v: string) =>
    /^\d{10}$/.test(v) ? null : "Mobile must be exactly 10 digits";

const validatePassword = (v: string) => {
    if (v.length < 8) return "Password must be at least 8 characters";
    if (!/[A-Z]/.test(v)) return "Add at least one uppercase letter";
    if (!/[a-z]/.test(v)) return "Add at least one lowercase letter";
    if (!/[0-9]/.test(v)) return "Add at least one number";
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(v)) return "Add at least one special character";
    return null;
};

const validateConfirm = (pw: string, cpw: string) =>
    pw === cpw ? null : "Passwords do not match";

function Field({ label, icon: Icon, error, touched, children }: {
    label: string; icon: any; error: string | null; touched: boolean; children: React.ReactNode;
}) {
    const state = !touched ? "idle" : error ? "error" : "ok";
    return (
        <div className="space-y-1.5">
            <label className="flex items-center gap-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider ml-1">
                <Icon className="w-3.5 h-3.5" />{label}
            </label>
            <div className="relative group">
                {children}
                {touched && (
                    <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
                        {state === "ok" ? <CheckCircle2 className="w-4 h-4 text-emerald-500" /> : <XCircle className="w-4 h-4 text-destructive" />}
                    </div>
                )}
            </div>
            {touched && error && (
                <p className="text-xs text-destructive ml-1 animate-in fade-in slide-in-from-top-1 duration-200">{error}</p>
            )}
        </div>
    );
}

function PasswordStrength({ password }: { password: string }) {
    const checks = useMemo(() => [
        { label: "8+ characters", ok: password.length >= 8 },
        { label: "Uppercase letter", ok: /[A-Z]/.test(password) },
        { label: "Lowercase letter", ok: /[a-z]/.test(password) },
        { label: "Number included", ok: /[0-9]/.test(password) },
        { label: "Special character", ok: /[!@#$%^&*(),.?":{}|<>]/.test(password) },
    ], [password]);
    const passed = checks.filter(c => c.ok).length;
    const colors = ["", "bg-destructive", "bg-orange-400", "bg-yellow-400", "bg-blue-400", "bg-emerald-500"];
    if (!password) return null;
    return (
        <div className="mt-2 space-y-2 animate-in fade-in duration-300">
            <div className="flex gap-1.5">
                {checks.map((_, i) => (
                    <div key={i} className={`h-1 flex-1 rounded-full transition-all duration-500 ${i < passed ? colors[passed] : "bg-muted"}`} />
                ))}
            </div>
            <div className="grid grid-cols-2 gap-1">
                {checks.map(c => (
                    <div key={c.label} className={`flex items-center gap-1.5 text-[11px] font-medium ${c.ok ? "text-emerald-500" : "text-muted-foreground/60"}`}>
                        <div className={`w-1.5 h-1.5 rounded-full ${c.ok ? "bg-emerald-500" : "bg-muted"}`} />{c.label}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default function SignupPage() {
    const { signup, verifySignup } = useAuth();
    const router = useRouter();

    const [fields, setFields] = useState({ name: "", email: "", mobile: "", password: "", confirm: "" });
    const [touched, setTouched] = useState<Record<string, boolean>>({});
    const [showPw, setShowPw] = useState(false);
    const [showCpw, setShowCpw] = useState(false);
    const [otpStep, setOtpStep] = useState(false);
    const [emailOtp, setEmailOtp] = useState("");
    const [mobileOtp, setMobileOtp] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const set = (key: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
        setFields(f => ({ ...f, [key]: e.target.value }));
    const touch = (key: string) => () =>
        setTouched(t => ({ ...t, [key]: true }));

    const errors = {
        name: validateName(fields.name),
        email: validateEmail(fields.email),
        mobile: validateMobile(fields.mobile),
        password: validatePassword(fields.password),
        confirm: validateConfirm(fields.password, fields.confirm),
    };
    const isValid = Object.values(errors).every(e => e === null);

    const inputClass = (key: string) => {
        const t = touched[key]; const err = errors[key as keyof typeof errors];
        return `w-full bg-secondary/50 border rounded-xl py-3 pl-10 pr-10 text-foreground placeholder:text-muted-foreground/40 focus:outline-none focus:ring-2 transition-all duration-200 text-sm ${!t ? "border-border focus:ring-primary/30 focus:border-primary/50" : err ? "border-destructive/60 focus:ring-destructive/20" : "border-emerald-500/50 focus:ring-emerald-500/20"}`;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setTouched({ name: true, email: true, mobile: true, password: true, confirm: true });
        if (!isValid) return;
        setError(""); setLoading(true);
        try {
            await signup(fields.email, fields.password, fields.name, fields.mobile);
            setOtpStep(true);
        } catch (err: any) {
            setError(err.message || "Registration failed.");
        } finally { setLoading(false); }
    };

    const handleVerifyOtp = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(""); setLoading(true);
        try {
            await verifySignup(fields.email, emailOtp, mobileOtp);
            router.push("/login?registered=true");
        } catch (err: any) {
            setError(err.message || "Verification failed. Check your codes.");
        } finally { setLoading(false); }
    };

    return (
        <div className="min-h-screen flex items-center justify-center relative overflow-hidden bg-background font-sans py-10">
            <div className="absolute top-1/4 right-1/4 w-[500px] h-[500px] bg-accent/20 rounded-full blur-[120px] pointer-events-none" />
            <div className="absolute bottom-1/4 left-1/4 w-[400px] h-[400px] bg-primary/20 rounded-full blur-[100px] pointer-events-none" />

            <div className="relative z-10 w-full max-w-lg px-4 animate-in fade-in slide-in-from-bottom-5 duration-700">
                <div className="flex justify-center mb-8"><Logo className="scale-125" /></div>

                <div className="bg-card/70 backdrop-blur-xl border border-white/10 rounded-[2rem] shadow-2xl p-8 md:p-10">
                    {otpStep ? (
                        /* ── OTP Verification Step ── */
                        <div className="animate-in slide-in-from-right-4 duration-500">
                            <div className="text-center mb-8 space-y-2">
                                <div className="inline-flex items-center justify-center w-14 h-14 bg-emerald-500/10 rounded-2xl border border-emerald-500/20 mb-3">
                                    <KeyRound className="w-7 h-7 text-emerald-500" />
                                </div>
                                <h1 className="text-2xl font-black tracking-tight text-foreground">Verify Your Account</h1>
                                <p className="text-sm text-muted-foreground">
                                    We sent codes to <strong>{fields.email}</strong> and mobile <strong>{fields.mobile}</strong>
                                </p>
                            </div>

                            {error && (
                                <div className="mb-5 p-4 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-sm flex items-center gap-3">
                                    <XCircle className="w-4 h-4 flex-shrink-0" />{error}
                                </div>
                            )}

                            <form onSubmit={handleVerifyOtp} className="space-y-5">
                                <div className="space-y-2">
                                    <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                                        <Mail className="w-3.5 h-3.5" /> Email OTP
                                    </label>
                                    <input
                                        type="text"
                                        value={emailOtp}
                                        onChange={e => setEmailOtp(e.target.value.replace(/\D/g, "").slice(0, 6))}
                                        className="w-full bg-secondary/70 border border-primary/30 rounded-xl py-4 text-center text-2xl font-mono tracking-[0.5em] focus:outline-none focus:ring-2 focus:ring-primary/40 transition-all"
                                        placeholder="000000" maxLength={6} required autoFocus
                                    />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                                        <Phone className="w-3.5 h-3.5" /> Mobile OTP
                                    </label>
                                    <input
                                        type="text"
                                        value={mobileOtp}
                                        onChange={e => setMobileOtp(e.target.value.replace(/\D/g, "").slice(0, 6))}
                                        className="w-full bg-secondary/70 border border-primary/30 rounded-xl py-4 text-center text-2xl font-mono tracking-[0.5em] focus:outline-none focus:ring-2 focus:ring-primary/40 transition-all"
                                        placeholder="000000" maxLength={6} required
                                    />
                                </div>
                                <p className="text-[11px] text-muted-foreground text-center">Both codes expire in 5 minutes.</p>
                                <button
                                    type="submit"
                                    disabled={loading || emailOtp.length < 6 || mobileOtp.length < 6}
                                    className="w-full flex items-center justify-center gap-2 py-3.5 rounded-xl font-bold text-sm bg-primary text-primary-foreground hover:bg-primary/90 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <><ShieldCheck className="w-4 h-4" /><span>Verify & Activate Account</span></>}
                                </button>
                                <button type="button" onClick={() => { setOtpStep(false); setError(""); }} className="w-full text-xs text-muted-foreground hover:text-foreground transition-colors">
                                    ← Back to form
                                </button>
                            </form>
                        </div>
                    ) : (
                        /* ── Form Step ── */
                        <>
                            <div className="text-center mb-8 space-y-2">
                                <div className="inline-flex items-center justify-center w-14 h-14 bg-primary/10 rounded-2xl border border-primary/20 mb-3">
                                    <ShieldCheck className="w-7 h-7 text-primary" />
                                </div>
                                <h1 className="text-2xl font-black tracking-tight text-foreground">Create Your Account</h1>
                                <p className="text-sm text-muted-foreground">Join thousands of students building smarter projects</p>
                            </div>

                            {error && (
                                <div className="mb-6 p-4 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-sm flex items-center gap-3 animate-in fade-in duration-300">
                                    <XCircle className="w-4 h-4 flex-shrink-0" />{error}
                                </div>
                            )}

                            <form onSubmit={handleSubmit} className="space-y-5">
                                <Field label="Full Name" icon={User} error={errors.name} touched={!!touched.name}>
                                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none"><User className="w-4 h-4" /></div>
                                    <input id="signup-name" type="text" value={fields.name} onChange={set("name")} onBlur={touch("name")} className={inputClass("name")} placeholder="John Doe" autoComplete="name" />
                                </Field>

                                <Field label="Gmail Address" icon={Mail} error={errors.email} touched={!!touched.email}>
                                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none"><Mail className="w-4 h-4" /></div>
                                    <input id="signup-email" type="email" value={fields.email} onChange={set("email")} onBlur={touch("email")} className={inputClass("email")} placeholder="name@gmail.com" autoComplete="email" />
                                </Field>

                                <Field label="Mobile Number" icon={Phone} error={errors.mobile} touched={!!touched.mobile}>
                                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none"><Phone className="w-4 h-4" /></div>
                                    <input id="signup-mobile" type="tel" value={fields.mobile} onChange={e => { const v = e.target.value.replace(/\D/g, "").slice(0, 10); setFields(f => ({ ...f, mobile: v })); }} onBlur={touch("mobile")} className={inputClass("mobile")} placeholder="10-digit number" maxLength={10} />
                                </Field>

                                <Field label="Password" icon={Lock} error={errors.password} touched={!!touched.password}>
                                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none"><Lock className="w-4 h-4" /></div>
                                    <input id="signup-password" type={showPw ? "text" : "password"} value={fields.password} onChange={set("password")} onBlur={touch("password")} className={inputClass("password")} placeholder="Min 8 chars, A-Z, 0-9, symbol" autoComplete="new-password" />
                                    <button type="button" onClick={() => setShowPw(p => !p)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground" tabIndex={-1}>
                                        {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                    </button>
                                </Field>
                                <PasswordStrength password={fields.password} />

                                <Field label="Confirm Password" icon={Lock} error={errors.confirm} touched={!!touched.confirm}>
                                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none"><Lock className="w-4 h-4" /></div>
                                    <input id="signup-confirm" type={showCpw ? "text" : "password"} value={fields.confirm} onChange={set("confirm")} onBlur={touch("confirm")} className={inputClass("confirm")} placeholder="Re-enter your password" autoComplete="new-password" />
                                    <button type="button" onClick={() => setShowCpw(p => !p)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground" tabIndex={-1}>
                                        {showCpw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                    </button>
                                </Field>

                                <button
                                    id="signup-submit" type="submit" disabled={loading}
                                    className={`w-full flex items-center justify-center gap-2.5 py-3.5 rounded-xl font-bold text-sm transition-all shadow-lg mt-2 ${isValid && !loading ? "bg-primary text-primary-foreground hover:bg-primary/90 hover:scale-[1.01]" : "bg-primary/50 text-primary-foreground/60 cursor-not-allowed"}`}
                                >
                                    {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <><UserPlus className="w-4 h-4" /><span>Create Account</span></>}
                                </button>
                            </form>

                            <div className="my-6 flex items-center gap-3">
                                <div className="flex-1 h-px bg-border/60" />
                                <span className="text-xs font-semibold text-muted-foreground/60 uppercase tracking-wider">or</span>
                                <div className="flex-1 h-px bg-border/60" />
                            </div>

                            <p className="text-center text-sm text-muted-foreground">
                                Already have an account?{" "}
                                <Link href="/login" className="text-primary hover:text-primary/80 font-semibold hover:underline underline-offset-4">Sign in</Link>
                            </p>
                        </>
                    )}
                </div>

                <p className="text-center text-xs text-muted-foreground/50 mt-6 px-4">
                    By creating an account you agree to our{" "}
                    <span className="underline cursor-pointer hover:text-muted-foreground">Terms of Service</span>{" "}
                    and <span className="underline cursor-pointer hover:text-muted-foreground">Privacy Policy</span>.
                </p>
            </div>
        </div>
    );
}
