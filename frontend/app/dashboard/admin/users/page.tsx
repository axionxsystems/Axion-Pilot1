"use client";

import { useState, useEffect } from "react";
import { api, User } from "../../../../services/api";
import { 
    Users, 
    Search, 
    MoreVertical, 
    Shield, 
    UserMinus, 
    Ban, 
    CheckCircle2, 
    Clock, 
    Layers,
    Trash2,
    Calendar,
    Loader2,
    AlertCircle
} from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

export default function UserManagementPage() {
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [error, setError] = useState<string | null>(null);

    const fetchUsers = async () => {
        try {
            const data = await api.adminListUsers();
            setUsers(data);
        } catch (err: any) {
            setError(err.message || "Failed to load users");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    const toggleStatus = async (userId: number) => {
        try {
            await api.adminToggleUserStatus(userId);
            fetchUsers(); // Refresh
        } catch (err: any) {
            alert(err.message);
        }
    };

    const deleteUser = async (userId: number) => {
        if (!confirm("Are you sure? This will delete all user data and projects permanently.")) return;
        try {
            await api.adminDeleteUser(userId);
            fetchUsers(); // Refresh
        } catch (err: any) {
            alert(err.message);
        }
    };

    const filteredUsers = users.filter(u => 
        u.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (u.name?.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    if (loading) return <div className="h-[60vh] flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;

    return (
        <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-black text-foreground">User Management</h1>
                    <p className="text-muted-foreground mt-1">Monitor and control platform access.</p>
                </div>
                <div className="relative w-full md:w-96">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <input 
                        type="text"
                        placeholder="Search by email or name..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-11 pr-4 py-3 bg-card border border-border/50 rounded-2xl outline-none focus:ring-2 focus:ring-primary/20 transition-all font-medium"
                    />
                </div>
            </div>

            <div className="bg-card border border-border/50 rounded-[2.5rem] shadow-sm overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="border-b border-border/40 bg-muted/30">
                                <th className="px-6 py-5 text-xs font-black uppercase tracking-widest text-muted-foreground">User Identity</th>
                                <th className="px-6 py-5 text-xs font-black uppercase tracking-widest text-muted-foreground">Status & Role</th>
                                <th className="px-6 py-5 text-xs font-black uppercase tracking-widest text-muted-foreground">Projects</th>
                                <th className="px-6 py-5 text-xs font-black uppercase tracking-widest text-muted-foreground">Joined At</th>
                                <th className="px-6 py-5 text-xs font-black uppercase tracking-widest text-muted-foreground text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border/40">
                            {filteredUsers.map((u) => (
                                <tr key={u.id} className="hover:bg-muted/20 transition-colors group">
                                    <td className="px-6 py-5">
                                        <div className="flex items-center gap-4">
                                            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold">
                                                {u.email[0].toUpperCase()}
                                            </div>
                                            <div>
                                                <p className="text-sm font-bold text-foreground">{u.name || "Anonymous User"}</p>
                                                <p className="text-xs text-muted-foreground">{u.email}</p>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-5">
                                        <div className="flex flex-col gap-1.5">
                                            <div className="flex items-center gap-2">
                                                {u.is_admin ? (
                                                    <span className="px-2 py-0.5 bg-amber-500/10 text-amber-500 text-[10px] font-black uppercase tracking-widest rounded-md border border-amber-500/20 flex items-center gap-1">
                                                        <Shield className="w-3 h-3" /> Admin
                                                    </span>
                                                ) : (
                                                    <span className="px-2 py-0.5 bg-blue-500/10 text-blue-500 text-[10px] font-black uppercase tracking-widest rounded-md border border-blue-500/20">User</span>
                                                )}
                                                {u.is_active ? (
                                                    <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-500 text-[10px] font-black uppercase tracking-widest rounded-md border border-emerald-500/20">Active</span>
                                                ) : (
                                                    <span className="px-2 py-0.5 bg-destructive/10 text-destructive text-[10px] font-black uppercase tracking-widest rounded-md border border-destructive/20">Suspended</span>
                                                )}
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-5">
                                        <div className="flex items-center gap-2 text-sm font-bold text-foreground">
                                            <Layers className="w-4 h-4 text-muted-foreground" />
                                            {(u as any).project_count || 0}
                                        </div>
                                    </td>
                                    <td className="px-6 py-5 text-sm text-muted-foreground">
                                        <div className="flex items-center gap-2">
                                            <Calendar className="w-4 h-4" />
                                            {format(new Date(u.created_at), 'MMM dd, yyyy')}
                                        </div>
                                    </td>
                                    <td className="px-6 py-5">
                                        <div className="flex items-center justify-end gap-2">
                                            <button 
                                                onClick={() => toggleStatus(u.id)}
                                                className={cn(
                                                    "p-2 rounded-xl border transition-all",
                                                    u.is_active 
                                                        ? "border-destructive/20 text-destructive hover:bg-destructive/10" 
                                                        : "border-emerald-500/20 text-emerald-500 hover:bg-emerald-500/10"
                                                )}
                                                title={u.is_active ? "Suspend User" : "Activate User"}
                                            >
                                                {u.is_active ? <Ban className="w-4 h-4" /> : <CheckCircle2 className="w-4 h-4" />}
                                            </button>
                                            <button 
                                                onClick={() => deleteUser(u.id)}
                                                className="p-2 rounded-xl border border-destructive/20 text-destructive hover:bg-destructive hover:text-white transition-all shadow-sm"
                                                title="Delete User"
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
            </div>
        </div>
    );
}
