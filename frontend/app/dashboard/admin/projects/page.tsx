"use client";

import { useState, useEffect } from "react";
import { api } from "../../../../services/api";
import { 
    Layers, 
    Search, 
    User, 
    Calendar, 
    Tag, 
    Trash2, 
    ExternalLink, 
    Filter,
    Loader2,
    CheckCircle2,
    Clock,
    Download,
    BarChart2,
    Zap
} from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

export default function ProjectMonitoringPage() {
    const [projects, setProjects] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [selectedDomain, setSelectedDomain] = useState("all");
    const [selectedDifficulty, setSelectedDifficulty] = useState("all");
    const [error, setError] = useState<string | null>(null);

    const fetchProjects = async () => {
        try {
            const data = await api.adminListAllProjects();
            setProjects(data);
        } catch (err: any) {
            setError(err.message || "Failed to load projects");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchProjects();
    }, []);

    const deleteProject = async (id: number) => {
        if (!confirm("Are you sure you want to delete this project permanently?")) return;
        try {
            await api.adminDeleteProject(id);
            setProjects(projects.filter(p => p.id !== id));
        } catch (err: any) {
            alert(err.message);
        }
    };

    const downloadReport = async (p: any) => {
        try {
            const blob = await api.downloadReport(p.data);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `${p.title}_Report.docx`;
            a.click();
        } catch (err: any) {
            alert(err.message);
        }
    };

    const domains = Array.from(new Set(projects.map(p => p.domain)));
    const filteredProjects = projects.filter(p => {
        const matchesSearch = p.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                             p.user_email.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesDomain = selectedDomain === "all" || p.domain === selectedDomain;
        const matchesDiff = selectedDifficulty === "all" || p.difficulty === selectedDifficulty;
        return matchesSearch && matchesDomain && matchesDiff;
    });

    if (loading) return <div className="h-[60vh] flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;

    return (
        <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Header Area */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div>
                    <h1 className="text-3xl font-black text-foreground">Global Project Monitoring</h1>
                    <p className="text-muted-foreground mt-1 font-medium">Full platform visibility of generated content.</p>
                </div>
                <div className="flex items-center gap-4 bg-card border border-border/50 rounded-2xl p-2 px-4 shadow-sm">
                    <div className="flex items-center gap-2">
                        <Zap className="w-4 h-4 text-primary animate-pulse" />
                        <span className="text-xs font-black uppercase tracking-widest text-foreground">{projects.length} Total Projects</span>
                    </div>
                </div>
            </div>

            {/* Controls Bar */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
                <div className="md:col-span-4 relative group">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                    <input 
                        type="text"
                        placeholder="Search title or owner email..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-11 pr-4 py-3 bg-card border border-border/50 rounded-2xl outline-none focus:ring-2 focus:ring-primary/20 transition-all font-medium"
                    />
                </div>
                <div className="md:col-span-3">
                    <select 
                        value={selectedDomain}
                        onChange={(e) => setSelectedDomain(e.target.value)}
                        className="w-full px-4 py-3 bg-card border border-border/50 rounded-2xl outline-none font-medium appearance-none cursor-pointer hover:bg-muted/30 transition-colors"
                    >
                        <option value="all">All Domains</option>
                        {domains.map(d => <option key={d} value={d}>{d}</option>)}
                    </select>
                </div>
                <div className="md:col-span-3">
                    <select 
                        value={selectedDifficulty}
                        onChange={(e) => setSelectedDifficulty(e.target.value)}
                        className="w-full px-4 py-3 bg-card border border-border/50 rounded-2xl outline-none font-medium appearance-none cursor-pointer hover:bg-muted/30 transition-colors"
                    >
                        <option value="all">All Difficulties</option>
                        <option value="Beginner">Beginner</option>
                        <option value="Intermediate">Intermediate</option>
                        <option value="Advanced">Advanced</option>
                    </select>
                </div>
                <div className="md:col-span-2">
                    <button 
                        onClick={fetchProjects}
                        className="w-full h-full bg-primary text-primary-foreground font-bold rounded-2xl hover:scale-[1.02] shadow-sm transition-all flex items-center justify-center gap-2"
                    >
                        <BarChart2 className="w-4 h-4" /> Refresh
                    </button>
                </div>
            </div>

            {/* Projects Table */}
            <div className="bg-card border border-border/50 rounded-[2.5rem] shadow-sm overflow-hidden min-h-[400px]">
                {filteredProjects.length === 0 ? (
                    <div className="p-20 text-center flex flex-col items-center gap-4">
                        <div className="w-16 h-16 rounded-3xl bg-muted/50 flex items-center justify-center text-muted-foreground">
                            <Filter className="w-8 h-8" />
                        </div>
                        <p className="font-bold text-muted-foreground">No projects match your filters.</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="border-b border-border/40 bg-muted/30">
                                    <th className="px-6 py-5 text-xs font-black uppercase tracking-widest text-muted-foreground w-1/3">Project & Owner</th>
                                    <th className="px-6 py-5 text-xs font-black uppercase tracking-widest text-muted-foreground">Context</th>
                                    <th className="px-6 py-5 text-xs font-black uppercase tracking-widest text-muted-foreground">Generated On</th>
                                    <th className="px-6 py-5 text-xs font-black uppercase tracking-widest text-muted-foreground text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-border/40">
                                {filteredProjects.map((p) => (
                                    <tr key={p.id} className="hover:bg-muted/20 transition-colors group">
                                        <td className="px-6 py-5">
                                            <div className="flex flex-col gap-1">
                                                <p className="text-sm font-black text-foreground group-hover:text-primary transition-colors">{p.title}</p>
                                                <div className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground uppercase tracking-wider">
                                                    <User className="w-3 h-3" />
                                                    {p.user_email}
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="flex flex-col gap-2">
                                                <div className="flex items-center gap-3">
                                                    <span className="px-2 py-0.5 bg-primary/10 text-primary text-[10px] font-black tracking-widest uppercase rounded-lg border border-primary/20">{p.domain}</span>
                                                    <span className={cn(
                                                        "px-2 py-0.5 text-[10px] font-black tracking-widest uppercase rounded-lg border",
                                                        p.difficulty === 'Beginner' ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' :
                                                        p.difficulty === 'Intermediate' ? 'bg-blue-500/10 text-blue-500 border-blue-500/20' :
                                                        'bg-destructive/10 text-destructive border-destructive/20'
                                                    )}>
                                                        {p.difficulty}
                                                    </span>
                                                </div>
                                                <p className="text-[10px] text-muted-foreground/60 font-bold max-w-[200px] truncate">{p.tech_stack}</p>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="flex items-center gap-2 text-xs font-bold text-muted-foreground">
                                                <Clock className="w-3.5 h-3.5" />
                                                {format(new Date(p.created_at), 'MMM dd, HH:mm')}
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="flex items-center justify-end gap-2">
                                                <button 
                                                    onClick={() => downloadReport(p)}
                                                    className="p-2 rounded-xl border border-border/80 hover:bg-muted/50 text-muted-foreground transition-all"
                                                    title="Download Report Preview"
                                                >
                                                    <Download className="w-4 h-4" />
                                                </button>
                                                <button 
                                                    onClick={() => deleteProject(p.id)}
                                                    className="p-2 rounded-xl border border-destructive/20 text-destructive hover:bg-destructive hover:text-white transition-all shadow-sm"
                                                    title="Delete Project"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}
