"use client";

import { useAuth } from "@/components/AuthProvider";
import { ProfileCard } from "./components/ProfileCard";
import { SecurityCard } from "./components/SecurityCard";
import { AdvancedSettings } from "./components/AdvancedSettings";
import { Settings as SettingsIcon, ShieldIcon, HelpCircle } from "lucide-react";

export default function SettingsPage() {
    const { user } = useAuth();

    return (
        <div className="max-w-5xl mx-auto space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-100 px-4 py-8 md:px-0">
            {/* Header Section */}
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-white/[0.05] pb-8">
                <div className="space-y-1.5">
                    <div className="flex items-center gap-2 mb-2">
                        <div className="p-1 px-2 rounded-md bg-blue-500/10 border border-blue-500/20 text-[10px] font-bold text-blue-400 tracking-[1.5px] uppercase">
                            User Dashboard
                        </div>
                    </div>
                    <h1 className="text-4xl md:text-5xl font-black tracking-tight text-white flex items-center gap-3">
                        <SettingsIcon className="w-8 h-8 md:w-10 md:h-10 text-blue-500" strokeWidth={3} />
                        Settings
                    </h1>
                    <p className="text-zinc-500 font-medium md:text-lg max-w-2xl leading-relaxed">
                        Adjust your profile, security preferences, and account management settings to tailor your experience.
                    </p>
                </div>
                
                <div className="flex items-center gap-3">
                    <button className="p-2.5 rounded-xl border border-white/5 bg-white/[0.03] text-zinc-400 hover:text-white hover:bg-white/10 transition-all duration-300">
                        <HelpCircle className="w-5 h-5" />
                    </button>
                    <div className="h-10 w-[1px] bg-white/[0.05] mx-2 hidden md:block" />
                    <div className="flex items-center gap-3 px-4 py-2 rounded-xl bg-[rgba(255,255,255,0.03)] border border-white/10">
                        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                        <span className="text-[11px] font-bold text-zinc-300 tracking-wider">SECURE CONNECTION</span>
                    </div>
                </div>
            </div>

            {/* Layout Sections */}
            <div className="grid grid-cols-1 gap-12 pt-4">
                {/* Profile Section */}
                <section className="space-y-4">
                    <div className="flex items-center gap-2 mb-4 px-1">
                        <SettingsIcon className="w-4 h-4 text-zinc-500" />
                        <h2 className="text-sm font-bold text-zinc-400 uppercase tracking-widest">General Profile</h2>
                    </div>
                    <ProfileCard user={user} />
                </section>

                {/* Security Section */}
                <section className="space-y-4">
                    <div className="flex items-center gap-2 mb-4 px-1">
                        <ShieldIcon className="w-4 h-4 text-zinc-500" />
                        <h2 className="text-sm font-bold text-zinc-400 uppercase tracking-widest">Security & Authentication</h2>
                    </div>
                    <SecurityCard />
                </section>

                {/* Advanced Section */}
                <section className="space-y-4 pb-12">
                    <div className="flex items-center gap-2 mb-4 px-1">
                        <HelpCircle className="w-4 h-4 text-zinc-500" />
                        <h2 className="text-sm font-bold text-zinc-400 uppercase tracking-widest">Account Management</h2>
                    </div>
                    <AdvancedSettings />
                </section>
            </div>
        </div>
    );
}
