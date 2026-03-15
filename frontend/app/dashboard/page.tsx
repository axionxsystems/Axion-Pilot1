"use client";

import { useState } from "react";
import ProjectForm from "../../components/ProjectForm";
import AuthGuard from "../../components/AuthGuard";
import { useAuth } from "../../components/AuthProvider";
import VivaAssistant from "../../components/VivaAssistant";
import DownloadButton from "../../components/DownloadButton";
import { StatsSection, ActivityFeed, SuggestionPanel, RecentProjectsList, ProjectProgressTracker } from "../../components/dashboard/Widgets";
import { api } from "../../services/api";
import Link from "next/link";
import { LogOut, Sparkles, FileText, Download, Code, MonitorPlay, Settings, Layers, ArrowRight, Clock } from "lucide-react";

export default function Dashboard() {
    const [project, setProject] = useState<any>(null);
    const { user } = useAuth();

    return (
        <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-5 duration-700">
            {/* Header Area */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-border/40 pb-8">
                <div>
                    <h1 className="text-4xl font-extrabold tracking-tight text-foreground bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                        Dashboard
                    </h1>
                    <p className="text-muted-foreground mt-2 text-lg">
                        Welcome back, <span className="text-foreground font-semibold">{user?.name || user?.email?.split('@')[0] || 'Creator'}</span>
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <button className="bg-background border border-border/50 text-foreground hover:bg-muted/50 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all flex items-center gap-2 shadow-sm">
                        <Settings className="w-4 h-4" />
                        Settings
                    </button>
                    <Link href="/dashboard/new">
                        <div className="bg-primary text-primary-foreground hover:bg-primary/90 px-6 py-2.5 rounded-xl text-sm font-bold transition-all flex items-center gap-2 shadow-lg shadow-primary/20 hover:scale-[1.02] active:scale-[0.98]">
                            <Sparkles className="w-4 h-4" />
                            New Project
                        </div>
                    </Link>
                </div>
            </div>

            {!project ? (
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-8 pb-12">
                    <div className="lg:col-span-8 space-y-8">
                        <StatsSection />
                        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                            <RecentProjectsList />
                            <ProjectProgressTracker />
                        </div>
                        <div className="mt-8">
                            <ProjectForm onProjectGenerated={setProject} />
                        </div>
                    </div>
                    <div className="lg:col-span-4 h-full space-y-8">
                        <ActivityFeed />
                        <SuggestionPanel />
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
                                <div className="space-y-4">
                                    <h3 className="text-sm font-black uppercase tracking-[0.2em] text-accent flex items-center gap-3">
                                        <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center">
                                            <Layers className="w-4 h-4" />
                                        </div>
                                        Architecture
                                    </h3>
                                    <div className="prose prose-sm max-w-none">
                                        <p className="text-base leading-relaxed text-foreground/80 font-medium">{project.architecture_description}</p>
                                    </div>
                                </div>
                            </div>

                            <div className="p-8 md:p-12 bg-muted/10 border-t flex flex-col md:flex-row gap-6">
                                <div className="flex-1 space-y-4">
                                    <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest ml-1">Download Assets</p>
                                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                                        <DownloadButton
                                            label="Project Report"
                                            filename="project_report.docx"
                                            onClick={() => api.downloadReport(project)}
                                            className="h-14 rounded-2xl font-bold bg-white hover:bg-muted text-foreground border-border/50 shadow-sm"
                                        />
                                        <DownloadButton
                                            label="Presentation"
                                            filename="project_presentation.pptx"
                                            onClick={() => api.downloadPPT(project)}
                                            className="h-14 rounded-2xl font-bold bg-white hover:bg-muted text-foreground border-border/50 shadow-sm"
                                        />
                                        <DownloadButton
                                            label="Source Code"
                                            filename="project_code.zip"
                                            onClick={() => api.downloadCode(project)}
                                            className="h-14 rounded-2xl font-bold bg-primary text-primary-foreground hover:opacity-90 border-none shadow-lg shadow-primary/20"
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
