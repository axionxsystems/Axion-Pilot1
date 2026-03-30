"use client";

import { useState, useEffect } from "react";
import { api } from "../../../services/api";
import { 
    Search, 
    Filter, 
    Layers, 
    Clock, 
    Trash2, 
    Download, 
    Eye, 
    FileText, 
    ChevronRight,
    Loader2
} from "lucide-react";
import Link from "next/link";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

export default function MyProjectsPage() {
    const [projects, setProjects] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    const [domainFilter, setDomainFilter] = useState("All");
    const [difficultyFilter, setDifficultyFilter] = useState("All");

    useEffect(() => {
        const fetchProjects = async () => {
            try {
                const data = await api.listProjects();
                setProjects(data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchProjects();
    }, []);

    const handleDelete = async (id: number) => {
        if (!confirm("Delete this project? This cannot be undone.")) return;
        try {
            await api.deleteProject(id);
            setProjects(projects.filter(p => p.id !== id));
        } catch (err: any) {
            alert(err.message);
        }
    };

    const filteredProjects = projects.filter(p => {
        const matchesSearch = p.title.toLowerCase().includes(search.toLowerCase());
        const matchesDomain = domainFilter === "All" || p.domain === domainFilter;
        const matchesDiff = difficultyFilter === "All" || p.difficulty === difficultyFilter;
        return matchesSearch && matchesDomain && matchesDiff;
    });

    const domains = ["All", ...Array.from(new Set(projects.map(p => p.domain)))];

    return (
        <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 pb-20">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div>
                    <h1 className="text-3xl font-black text-foreground">My Creative Vault</h1>
                    <p className="text-muted-foreground mt-1 font-medium">Manage and explore your generated masterpieces.</p>
                </div>
                
                <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
                    <div className="relative flex-grow md:flex-grow-0">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <input 
                            type="text" 
                            placeholder="Search projects..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="bg-card border border-border/50 rounded-xl py-2.5 pl-10 pr-4 text-sm font-medium w-full md:w-64 focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                        />
                    </div>
                </div>
            </div>

            <div className="flex flex-wrap gap-4 items-center">
                <div className="flex items-center gap-2 bg-card border border-border/50 rounded-xl p-1 px-3">
                    <Filter className="w-3.5 h-3.5 text-muted-foreground" />
                    <select 
                        value={domainFilter}
                        onChange={(e) => setDomainFilter(e.target.value)}
                        className="bg-transparent text-foreground text-xs font-bold uppercase tracking-widest outline-none py-1.5 cursor-pointer"
                    >
                        {domains.map(d => <option key={d} value={d} className="bg-background text-foreground">{d}</option>)}
                    </select>
                </div>
                <div className="flex items-center gap-2 bg-card border border-border/50 rounded-xl p-1 px-3">
                    <Layers className="w-3.5 h-3.5 text-muted-foreground" />
                    <select 
                        value={difficultyFilter}
                        onChange={(e) => setDifficultyFilter(e.target.value)}
                        className="bg-transparent text-foreground text-xs font-bold uppercase tracking-widest outline-none py-1.5 cursor-pointer"
                    >
                        <option value="All" className="bg-background text-foreground">All Levels</option>
                        <option value="Beginner" className="bg-background text-foreground">Beginner</option>
                        <option value="Intermediate" className="bg-background text-foreground">Intermediate</option>
                        <option value="Advanced" className="bg-background text-foreground">Advanced</option>
                    </select>
                </div>
            </div>

            {loading ? (
                <div className="h-[40vh] flex items-center justify-center">
                    <Loader2 className="w-8 h-8 animate-spin text-primary" />
                </div>
            ) : filteredProjects.length === 0 ? (
                <div className="bg-card border border-border/50 rounded-[2.5rem] p-20 text-center space-y-4">
                    <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto text-muted-foreground">
                        <Eye className="w-8 h-8 opacity-20" />
                    </div>
                    <p className="text-xl font-black text-foreground">No projects found</p>
                    <p className="text-muted-foreground max-w-sm mx-auto">Try adjusting your filters or search terms to find what you're looking for.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredProjects.map((p) => (
                        <div key={p.id} className="bg-card border border-border/50 rounded-[2.5rem] p-8 shadow-sm hover:shadow-xl hover:shadow-primary/5 hover:border-primary/20 transition-all group animate-in zoom-in-95 duration-300">
                            <div className="flex justify-between items-start mb-6">
                                <span className={cn(
                                    "px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border",
                                    p.status === 'completed' ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' : 
                                    p.status === 'flagged' ? 'bg-destructive/10 text-destructive border-destructive/20' :
                                    'bg-primary/10 text-primary border-primary/20'
                                )}>
                                    {p.status || 'Active'}
                                </span>
                                <div className="flex items-center gap-2 text-xs font-bold text-muted-foreground">
                                    <Clock className="w-3.5 h-3.5" />
                                    {format(new Date(p.created_at), 'MMM dd')}
                                </div>
                            </div>

                            <div className="space-y-4">
                                <h3 className="text-xl font-black text-foreground group-hover:text-primary transition-colors line-clamp-1">
                                    {p.title}
                                </h3>
                                
                                <div className="flex flex-wrap gap-2">
                                    <span className="bg-muted text-[10px] font-black uppercase tracking-tighter px-2.5 py-1 rounded-lg">{p.domain}</span>
                                    <span className={cn(
                                        "text-[10px] font-black uppercase tracking-tighter px-2.5 py-1 rounded-lg border",
                                        p.difficulty === 'Beginner' ? 'border-emerald-500/20 text-emerald-500' :
                                        p.difficulty === 'Intermediate' ? 'border-blue-500/20 text-blue-500' :
                                        'border-destructive/20 text-destructive'
                                    )}>{p.difficulty}</span>
                                </div>

                                <p className="text-xs font-bold text-muted-foreground flex items-center gap-1.5 pt-1">
                                    <Layers className="w-3.5 h-3.5 text-primary/50" />
                                    {p.tech_stack}
                                </p>
                            </div>

                            <div className="mt-8 pt-6 border-t border-border/40 grid grid-cols-2 gap-3">
                                <Link href={`/dashboard/projects/${p.id}`} className="col-span-2">
                                    <button className="w-full py-3 bg-primary text-primary-foreground rounded-2xl font-bold flex items-center justify-center gap-2 hover:scale-[1.02] active:scale-95 transition-all shadow-lg shadow-primary/20">
                                        Open Workspace
                                        <ChevronRight className="w-4 h-4" />
                                    </button>
                                </Link>
                                <button 
                                    onClick={() => api.downloadReport(p)}
                                    className="p-3 bg-muted/50 rounded-xl flex items-center justify-center gap-2 text-xs font-bold hover:bg-muted transition-all"
                                >
                                    <FileText className="w-3.5 h-3.5 text-primary" />
                                    Report
                                </button>
                                <button 
                                    onClick={() => handleDelete(p.id)}
                                    className="p-3 bg-destructive/5 text-destructive rounded-xl flex items-center justify-center gap-2 text-xs font-bold hover:bg-destructive hover:text-white transition-all"
                                >
                                    <Trash2 className="w-3.5 h-3.5" />
                                    Delete
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
