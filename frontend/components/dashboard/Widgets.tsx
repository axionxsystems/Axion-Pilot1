"use client";

import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { 
    Sparkles, 
    FileText, 
    Presentation, 
    MessageSquare, 
    Briefcase, 
    Activity, 
    Clock, 
    ChevronRight, 
    Rocket,
    Plus,
    History,
    FileSearch,
    Cpu,
    MonitorIcon,
    TerminalSquare
} from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

// --- Helper for Count-up animation ---
function CountUp({ value, duration = 1000 }: { value: number | string, duration?: number }) {
    const [count, setCount] = useState(0);
    const target = typeof value === 'string' ? parseInt(value) || 0 : value;

    useEffect(() => {
        let startTime: number | null = null;
        const animate = (timestamp: number) => {
            if (!startTime) startTime = timestamp;
            const progress = Math.min((timestamp - startTime) / duration, 1);
            setCount(Math.floor(progress * target));
            if (progress < 1) requestAnimationFrame(animate);
        };
        requestAnimationFrame(animate);
    }, [target, duration]);

    return <span>{count}</span>;
}

export function StatsSection({ data }: { data: any }) {
    const stats = [
        { label: "Projects Generated", value: data?.projects_generated || 0, icon: Briefcase, color: "text-blue-400", glow: "shadow-blue-500/20", bg: "bg-blue-500/10", border: "border-blue-500/20" },
        { label: "Reports Created", value: data?.reports_created || 0, icon: FileText, color: "text-purple-400", glow: "shadow-purple-500/20", bg: "bg-purple-500/10", border: "border-purple-500/20" },
        { label: "Presentations", value: data?.presentations_created || 0, icon: Presentation, color: "text-pink-400", glow: "shadow-pink-500/20", bg: "bg-pink-500/10", border: "border-pink-500/20" },
        { label: "Viva Questions", value: data?.viva_questions || 0, icon: MessageSquare, color: "text-emerald-400", glow: "shadow-emerald-500/20", bg: "bg-emerald-500/10", border: "border-emerald-500/20" },
    ];

    return (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-5 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {stats.map((stat, i) => (
                <div 
                    key={i} 
                    className="relative group bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.08)] backdrop-blur-xl rounded-[2rem] p-6 transition-all duration-300 hover:translate-y-[-5px] hover:scale-[1.02] hover:border-[rgba(255,255,255,0.15)] hover:shadow-[0_20px_40px_-15px_rgba(0,0,0,0.3)] overflow-hidden"
                >
                    <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-white/[0.02] to-transparent rounded-full -mr-12 -mt-12 transition-transform group-hover:scale-150 duration-700" />
                    
                    <div className="flex flex-col gap-4 relative z-10">
                        <div className={cn("p-3 w-fit rounded-2xl border transition-all duration-300 group-hover:scale-110 group-hover:shadow-[0_0_20px_rgba(0,0,0,0.2)]", stat.bg, stat.border, stat.glow)}>
                            <stat.icon className={cn("w-6 h-6", stat.color)} />
                        </div>
                        <div>
                            <h3 className="text-3xl font-black text-white tracking-tighter">
                                <CountUp value={stat.value} />
                            </h3>
                            <p className="text-[11px] text-zinc-500 font-bold uppercase tracking-[2px] mt-1">{stat.label}</p>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
}

export function ActivityFeed() {
    const activities = [
        { text: "Generated abstract for Face Recognition", time: "2m ago", icon: FileText, color: "text-blue-400", bg: "bg-blue-500/10" },
        { text: "Compiled React codebase", time: "15m ago", icon: Briefcase, color: "text-purple-400", bg: "bg-purple-500/10" },
        { text: "Created 12 Viva questions", time: "1h ago", icon: MessageSquare, color: "text-emerald-400", bg: "bg-emerald-500/10" },
        { text: "Designed PPT for Blockchain system", time: "3h ago", icon: Presentation, color: "text-pink-400", bg: "bg-pink-500/10" }
    ];

    return (
        <div className="bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.08)] backdrop-blur-xl rounded-[2.5rem] p-8 shadow-2xl flex flex-col h-full group/main transition-all duration-300 hover:border-white/10 overflow-hidden">
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                    <div className="p-2 rounded-xl bg-primary/10 border border-primary/20">
                        <Activity className="w-5 h-5 text-primary" />
                    </div>
                    <h3 className="text-xl font-black text-white tracking-tight">AI Activity</h3>
                </div>
                <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
            </div>

            <div className="space-y-0 flex-1 relative">
                {/* Vertical Timeline Line */}
                <div className="absolute left-[19px] top-4 bottom-4 w-px bg-gradient-to-b from-primary/50 via-primary/10 to-transparent" />
                
                {activities.map((act, i) => (
                    <div key={i} className="flex gap-5 group items-start pb-8 last:pb-0 relative">
                        <div className="relative z-10">
                            <div className={cn("w-10 h-10 rounded-2xl flex items-center justify-center transition-all duration-300 border border-white/5 group-hover:scale-110 group-hover:shadow-[0_0_15px_rgba(0,0,0,0.2)]", act.bg)}>
                                <act.icon className={cn("w-4 h-4", act.color)} />
                            </div>
                        </div>
                        <div className="pt-1.5 transition-all duration-300 group-hover:translate-x-1 flex-1 min-w-0">
                            <p className="text-sm font-bold text-zinc-200 leading-tight group-hover:text-white transition-colors truncate">{act.text}</p>
                            <span className="text-[10px] text-zinc-500 font-bold uppercase tracking-wider flex items-center gap-1.5 mt-2">
                                <Clock className="w-3 h-3" />
                                {act.time}
                            </span>
                        </div>
                        {i === 0 && (
                            <div className="absolute right-0 top-1 px-2 py-0.5 rounded-md bg-blue-500/10 border border-blue-500/20 text-[9px] font-black text-blue-400 tracking-tighter uppercase animate-pulse">
                                Newest
                            </div>
                        )}
                    </div>
                ))}
                
                {/* Scroll Fade Effect at bottom */}
                <div className="absolute bottom-0 left-0 w-full h-12 bg-gradient-to-t from-[rgba(10,13,20,0.5)] to-transparent pointer-events-none" />
            </div>
            
            <Button variant="ghost" className="w-full mt-8 rounded-2xl bg-white/[0.03] border border-white/5 text-zinc-400 hover:text-white hover:bg-white/10 transition-all font-bold text-xs tracking-widest gap-2">
                VIEW HISTORY
                <ChevronRight className="w-4 h-4" />
            </Button>
        </div>
    );
}

export function SuggestionPanel() {
    const suggestions = [
        { title: "AI Resume Analyzer", domain: "Machine Learning", diff: "Intermediate", icon: MonitorIcon, color: "text-blue-400" },
        { title: "Blockchain Voting System", domain: "Blockchain", diff: "Advanced", icon: TerminalSquare, color: "text-purple-400" },
        { title: "IoT Smart Agriculture", domain: "IoT", diff: "Beginner", icon: Cpu, color: "text-emerald-400" }
    ];

    return (
        <div className="bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.08)] backdrop-blur-xl rounded-[2.5rem] p-8 shadow-2xl transition-all duration-300 hover:border-white/10">
            <div className="flex items-center gap-3 mb-8">
                <div className="p-2 rounded-xl bg-orange-500/10 border border-orange-500/20">
                    <Sparkles className="w-5 h-5 text-orange-400" />
                </div>
                <h3 className="text-xl font-black text-white tracking-tight">AI Insights</h3>
            </div>
            <div className="space-y-4">
                {suggestions.map((sug, i) => (
                    <button key={i} className="w-full text-left bg-white/[0.02] border border-white/5 rounded-3xl p-5 hover:bg-white/[0.05] hover:border-white/10 transition-all duration-300 group flex items-center gap-4">
                        <div className="p-3 rounded-2xl bg-white/5 border border-white/5 group-hover:scale-110 transition-all duration-500">
                            <sug.icon className={cn("w-5 h-5", sug.color)} />
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="font-bold text-zinc-200 text-sm leading-tight group-hover:text-white transition-colors truncate">{sug.title}</p>
                            <div className="flex items-center gap-2 mt-2">
                                <span className="text-[9px] uppercase font-black text-zinc-500 tracking-tighter bg-white/5 px-2 py-0.5 rounded-md border border-white/5 truncate">{sug.domain}</span>
                                <span className="text-[9px] uppercase font-black text-zinc-500 tracking-tighter bg-white/5 px-2 py-0.5 rounded-md border border-white/5 uppercase shrink-0">{sug.diff}</span>
                            </div>
                        </div>
                        <div className="p-2 rounded-xl bg-white/5 opacity-0 group-hover:opacity-100 transition-all duration-300">
                            <ChevronRight className="w-4 h-4 text-white" />
                        </div>
                    </button>
                ))}
            </div>
        </div>
    );
}

export function RecentProjectsList({ projects }: { projects: any[] }) {
    return (
        <div className="bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.08)] backdrop-blur-xl rounded-[2.5rem] p-8 shadow-2xl transition-all duration-300 hover:border-white/10">
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                    <div className="p-2 rounded-xl bg-blue-500/10 border border-blue-500/20">
                        <Briefcase className="w-5 h-5 text-blue-400" />
                    </div>
                    <h3 className="text-xl font-black text-white tracking-tight">Recent Projects</h3>
                </div>
                <Link href="/dashboard/projects" className="text-[10px] font-black text-zinc-500 hover:text-white uppercase tracking-widest bg-white/5 px-3 py-1.5 rounded-xl border border-white/5 transition-all">
                    All Projects
                </Link>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {(projects || []).slice(0, 2).map((proj, i) => (
                    <div key={proj.id} className="bg-white/[0.02] border border-white/5 rounded-3xl p-6 hover:border-blue-500/30 hover:bg-white/[0.04] transition-all duration-300 group relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-16 h-16 bg-blue-500/5 blur-2xl group-hover:bg-blue-500/10 transition-all" />
                        
                        <div className="flex justify-between items-start mb-6 gap-3">
                            <h4 className="font-bold text-zinc-200 line-clamp-1 group-hover:text-white transition-colors flex-1 min-w-0">{proj.title}</h4>
                            <span className="text-[9px] font-black uppercase tracking-[1px] px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.15)] shrink-0">
                                READY
                            </span>
                        </div>
                        
                        <div className="space-y-3">
                            <div className="flex justify-between items-center text-[10px] text-zinc-500 font-black uppercase tracking-wider">
                                <span className="truncate mr-2">Optimization</span>
                                <span className="text-emerald-400 shrink-0">100%</span>
                            </div>
                            <div className="w-full bg-white/5 rounded-full h-1.5 overflow-hidden">
                                <div className="h-full rounded-full bg-gradient-to-r from-emerald-600 to-emerald-400 w-full shadow-[0_0_10px_rgba(16,185,129,0.3)] animate-in slide-in-from-left duration-1000" />
                            </div>
                        </div>
                        
                        <Link href={`/dashboard/projects/${proj.id}`} className="block mt-6">
                            <Button variant="outline" className="w-full rounded-2xl bg-white/5 border-white/10 hover:bg-blue-500 hover:text-white hover:border-blue-500 font-bold text-xs tracking-tight transition-all duration-300 group/btn px-4 py-2 h-auto min-h-[40px]">
                                <span className="truncate">Open Workspace</span>
                                <ArrowRight className="w-3.5 h-3.5 ml-2 group-hover/btn:translate-x-1 transition-transform shrink-0" />
                            </Button>
                        </Link>
                    </div>
                ))}
                
                {(!projects || projects.length === 0) && (
                    <div className="col-span-2 py-12 flex flex-col items-center justify-center text-center space-y-4 bg-white/[0.02] border border-white/5 border-dashed rounded-3xl">
                        <div className="p-4 rounded-full bg-white/5 border border-white/10">
                            <FileSearch className="w-8 h-8 text-zinc-600" />
                        </div>
                        <div>
                            <p className="text-sm font-bold text-zinc-400 tracking-tight">No projects created yet</p>
                            <p className="text-[10px] text-zinc-600 font-medium mt-1">Start by clicking the "Launch Generator" button</p>
                        </div>
                        <Button 
                            onClick={() => document.getElementById('project-form')?.scrollIntoView({ behavior: 'smooth' })}
                            className="bg-primary text-primary-foreground font-black text-xs rounded-xl shadow-lg shadow-primary/20 hover:scale-[1.05] transition-all px-6"
                        >
                            <Plus className="w-4 h-4 mr-1" />
                            CREATE FIRST PROJECT
                        </Button>
                    </div>
                )}
            </div>
        </div>
    );
}

export function ProjectProgressTracker() {
    const trackerStages = [
        { name: "Global Moderation", progress: 100, color: "from-blue-600 to-blue-400", glow: "shadow-blue-500/20" },
        { name: "Asset Optimization", progress: 95, color: "from-purple-600 to-purple-400", glow: "shadow-purple-500/20" },
        { name: "Live Sandbox", progress: 80, color: "from-emerald-600 to-emerald-400", glow: "shadow-emerald-500/20" },
    ];

    return (
        <div className="bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.08)] backdrop-blur-xl rounded-[2.5rem] p-8 shadow-2xl transition-all duration-300 hover:border-white/10">
            <div className="flex items-center gap-3 mb-8">
                <div className="p-2 rounded-xl bg-primary/10 border border-primary/20">
                    <Rocket className="w-5 h-5 text-primary" />
                </div>
                <h3 className="text-xl font-black text-white tracking-tight">Platform Vitals</h3>
            </div>
            <div className="space-y-8">
                {trackerStages.map((stage, i) => (
                    <div key={i} className="space-y-3 group">
                        <div className="flex justify-between items-end">
                            <span className="text-sm font-bold text-zinc-300 group-hover:text-white transition-colors">{stage.name}</span>
                            <span className="text-[11px] font-black text-zinc-500 tabular-nums">{stage.progress}%</span>
                        </div>
                        <div className="relative w-full bg-white/5 rounded-full h-2.5 overflow-hidden">
                            <div 
                                className={cn("absolute inset-y-0 left-0 h-full rounded-full bg-gradient-to-r transition-all duration-1000 ease-out", stage.color, stage.glow)}
                                style={{ width: `${stage.progress}%` }}
                            >
                                {/* Glow ending tip */}
                                <div className="absolute right-0 top-0 bottom-0 w-2 bg-white/40 blur-sm" />
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

// Additional icons for imports
function ArrowRight({ className }: { className?: string }) {
    return <ChevronRight className={className} />;
}
