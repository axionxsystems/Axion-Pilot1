"use client";

import { useState } from "react";
import ProjectForm from "../../components/ProjectForm";
import AuthGuard from "../../components/AuthGuard";
import { useAuth } from "../../components/AuthProvider";
import VivaAssistant from "../../components/VivaAssistant";
import DownloadButton from "../../components/DownloadButton";
import { api } from "../../services/api";
import Link from "next/link";
import { LogOut, Sparkles, FileText, Download, Code, MonitorPlay, Settings } from "lucide-react";

export default function Dashboard() {
    const [project, setProject] = useState<any>(null);
    const { user } = useAuth();

    return (
        <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-5 duration-700">
            {/* Header Area */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-border/40 pb-6">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-foreground">Dashboard</h1>
                    <p className="text-muted-foreground mt-1">Welcome back, {user?.name || user?.email?.split('@')[0] || 'Creator'}</p>
                </div>
                <div className="flex items-center gap-2">
                    <Link href="/dashboard/new">
                        <div className="bg-primary text-primary-foreground hover:bg-primary/90 px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 shadow-sm">
                            <Sparkles className="w-4 h-4" />
                            New Project
                        </div>
                    </Link>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Left Column: Form */}
                <div className="lg:col-span-4 space-y-6">
                    <div className="rounded-xl border bg-card text-card-foreground shadow-sm">
                        <div className="p-6">
                            <h2 className="text-lg font-semibold mb-2">Generate Project</h2>
                            <p className="text-sm text-muted-foreground mb-6">Describe your idea to generate a complete project bundle.</p>
                            <ProjectForm onProjectGenerated={setProject} />
                        </div>
                    </div>
                </div>

                {/* Right Column: Result */}
                <div className="lg:col-span-8">
                    {project ? (
                        <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-500">
                            <div className="rounded-xl border bg-card text-card-foreground shadow-sm overflow-hidden">
                                <div className="p-6 border-b bg-muted/30">
                                    <div className="flex justify-between items-start mb-4">
                                        <h2 className="text-2xl font-bold leading-tight">{project.title}</h2>
                                        <span className="px-2.5 py-0.5 rounded-full bg-primary/10 text-primary text-xs font-semibold border border-primary/20">
                                            Generated
                                        </span>
                                    </div>
                                    <div className="flex gap-4 text-sm text-muted-foreground">
                                        <span className="flex items-center gap-1.5">
                                            <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                                            {project.domain || "AI Project"}
                                        </span>
                                        <span className="flex items-center gap-1.5">
                                            <span className="w-1.5 h-1.5 rounded-full bg-orange-400" />
                                            {project.difficulty || "Intermediate"}
                                        </span>
                                    </div>
                                </div>

                                <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
                                    <div className="space-y-2">
                                        <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                                            <FileText className="w-4 h-4" />
                                            Abstract
                                        </h3>
                                        <p className="text-sm leading-relaxed text-foreground/80">{project.abstract}</p>
                                    </div>
                                    <div className="space-y-2">
                                        <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                                            <Layers className="w-4 h-4" />
                                            Architecture
                                        </h3>
                                        <p className="text-sm leading-relaxed text-foreground/80">{project.architecture_description}</p>
                                    </div>
                                </div>

                                <div className="p-6 bg-muted/20 border-t flex flex-col sm:flex-row gap-4">
                                    <DownloadButton
                                        label="Report"
                                        filename="project_report.docx"
                                        onClick={() => api.downloadReport(project)}
                                        className="flex-1"
                                    />
                                    <DownloadButton
                                        label="PPT"
                                        filename="project_presentation.pptx"
                                        onClick={() => api.downloadPPT(project)}
                                        className="flex-1"
                                    />
                                    <DownloadButton
                                        label="Code"
                                        filename="project_code.zip"
                                        onClick={() => api.downloadCode(project)}
                                        className="flex-1"
                                    />
                                </div>
                            </div>

                            {/* Viva Assistant */}
                            <VivaAssistant projectData={project} />
                        </div>
                    ) : (
                        <div className="h-full min-h-[400px] rounded-xl border-2 border-dashed border-muted-foreground/20 bg-muted/5 flex flex-col items-center justify-center text-center p-12">
                            <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
                                <MonitorPlay className="w-8 h-8 text-muted-foreground" />
                            </div>
                            <h3 className="text-lg font-medium mb-1">No Project Generated</h3>
                            <p className="text-sm text-muted-foreground max-w-sm">
                                Use the generator form to create your next AI project.
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

// Icon for architecture
function Layers(props: any) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z" />
            <path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65" />
            <path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65" />
        </svg>
    )
}
