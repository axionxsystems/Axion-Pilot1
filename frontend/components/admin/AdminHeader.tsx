"use client";

import { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { api } from "../../services/api";
import { useAuth } from "../AuthProvider";
import { cn } from "@/lib/utils";

export default function AdminHeader() {
    const { user } = useAuth();
    const pathname = usePathname();
    const [stats, setStats] = useState<any>(null);

    useEffect(() => {
        if (user && user.is_admin) {
            api.getAdminStats().then(setStats).catch(console.error);
        }
    }, [user]);

    if (!user?.is_admin) return null;

    return (
        <div className="space-y-6 mb-8 mt-4 animate-in fade-in duration-500">
            {/* ── Command Center Header ─────────────────────────────────────── */}
            <div className="relative rounded-[2rem] overflow-hidden border border-red-500/20 bg-gradient-to-br from-zinc-900/80 via-background to-red-950/20 p-8 md:p-10">
                {/* Grid pattern overlay */}
                <div className="absolute inset-0 opacity-5 pointer-events-none"
                    style={{ backgroundImage: "linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)", backgroundSize: "40px 40px" }} />
                {/* Red glow */}
                <div className="absolute -top-10 -right-10 w-64 h-64 bg-red-500/10 rounded-full blur-3xl pointer-events-none" />
                <div className="absolute -bottom-10 -left-10 w-48 h-48 bg-orange-500/5 rounded-full blur-3xl pointer-events-none" />

                <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                    <div>
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md bg-red-500/10 border border-red-500/30 text-red-400 text-[10px] font-black uppercase tracking-[0.2em] mb-3 font-mono">
                            <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse" />
                            SUDO ACCESS — RESTRICTED
                        </div>
                        <h1 className="text-4xl md:text-5xl font-black tracking-tight text-foreground font-mono">
                            Platform Control<br />
                            <span className="text-red-400">Center</span>
                        </h1>
                        <p className="text-muted-foreground mt-2 text-sm font-medium font-mono">
                            Logged in as <span className="text-red-400 font-bold">{user?.email}</span> · All actions are logged.
                        </p>
                    </div>

                    {/* Status + Date */}
                    <div className="flex flex-col items-end gap-3">
                        <div className="flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 rounded-xl px-4 py-2">
                            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_6px_#4ade80]" />
                            <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest font-mono">SYSTEM LIVE</span>
                        </div>
                        <div className="text-xs text-muted-foreground font-mono text-right">
                            <div className="font-bold text-foreground">{new Date().toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long" })}</div>
                            <div>{new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} IST</div>
                        </div>
                    </div>
                </div>

                {/* KPI strip */}
                <div className="relative z-10 grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6">
                    {[
                        { label: "Total Users", value: stats?.total_users ?? "—", suffix: "accounts", color: "text-blue-400", border: "border-blue-500/20 bg-blue-500/5" },
                        { label: "Projects", value: stats?.total_projects ?? "—", suffix: "generated", color: "text-violet-400", border: "border-violet-500/20 bg-violet-500/5" },
                        { label: "Reports", value: stats?.total_reports ?? "—", suffix: "produced", color: "text-emerald-400", border: "border-emerald-500/20 bg-emerald-500/5" },
                        { label: "PPTs", value: stats?.total_presentations ?? "—", suffix: "created", color: "text-amber-400", border: "border-amber-500/20 bg-amber-500/5" },
                    ].map(k => (
                        <div key={k.label} className={`rounded-2xl border ${k.border} px-4 py-3`}>
                            <div className={`text-2xl font-black font-mono ${k.color}`}>{k.value}</div>
                            <div className="text-[10px] text-muted-foreground uppercase tracking-widest font-bold mt-0.5">{k.label}</div>
                            <div className="text-[10px] text-muted-foreground/50">{k.suffix}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Admin Navigation Hub using Next.js Link for SPA transitions */}
            <div className="flex flex-wrap items-center gap-1.5 p-1 bg-muted/40 border border-border/40 rounded-[1.25rem] w-fit">
                {[
                    { label: "Overview", href: "/dashboard/admin" },
                    { label: "Accounts", href: "/dashboard/admin/users" },
                    { label: "Projects", href: "/dashboard/admin/projects" },
                    { label: "Moderation", href: "/dashboard/admin/moderation" },
                    { label: "Templates", href: "/dashboard/admin/templates" },
                    { label: "AI Config", href: "/dashboard/admin/settings" },
                ].map((link) => (
                    <Link
                        key={link.href}
                        href={link.href}
                        className={cn(
                            "px-5 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all",
                            pathname === link.href ? "bg-card text-red-400 shadow-sm ring-1 ring-red-500/20" : "text-muted-foreground hover:text-foreground"
                        )}
                    >
                        {link.label}
                    </Link>
                ))}
            </div>
        </div>
    );
}
