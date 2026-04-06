"use client";

import { useState, useEffect } from "react";
import ProjectForm from "../../components/ProjectForm";
import AuthGuard from "../../components/AuthGuard";
import { useAuth } from "../../components/AuthProvider";
import VivaAssistant from "../../components/VivaAssistant";
import DownloadButton from "../../components/DownloadButton";
import { StatsSection, ActivityFeed, SuggestionPanel, RecentProjectsList, ProjectProgressTracker } from "../../components/dashboard/Widgets";
import { api } from "../../services/api";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "../../components/ui/button";
import { 
    LogOut, 
    Sparkles, 
    FileText, 
    Download, 
    Code, 
    MonitorPlay, 
    Settings, 
    Layers, 
    ArrowRight, 
    Clock, 
    BookOpen, 
    Database, 
    Cpu, 
    Rocket, 
    Activity as ActivityIcon, 
    Zap, 
    PlusCircle, 
    History as LucideHistory 
} from "lucide-react";

export default function Dashboard() {
    const [project, setProject] = useState<any>(null);
    const [stats, setStats] = useState<any>(null);
    const [recentProjects, setRecentProjects] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const { user } = useAuth();
    const router = useRouter();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [statsData, projectsData] = await Promise.all([
                    api.getUserStats(),
                    api.listProjects()
                ]);
                setStats(statsData);
                setRecentProjects(projectsData || []);
            } catch (err) {
                console.error("Failed to fetch dashboard data", err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    return (
        <div className="max-w-7xl mx-auto space-y-12 animate-in fade-in slide-in-from-bottom-5 duration-1000 px-6 py-10 md:px-0">
            {/* 1. TOP HEADER (Dashboard + Welcome) */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 border-b border-white/[0.05] pb-10">
                <div className="space-y-2 group">
                    <div className="flex items-center gap-2 mb-2">
                        <div className="p-1 px-2.5 rounded-lg bg-blue-500/10 border border-blue-500/20 text-[10px] font-black text-blue-400 tracking-[3px] uppercase animate-pulse">
                            Active Session
                        </div>
                    </div>
                    <h1 className="text-5xl md:text-6xl font-black tracking-tighter text-white flex items-center gap-4 relative">
                        <span className="bg-gradient-to-r from-blue-500 via-cyan-400 to-blue-400 bg-clip-text text-transparent drop-shadow-[0_0_15px_rgba(59,130,246,0.5)]">
                            Dashboard
                        </span>
                        <div className="absolute -bottom-2 left-0 w-24 h-1 bg-gradient-to-r from-blue-500 to-transparent rounded-full shadow-[0_0_10px_rgba(59,130,246,0.8)] group-hover:w-full transition-all duration-700" />
                    </h1>
                    <p className="text-zinc-500 mt-4 text-lg font-semibold tracking-tight">
                        Welcome back, <span className="text-zinc-300 font-bold">{user?.name?.split(" ")[0] || user?.email?.split('@')[0] || 'Creator'}</span>. You've completed <span className="text-blue-400">{stats?.projects_generated || 0}</span> projects this month.
                    </p>
                </div>
                
                <div className="flex flex-wrap items-center gap-4">
                    <div className="hidden lg:flex items-center gap-2 px-5 py-3 rounded-2xl bg-white/[0.03] border border-white/10 shadow-xl">
                        <div className="flex flex-col items-start mr-4">
                            <span className="text-[9px] font-black text-zinc-600 uppercase tracking-widest leading-none">System Health</span>
                            <span className="text-xs font-black text-emerald-500 mt-1 uppercase tracking-tighter">OPTIMAL 99.9%</span>
                        </div>
                        <div className="flex gap-1 h-1.5 w-12 bg-white/5 rounded-full overflow-hidden">
                            <div className="h-full w-4 bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                            <div className="h-full w-4 bg-emerald-500" />
                            <div className="h-full w-4 bg-emerald-400 animate-pulse" />
                        </div>
                    </div>

                    <Link href="/dashboard/projects">
                        <button className="relative group/btn bg-zinc-900 border border-white/10 text-white hover:text-white px-6 py-3.5 rounded-2xl text-xs font-black transition-all flex items-center gap-3 shadow-2xl overflow-hidden hover:scale-[1.02] active:scale-95 tracking-widest uppercase">
                            <Layers className="w-4 h-4 text-zinc-500 group-hover/btn:text-blue-400 transition-colors" />
                            MY VAULT
                            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-transparent opacity-0 group-hover/btn:opacity-100 transition-opacity" />
                        </button>
                    </Link>
                </div>
            </div>

            {!project ? (
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
                    <div className="lg:col-span-8 space-y-12">
                        {/* 2. STATS CARDS */}
                        <section className="space-y-4">
                            <div className="flex items-center gap-2 px-2">
                                <ActivityIcon className="w-4 h-4 text-zinc-500" />
                                <h2 className="text-xs font-black text-zinc-500 uppercase tracking-[3px]">Performance Overview</h2>
                            </div>
                            <StatsSection data={stats} />
                        </section>

                        {/* ADVANCED FEATURES (IMPORTANT) - Usage Stats & Quick Actions */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            {/* Quick Actions */}
                            <div className="bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.08)] backdrop-blur-xl rounded-[2.5rem] p-8 shadow-2xl transition-all duration-300 hover:border-white/10 group/qa">
                                <div className="flex items-center gap-3 mb-8">
                                    <div className="p-2 rounded-xl bg-blue-500/10 border border-blue-500/20">
                                        <Zap className="w-5 h-5 text-blue-400" />
                                    </div>
                                    <h3 className="text-xl font-black text-white tracking-tight">Quick Actions</h3>
                                </div>
                                <div className="grid grid-cols-2 gap-3">
                                    <button 
                                        onClick={() => document.getElementById('project-form')?.scrollIntoView({ behavior: 'smooth' })}
                                        className="p-4 rounded-2xl bg-white/[0.03] border border-white/5 hover:bg-blue-500 hover:border-blue-500 transition-all duration-300 group/item flex flex-col items-center justify-center text-center gap-3"
                                    >
                                        <PlusCircle className="w-6 h-6 text-blue-400 group-hover/item:text-white transition-colors" />
                                        <span className="text-[10px] font-black text-zinc-300 group-hover/item:text-white uppercase tracking-widest">New Project</span>
                                    </button>
                                    <button 
                                        onClick={() => router.push('/dashboard/projects')}
                                        className="p-4 rounded-2xl bg-white/[0.03] border border-white/5 hover:bg-purple-500 hover:border-purple-500 transition-all duration-300 group/item flex flex-col items-center justify-center text-center gap-3"
                                    >
                                        <LucideHistory className="w-6 h-6 text-purple-400 group-hover/item:text-white transition-colors" />
                                        <span className="text-[10px] font-black text-zinc-300 group-hover/item:text-white uppercase tracking-widest">Resume Last</span>
                                    </button>
                                    <button 
                                        onClick={() => router.push('/dashboard/settings')}
                                        className="p-4 rounded-2xl bg-white/[0.03] border border-white/5 hover:bg-pink-500 hover:border-pink-500 transition-all duration-300 group/item flex flex-col items-center justify-center text-center gap-3"
                                    >
                                        <Settings className="w-6 h-6 text-pink-400 group-hover/item:text-white transition-colors" />
                                        <span className="text-[10px] font-black text-zinc-300 group-hover/item:text-white uppercase tracking-widest">Preferences</span>
                                    </button>
                                    <button className="p-4 rounded-2xl bg-white/[0.03] border border-white/5 hover:bg-emerald-500 hover:border-emerald-500 transition-all duration-300 group/item flex flex-col items-center justify-center text-center gap-3">
                                        <Download className="w-6 h-6 text-emerald-400 group-hover/item:text-white transition-colors" />
                                        <span className="text-[10px] font-black text-zinc-300 group-hover/item:text-white uppercase tracking-widest">View Reports</span>
                                    </button>
                                </div>
                            </div>

                            {/* Usage Stats / AI Credits */}
                            <div className="bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.08)] backdrop-blur-xl rounded-[2.5rem] p-8 shadow-2xl transition-all duration-300 hover:border-white/10 group/usage overflow-hidden relative">
                                <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 blur-3xl -z-10 group-hover/usage:bg-primary/10 transition-all" />
                                <div className="flex items-center gap-3 mb-8">
                                    <div className="p-2 rounded-xl bg-orange-500/10 border border-orange-500/20">
                                        <Database className="w-5 h-5 text-orange-400" />
                                    </div>
                                    <h3 className="text-xl font-black text-white tracking-tight">Cloud Resources</h3>
                                </div>
                                <div className="space-y-6">
                                    <div className="space-y-3">
                                        <div className="flex justify-between items-end">
                                            <span className="text-[11px] font-black text-zinc-400 uppercase tracking-widest">AI Credits Used</span>
                                            <span className="text-xs font-black text-white">850 / 1000</span>
                                        </div>
                                        <div className="h-2.5 bg-white/5 rounded-full overflow-hidden border border-white/5">
                                            <div className="h-full w-[85%] bg-gradient-to-r from-orange-600 to-orange-400 shadow-[0_0_15px_rgba(251,146,60,0.3)]" />
                                        </div>
                                    </div>
                                    <div className="space-y-3">
                                        <div className="flex justify-between items-end">
                                            <span className="text-[11px] font-black text-zinc-400 uppercase tracking-widest">API Endpoint Calls</span>
                                            <span className="text-xs font-black text-white">4.2k / 10k</span>
                                        </div>
                                        <div className="h-2.5 bg-white/5 rounded-full overflow-hidden border border-white/5">
                                            <div className="h-full w-[42%] bg-gradient-to-r from-blue-600 to-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.3)]" />
                                        </div>
                                    </div>
                                    <div className="pt-2">
                                        <p className="text-[10px] text-zinc-600 font-bold leading-relaxed tracking-tight italic">
                                            Usage stats update every 6 hours. Current billing cycle ends on <span className="text-zinc-500">April 28</span>.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                            <RecentProjectsList projects={recentProjects} />
                            <ProjectProgressTracker />
                        </div>

                        {/* 6. MAIN CTA CARD (Launch Generator) */}
                        <div className="group relative rounded-[3rem] p-12 overflow-hidden border border-white/10 shadow-2xl transition-all duration-700 hover:scale-[1.01]">
                            {/* Animated Background Gradient Overlay */}
                            <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 via-cyan-600/10 to-indigo-600/20 group-hover:scale-110 transition-transform duration-1000" />
                            <div className="absolute -right-20 -top-20 w-80 h-80 bg-blue-500/10 blur-[100px] animate-pulse" />
                            <div className="absolute -left-20 -bottom-20 w-80 h-80 bg-cyan-500/10 blur-[100px] group-hover:bg-cyan-500/20 transition-all duration-700" />
                            
                            {/* Particles/Shapes Decor */}
                            <div className="absolute top-10 right-20 w-2 h-2 rounded-full bg-blue-400/20 animate-bounce transition-all [animation-delay:200ms]" />
                            <div className="absolute bottom-20 left-40 w-3 h-3 rounded-full bg-cyan-400/20 animate-pulse transition-all [animation-delay:500ms]" />
                            <div className="absolute top-1/2 left-20 w-1 h-1 rounded-full bg-white/40 animate-ping transition-all duration-1000" />

                            <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-12 text-center md:text-left">
                                <div className="space-y-6">
                                    <div className="p-4 bg-[rgba(255,255,255,0.05)] backdrop-blur-xl w-fit mx-auto md:mx-0 rounded-[2rem] shadow-2xl border border-white/10 group-hover:rotate-12 transition-all duration-500">
                                        <Rocket className="w-12 h-12 text-white group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                                    </div>
                                    <div>
                                        <h2 className="text-4xl md:text-5xl font-black text-white tracking-tighter mb-4 leading-[1.1]">
                                            Ready to Build <br /> Something Big?
                                        </h2>
                                        <p className="text-zinc-400 font-bold text-lg max-w-sm tracking-tight leading-relaxed">
                                            Turn project ideas into production assets <br className="hidden md:block" /> 
                                            in sixty seconds.
                                        </p>
                                    </div>
                                    <button
                                        onClick={() => document.getElementById('project-form')?.scrollIntoView({ behavior: 'smooth' })}
                                        className="relative group/launch px-12 py-5 bg-gradient-to-r from-blue-600 via-cyan-500 to-blue-600 bg-[length:200%_auto] hover:bg-right transition-all duration-500 text-white font-black text-sm tracking-[3px] rounded-[1.5rem] shadow-[0_20px_40px_-10px_rgba(59,130,246,0.5)] hover:shadow-[0_25px_50px_-12px_rgba(59,130,246,0.6)] uppercase flex items-center gap-3 overflow-hidden"
                                    >
                                        <div className="absolute inset-0 bg-white/20 opacity-0 group-hover/launch:opacity-100 transition-opacity" />
                                        Launch Generator
                                        <Sparkles className="w-5 h-5 text-white animate-pulse" />
                                    </button>
                                </div>
                                
                                <div className="hidden xl:block relative group/model">
                                    <div className="absolute -inset-10 bg-blue-500/20 blur-[60px] opacity-0 group-hover/model:opacity-100 transition-all duration-1000" />
                                    <div className="w-[300px] h-[300px] rounded-[3rem] bg-[rgba(255,255,255,0.03)] border border-white/10 backdrop-blur-3xl p-8 flex items-center justify-center transform rotate-3 hover:rotate-0 transition-all duration-700 relative overflow-hidden group-hover:scale-110">
                                        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-transparent to-transparent" />
                                        <MonitorPlay className="w-32 h-32 text-white/10 group-hover:text-blue-500 transition-colors" strokeWidth={0.5} />
                                        <div className="absolute bottom-6 left-6 right-6 p-4 rounded-2xl bg-black/40 border border-white/5 backdrop-blur-xl">
                                            <div className="flex items-center gap-2 mb-2">
                                                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                                                <span className="text-[8px] font-black text-white uppercase tracking-widest">Processing Core</span>
                                            </div>
                                            <div className="h-1 bg-white/10 rounded-full overflow-hidden">
                                                <div className="h-full w-2/3 bg-blue-500 group-hover:w-full transition-all duration-1000" />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div id="project-form" className="mt-8 scroll-mt-24 pb-20">
                            <div className="flex flex-col items-center justify-center text-center space-y-3 mb-10">
                                <h3 className="text-[10px] font-black text-primary uppercase tracking-[5px]">The Generator</h3>
                                <h2 className="text-3xl font-black text-white tracking-tight">Configure Your Solution</h2>
                                <div className="w-12 h-1 bg-primary/20 rounded-full" />
                            </div>
                            <div className="animate-in fade-in slide-in-from-bottom-10 duration-1000">
                                <ProjectForm onProjectGenerated={setProject} />
                            </div>
                        </div>
                    </div>
                    
                    <div className="lg:col-span-4 h-full space-y-10">
                        <ActivityFeed />
                        <SuggestionPanel />
                        
                        <div className="p-8 rounded-[2.5rem] bg-gradient-to-br from-zinc-900 to-black border border-white/10 relative overflow-hidden group">
                            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 blur-3xl -z-10 group-hover:bg-primary/10 transition-all" />
                            <h4 className="text-xl font-black text-white mb-4 tracking-tight">Need Assistance?</h4>
                            <p className="text-sm text-zinc-500 font-bold mb-6 leading-relaxed">Our AI experts are ready to help you optimize your generation parameters.</p>
                            <Button className="w-full h-12 bg-white text-black hover:bg-zinc-200 border-none rounded-2xl font-black text-xs tracking-widest uppercase shadow-2xl transition-all hover:scale-[1.02]">
                                CONTACT SUPPORT
                            </Button>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="lg:col-span-12 max-w-5xl mx-auto w-full">
                    <div className="space-y-8 animate-in fade-in slide-in-from-top-4 duration-700">
                        <div className="flex items-center justify-between">
                            <button
                                onClick={() => setProject(null)}
                                className="group text-sm font-bold text-muted-foreground hover:text-primary flex items-center gap-2 transition-all"
                            >
                                <span className="group-hover:-translate-x-1 transition-transform">←</span>
                                Back to Dashboard
                            </button>
                            <div className="flex items-center gap-2 text-xs font-bold text-muted-foreground uppercase tracking-widest">
                                <Clock className="w-3 h-3" />
                                Generated {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </div>
                        </div>

                        <div className="rounded-[32px] border border-border/50 bg-card shadow-2xl overflow-hidden premium-shadow">
                            <div className="p-8 md:p-12 border-b bg-muted/20 relative overflow-hidden">
                                <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full -mr-32 -mt-32 blur-3xl" />
                                <div className="absolute bottom-0 left-0 w-64 h-64 bg-accent/5 rounded-full -ml-32 -mb-32 blur-3xl" />

                                <div className="relative z-10">
                                    <div className="flex justify-between items-start mb-6">
                                        <h2 className="text-4xl md:text-5xl font-black leading-tight tracking-tight text-foreground max-w-3xl">
                                            {project.title}
                                        </h2>
                                        <span className="px-4 py-1.5 rounded-full bg-primary/10 text-primary text-xs font-black border border-primary/20 uppercase tracking-tighter">
                                            Ready
                                        </span>
                                    </div>
                                    <div className="flex flex-wrap gap-4 text-sm font-semibold">
                                        <div className="flex items-center gap-2 bg-background/50 border border-border/50 px-4 py-2 rounded-2xl">
                                            <span className="w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]" />
                                            <span className="text-muted-foreground uppercase text-[10px] tracking-widest">Domain:</span>
                                            {project.domain || "AI Project"}
                                        </div>
                                        <div className="flex items-center gap-2 bg-background/50 border border-border/50 px-4 py-2 rounded-2xl">
                                            <span className="w-2 h-2 rounded-full bg-orange-400 shadow-[0_0_8px_rgba(251,146,60,0.5)]" />
                                            <span className="text-muted-foreground uppercase text-[10px] tracking-widest">Difficulty:</span>
                                            {project.difficulty || "Intermediate"}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="p-8 md:p-12 grid grid-cols-1 md:grid-cols-2 gap-12">
                                <div className="space-y-8">
                                    <div className="space-y-4">
                                        <h3 className="text-sm font-black uppercase tracking-[0.2em] text-primary flex items-center gap-3">
                                            <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                                                <FileText className="w-4 h-4" />
                                            </div>
                                            Abstract
                                        </h3>
                                        <div className="prose prose-sm max-w-none">
                                            <p className="text-base leading-relaxed text-foreground/80 font-medium">{project.abstract}</p>
                                        </div>
                                    </div>

                                    {project.features && project.features.length > 0 && (
                                        <div className="space-y-4">
                                            <h3 className="text-sm font-black uppercase tracking-[0.2em] text-emerald-500 flex items-center gap-3">
                                                <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                                                    <Sparkles className="w-4 h-4" />
                                                </div>
                                                Key Features
                                            </h3>
                                            <ul className="grid grid-cols-1 gap-2">
                                                {project.features.map((f: string, i: number) => (
                                                    <li key={i} className="flex items-center gap-2 text-sm text-foreground/70 font-medium bg-muted/30 px-3 py-2 rounded-xl border border-border/40">
                                                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                                                        {f}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}

                                    {project.literature_survey && (
                                        <div className="space-y-4">
                                            <h3 className="text-sm font-black uppercase tracking-[0.2em] text-blue-500 flex items-center gap-3">
                                                <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center">
                                                    <BookOpen className="w-4 h-4" />
                                                </div>
                                                Literature Survey
                                            </h3>
                                            <div className="prose prose-sm max-w-none p-4 rounded-2xl bg-blue-500/5 border border-blue-500/10">
                                                <p className="text-sm leading-relaxed text-foreground/80 italic font-medium">"{project.literature_survey}"</p>
                                            </div>
                                        </div>
                                    )}
                                </div>

                                <div className="space-y-8">
                                    <div className="space-y-4">
                                        <h3 className="text-sm font-black uppercase tracking-[0.2em] text-accent flex items-center gap-3">
                                            <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center">
                                                <Layers className="w-4 h-4" />
                                            </div>
                                            Technical Architecture
                                        </h3>
                                        <div className="prose prose-sm max-w-none">
                                            <p className="text-base leading-relaxed text-foreground/80 font-medium">{project.architecture_description}</p>
                                        </div>
                                    </div>

                                    {project.database_design && (
                                        <div className="space-y-4">
                                            <h3 className="text-sm font-black uppercase tracking-[0.2em] text-orange-500 flex items-center gap-3">
                                                <div className="w-8 h-8 rounded-lg bg-orange-500/10 flex items-center justify-center">
                                                    <Database className="w-4 h-4" />
                                                </div>
                                                Database Blueprint
                                            </h3>
                                            <div className="p-4 rounded-2xl bg-orange-500/5 border border-orange-500/10 text-xs font-mono text-foreground/80 overflow-x-auto">
                                                <pre className="whitespace-pre-wrap">{project.database_design}</pre>
                                            </div>
                                        </div>
                                    )}

                                    {project.methodology && (
                                        <div className="space-y-4">
                                            <h3 className="text-sm font-black uppercase tracking-[0.2em] text-purple-500 flex items-center gap-3">
                                                <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center">
                                                    <Cpu className="w-4 h-4" />
                                                </div>
                                                Methodology
                                            </h3>
                                            <div className="prose prose-sm max-w-none">
                                                <p className="text-sm leading-relaxed text-foreground/70 font-medium">{project.methodology}</p>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>

                            <div className="p-8 md:p-12 bg-muted/10 border-t flex flex-col md:flex-row gap-6">
                                <div className="flex-1 space-y-4">
                                    <div className="flex items-center justify-between">
                                        <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest ml-1">Download Professional Assets</p>
                                        <span className="text-[10px] font-black bg-primary/20 text-primary px-2 py-0.5 rounded-md uppercase">High-Quality Output</span>
                                    </div>
                                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                                        <DownloadButton
                                            label="Full Report"
                                            filename="project_report.docx"
                                            onClick={() => api.downloadReport(project.id)}
                                            className="h-14 rounded-2xl font-bold bg-zinc-900 hover:bg-zinc-800 text-white border border-white/10 shadow-sm transition-all hover:scale-[1.02]"
                                        />
                                        <DownloadButton
                                            label="PPT Presentation"
                                            filename="project_presentation.pptx"
                                            onClick={() => api.downloadPPT(project.id)}
                                            className="h-14 rounded-2xl font-bold bg-zinc-900 hover:bg-zinc-800 text-white border border-white/10 shadow-sm transition-all hover:scale-[1.02]"
                                        />
                                        <DownloadButton
                                            label="Production Code"
                                            filename="project_code.zip"
                                            onClick={() => api.downloadCode(project.id)}
                                            className="h-14 rounded-2xl font-bold bg-primary text-primary-foreground hover:opacity-90 border-none shadow-lg shadow-primary/20 transition-all hover:scale-[1.02]"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Viva Assistant */}
                        <div className="pt-4">
                            <VivaAssistant projectData={project} />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
