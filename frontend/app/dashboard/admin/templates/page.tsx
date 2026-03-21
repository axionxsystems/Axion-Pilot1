"use client";

import { useState, useEffect } from "react";
import { api } from "../../../../services/api";
import { 
    Layout, 
    Plus, 
    Trash2, 
    Zap, 
    Code, 
    FileText, 
    Layers, 
    Settings, 
    Save, 
    RefreshCw,
    Loader2,
    Calendar,
    Tag,
    AlertCircle
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function TemplateManagerPage() {
    const [templates, setTemplates] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [isCreating, setIsCreating] = useState(false);
    const [newTemplate, setNewTemplate] = useState({
        name: "",
        domain: "AI & Machine Learning",
        tech_stack: "",
        difficulty: "Beginner",
        description: ""
    });

    const fetchTemplates = async () => {
        try {
            const data = await api.adminListTemplates();
            setTemplates(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTemplates();
    }, []);

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await api.adminCreateTemplate(newTemplate);
            setIsCreating(false);
            setNewTemplate({ name: "", domain: "AI & Machine Learning", tech_stack: "", difficulty: "Beginner", description: "" });
            fetchTemplates();
        } catch (err: any) {
            alert(err.message);
        }
    };

    const handleDelete = async (id: number) => {
        if (!confirm("Are you sure? This template will no longer be available to users.")) return;
        try {
            await api.adminDeleteTemplate(id);
            fetchTemplates();
        } catch (err: any) {
            alert(err.message);
        }
    };

    if (loading) return <div className="h-[60vh] flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;

    return (
        <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-black text-foreground">Template Architect</h1>
                    <p className="text-muted-foreground mt-1">Design global blueprints for project generation.</p>
                </div>
                <button 
                    onClick={() => setIsCreating(true)}
                    className="flex items-center gap-2 bg-primary text-primary-foreground px-6 py-3 rounded-2xl font-bold hover:scale-[1.02] active:scale-95 transition-all shadow-lg shadow-primary/25"
                >
                    <Plus className="w-5 h-5" />
                    New Blueprint
                </button>
            </div>

            {isCreating && (
                <div className="bg-card border border-primary/20 rounded-[2.5rem] p-10 shadow-2xl animate-in zoom-in-95 duration-300 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full -mr-32 -mt-32 blur-[100px] group-hover:scale-150 transition-transform duration-1000" />
                    <h2 className="text-2xl font-black mb-8 flex items-center gap-3">
                        <Layout className="w-6 h-6 text-primary" /> Create New Global Template
                    </h2>
                    
                    <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-2 gap-8 relative z-10">
                        <div className="space-y-6">
                            <div className="space-y-2">
                                <label className="text-xs font-black uppercase tracking-widest text-muted-foreground ml-1">Blueprint Name</label>
                                <input 
                                    type="text" required
                                    value={newTemplate.name}
                                    onChange={(e) => setNewTemplate({...newTemplate, name: e.target.value})}
                                    placeholder="e.g. Fullstack E-Commerce Master"
                                    className="w-full p-4 bg-muted/50 border-none rounded-2xl font-bold outline-none focus:ring-2 focus:ring-primary/20 transition-all"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs font-black uppercase tracking-widest text-muted-foreground ml-1">Technical Stack</label>
                                <input 
                                    type="text" required
                                    value={newTemplate.tech_stack}
                                    onChange={(e) => setNewTemplate({...newTemplate, tech_stack: e.target.value})}
                                    placeholder="e.g. Next.js, FastAPI, PostgreSQL"
                                    className="w-full p-4 bg-muted/50 border-none rounded-2xl font-bold outline-none focus:ring-2 focus:ring-primary/20 transition-all"
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-xs font-black uppercase tracking-widest text-muted-foreground ml-1">Domain</label>
                                    <select 
                                        value={newTemplate.domain}
                                        onChange={(e) => setNewTemplate({...newTemplate, domain: e.target.value})}
                                        className="w-full p-4 bg-muted/50 border-none rounded-2xl font-bold outline-none"
                                    >
                                        <option>AI & Machine Learning</option>
                                        <option>Web Development</option>
                                        <option>Mobile Apps</option>
                                        <option>Cyber Security</option>
                                        <option>Data Science</option>
                                    </select>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-xs font-black uppercase tracking-widest text-muted-foreground ml-1">Difficulty</label>
                                    <select 
                                        value={newTemplate.difficulty}
                                        onChange={(e) => setNewTemplate({...newTemplate, difficulty: e.target.value})}
                                        className="w-full p-4 bg-muted/50 border-none rounded-2xl font-bold outline-none"
                                    >
                                        <option>Beginner</option>
                                        <option>Intermediate</option>
                                        <option>Advanced</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-6">
                            <div className="space-y-2 h-full flex flex-col">
                                <label className="text-xs font-black uppercase tracking-widest text-muted-foreground ml-1">Architectural Brief (Description)</label>
                                <textarea 
                                    required
                                    value={newTemplate.description}
                                    onChange={(e) => setNewTemplate({...newTemplate, description: e.target.value})}
                                    className="w-full flex-grow p-4 bg-muted/50 border-none rounded-2xl font-bold outline-none focus:ring-2 focus:ring-primary/20 transition-all resize-none min-h-[150px]"
                                    placeholder="Briefly describe the project scope and core requirements..."
                                />
                            </div>
                            <div className="flex gap-4">
                                <button 
                                    type="button" 
                                    onClick={() => setIsCreating(false)}
                                    className="flex-1 p-4 rounded-2xl bg-muted/50 font-bold hover:bg-muted transition-all"
                                >
                                    Cancel
                                </button>
                                <button 
                                    type="submit" 
                                    className="flex-1 p-4 rounded-2xl bg-primary text-primary-foreground font-black shadow-lg shadow-primary/25 hover:scale-[1.02] active:scale-[0.98] transition-all"
                                >
                                    Deploy Template
                                </button>
                            </div>
                        </div>
                    </form>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {templates.map((t) => (
                    <div key={t.id} className="bg-card border border-border/50 rounded-[2.5rem] p-8 shadow-sm hover:shadow-xl hover:shadow-primary/5 transition-all group relative overflow-hidden">
                        <div className="flex justify-between items-start mb-6">
                            <div className="p-4 rounded-2xl bg-primary/10 text-primary">
                                <Layout className="w-6 h-6" />
                            </div>
                            <button 
                                onClick={() => handleDelete(t.id)}
                                className="p-2.5 rounded-xl border border-border/80 text-muted-foreground hover:bg-destructive hover:text-white hover:border-transparent transition-all"
                            >
                                <Trash2 className="w-4 h-4" />
                            </button>
                        </div>
                        
                        <div className="space-y-4">
                            <div>
                                <h3 className="text-xl font-black text-foreground line-clamp-1">{t.name}</h3>
                                <p className="text-xs font-bold text-primary mt-1 uppercase tracking-wider">{t.domain}</p>
                            </div>
                            
                            <p className="text-sm text-muted-foreground font-medium line-clamp-3 leading-relaxed">
                                {t.description}
                            </p>

                            <div className="flex flex-wrap gap-2 pt-2">
                                <span className={cn(
                                    "px-3 py-1 text-[10px] font-black uppercase tracking-widest rounded-full border",
                                    t.difficulty === 'Beginner' ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' :
                                    t.difficulty === 'Intermediate' ? 'bg-blue-500/10 text-blue-500 border-blue-500/20' :
                                    'bg-destructive/10 text-destructive border-destructive/20'
                                )}>
                                    {t.difficulty}
                                </span>
                                <span className="px-3 py-1 bg-muted/50 text-muted-foreground border border-border/50 text-[10px] font-black uppercase tracking-widest rounded-full">
                                    {t.tech_stack}
                                </span>
                            </div>
                        </div>

                        <div className="mt-8 pt-6 border-t border-border/40 flex items-center justify-between text-[10px] text-muted-foreground font-bold uppercase tracking-widest">
                            <div className="flex items-center gap-1.5 line-clamp-1 overflow-hidden max-w-[150px]">
                                <Tag className="w-3 h-3 " />
                                <span>Default Blueprint</span>
                            </div>
                            <div className="flex items-center gap-1.5 whitespace-nowrap">
                                <Calendar className="w-3 h-3" />
                                {new Date(t.created_at).toLocaleDateString()}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
