"use client";

import { useState, useEffect } from "react";
import { api } from "../../../../services/api";
import { 
    AlertCircle, 
    CheckCircle2, 
    Trash2, 
    User, 
    Clock, 
    ShieldAlert, 
    Filter,
    Loader2,
    Eye,
    MessageSquare,
    ShieldCheck,
    ThumbsDown
} from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

export default function ModerationPage() {
    const [projects, setProjects] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [filterStatus, setFilterStatus] = useState("flagged");
    const [updatingId, setUpdatingId] = useState<number | null>(null);

    const fetchFlagged = async () => {
        setLoading(true);
        try {
            const data = await api.getAdminModerationProjects(filterStatus);
            setProjects(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchFlagged();
    }, [filterStatus]);

    const handleStatusUpdate = async (id: number, newStatus: string) => {
        setUpdatingId(id);
        try {
            await api.updateAdminProjectStatus(id, newStatus);
            setProjects(projects.filter(p => p.id !== id));
        } catch (err: any) {
            alert(err.message);
        } finally {
            setUpdatingId(null);
        }
    };

    if (loading && projects.length === 0) return <div className="h-[60vh] flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;

    return (
        <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div>
                    <h1 className="text-3xl font-black text-foreground flex items-center gap-3">
                        Moderation Protocol
                        {projects.length > 0 && filterStatus === "flagged" && (
                            <span className="bg-destructive/10 text-destructive text-[10px] font-black uppercase tracking-widest px-3 py-1 rounded-full border border-destructive/20 animate-pulse">
                                Requires Action
                            </span>
                        )}
                    </h1>
                    <p className="text-muted-foreground mt-1 font-medium">Review and moderate platform content quality.</p>
                </div>

                <div className="flex items-center gap-1.5 p-1 bg-card border border-border/50 rounded-2xl">
                    {[
                        { id: "flagged", label: "Flagged", icon: ShieldAlert, color: "text-destructive" },
                        { id: "active", label: "Active", icon: Clock, color: "text-blue-500" },
                        { id: "low_quality", label: "Low Quality", icon: ThumbsDown, color: "text-amber-500" },
                        { id: "approved", label: "Verified", icon: ShieldCheck, color: "text-emerald-500" }
                    ].map((btn) => (
                        <button 
                            key={btn.id}
                            onClick={() => setFilterStatus(btn.id)}
                            className={cn(
                                "flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-black uppercase tracking-widest transition-all",
                                filterStatus === btn.id ? "bg-muted text-foreground shadow-sm" : "text-muted-foreground hover:bg-muted/30"
                            )}
                        >
                            <btn.icon className={cn("w-3.5 h-3.5", filterStatus === btn.id ? btn.color : "")} />
                            {btn.label}
                        </button>
                    ))}
                </div>
            </div>

            <div className="bg-card border border-border/50 rounded-[2.5rem] shadow-sm overflow-hidden min-h-[400px]">
                {projects.length === 0 ? (
                    <div className="p-24 text-center flex flex-col items-center gap-4">
                        <div className="w-20 h-20 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-500 border border-emerald-500/20">
                            <CheckCircle2 className="w-10 h-10" />
                        </div>
                        <div>
                            <p className="font-black text-xl text-foreground">All Clear</p>
                            <p className="text-muted-foreground font-medium">No projects in the "{filterStatus}" queue.</p>
                        </div>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="border-b border-border/40 bg-muted/30">
                                    <th className="px-6 py-5 text-xs font-black uppercase tracking-widest text-muted-foreground">Original Source</th>
                                    <th className="px-6 py-5 text-xs font-black uppercase tracking-widest text-muted-foreground">Context</th>
                                    <th className="px-6 py-5 text-xs font-black uppercase tracking-widest text-muted-foreground">Timestamp</th>
                                    <th className="px-6 py-5 text-xs font-black uppercase tracking-widest text-muted-foreground text-right">Moderation Decal</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-border/40">
                                {projects.map((p) => (
                                    <tr key={p.id} className="hover:bg-muted/10 transition-colors group">
                                        <td className="px-6 py-5">
                                            <div className="flex flex-col gap-1">
                                                <p className="text-sm font-black text-foreground">{p.title}</p>
                                                <div className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground uppercase tracking-widest">
                                                    <User className="w-3 h-3" />
                                                    {p.user_email}
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="flex items-center gap-3">
                                                <span className="px-3 py-1 bg-muted text-[10px] font-black tracking-widest uppercase rounded-full border border-border/50">{p.domain}</span>
                                                <span className="px-3 py-1 bg-muted text-[10px] font-black tracking-widest uppercase rounded-full border border-border/50">{p.difficulty}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground">
                                                <Clock className="w-3.5 h-3.5" />
                                                {format(new Date(p.created_at), 'MMM dd, HH:mm:ss')}
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="flex items-center justify-end gap-2">
                                                {filterStatus !== 'approved' && (
                                                    <button 
                                                        disabled={updatingId === p.id}
                                                        onClick={() => handleStatusUpdate(p.id, 'approved')}
                                                        className="p-3 bg-emerald-500/10 text-emerald-500 rounded-2xl border border-emerald-500/20 hover:bg-emerald-500 hover:text-white transition-all shadow-sm"
                                                        title="Approve & Verify"
                                                    >
                                                        <ShieldCheck className="w-4 h-4" />
                                                    </button>
                                                )}
                                                {filterStatus !== 'low_quality' && (
                                                    <button 
                                                        disabled={updatingId === p.id}
                                                        onClick={() => handleStatusUpdate(p.id, 'low_quality')}
                                                        className="p-3 bg-amber-500/10 text-amber-500 rounded-2xl border border-amber-500/20 hover:bg-amber-500 hover:text-white transition-all shadow-sm"
                                                        title="Mark as Low Quality"
                                                    >
                                                        <ThumbsDown className="w-4 h-4" />
                                                    </button>
                                                )}
                                                {filterStatus !== 'flagged' && (
                                                    <button 
                                                        disabled={updatingId === p.id}
                                                        onClick={() => handleStatusUpdate(p.id, 'flagged')}
                                                        className="p-3 bg-destructive/10 text-destructive rounded-2xl border border-destructive/20 hover:bg-destructive hover:text-white transition-all shadow-sm"
                                                        title="Flag for Violation"
                                                    >
                                                        <ShieldAlert className="w-4 h-4" />
                                                    </button>
                                                )}
                                                <button 
                                                    disabled={updatingId === p.id}
                                                    onClick={async () => {
                                                        if(confirm("Delete this content permanently?")) {
                                                            await api.adminDeleteProject(p.id);
                                                            setProjects(projects.filter(x => x.id !== p.id));
                                                        }
                                                    }}
                                                    className="p-3 bg-card border border-border text-muted-foreground rounded-2xl hover:bg-destructive hover:text-white hover:border-transparent transition-all shadow-sm"
                                                    title="Permanent Delete"
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
