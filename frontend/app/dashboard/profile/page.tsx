"use client";

import { useAuth } from "@/components/AuthProvider";
import { Button } from "@/components/ui/button";
import { Camera, Mail, Shield, Zap, CreditCard, ChevronRight, User as UserIcon, Calendar, Activity, X } from "lucide-react";
import Image from "next/image";
import { useState, useEffect } from "react";
import { api } from "@/services/api";

export default function ProfilePage() {
    const { user } = useAuth(); // Assuming login logic is just restoring context if needed, but we'll use API.
    const [stats, setStats] = useState<any>(null);
    
    // Modals
    const [editNameOpen, setEditNameOpen] = useState(false);
    const [nameInput, setNameInput] = useState(user?.name || "");
    const [passwordOpen, setPasswordOpen] = useState(false);
    const [currentPassword, setCurrentPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [msg, setMsg] = useState("");

    useEffect(() => {
        api.getUserStats().then(setStats).catch(console.error);
        if (user) setNameInput(user.name || "");
    }, [user]);

    const handleUpdateName = async () => {
        try {
            await api.updateProfile(nameInput);
            setMsg("Name updated! Refresh to see changes globally.");
            setTimeout(() => { setEditNameOpen(false); setMsg(""); }, 2000);
        } catch(e: any) {
            setMsg(e.message);
        }
    }

    const handleUpdatePassword = async () => {
        try {
            await api.updatePassword(currentPassword, newPassword);
            setMsg("Password successfully updated.");
            setCurrentPassword(""); setNewPassword("");
            setTimeout(() => { setPasswordOpen(false); setMsg(""); }, 2000);
        } catch(e: any) {
            setMsg(e.message);
        }
    }

    if (!user) return null;

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-700">
            <h1 className="text-3xl font-bold tracking-tight">Account & Security</h1>

            {/* Profile Header */}
            <div className="flex flex-col md:flex-row items-center gap-8 p-8 rounded-3xl bg-card border border-border/50 shadow-sm relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-[100px]" />
                <div className="relative z-10 w-28 h-28 rounded-full bg-gradient-to-br from-primary/20 to-accent/20 border-2 border-primary/20 flex items-center justify-center text-4xl shadow-inner">
                    <span className="font-black text-primary">
                        {user?.name ? user.name.charAt(0).toUpperCase() : user?.email?.charAt(0).toUpperCase()}
                    </span>
                    <button className="absolute bottom-0 right-0 p-2 rounded-full bg-primary text-primary-foreground shadow-lg hover:scale-110 transition-transform hidden">
                        <Camera className="w-4 h-4" />
                    </button>
                </div>
                <div className="space-y-2 text-center md:text-left relative z-10">
                    <h2 className="text-3xl font-black">{user?.name || "No Name Set"}</h2>
                    <p className="text-muted-foreground font-medium flex items-center justify-center md:justify-start gap-2">
                        <Mail className="w-4 h-4" /> {user?.email}
                    </p>
                    <div className="flex flex-wrap items-center justify-center md:justify-start gap-2 text-xs font-black uppercase tracking-widest mt-4 pt-2">
                        <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 shadow-sm">
                            {user?.plan || "Free"} Tier
                        </span>
                        {user?.email === "niyant214@gmail.com" && (
                            <span className="px-3 py-1 rounded-full bg-blue-500/10 text-blue-500 border border-blue-500/20 shadow-sm">
                                Administrator
                            </span>
                        )}
                    </div>
                </div>
                
                <div className="md:ml-auto grid grid-cols-2 gap-4 relative z-10">
                   <div className="p-4 bg-muted/30 rounded-2xl border border-border/40 text-center space-y-1">
                       <p className="text-2xl font-black text-foreground">{stats?.projects_generated || 0}</p>
                       <p className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider">Projects</p>
                   </div>
                   <div className="p-4 bg-muted/30 rounded-2xl border border-border/40 text-center space-y-1">
                       <p className="text-2xl font-black text-foreground">{stats?.reports_created || 0}</p>
                       <p className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider">Reports</p>
                   </div>
                </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
                {/* Personal Information */}
                <div className="space-y-4">
                    <h3 className="text-sm font-black text-muted-foreground uppercase tracking-widest">Personal Configuration</h3>
                    <div className="bg-card border border-border/50 rounded-3xl overflow-hidden shadow-sm">
                        <div onClick={() => setEditNameOpen(true)} className="p-5 flex items-center justify-between hover:bg-muted/30 transition-colors cursor-pointer border-b border-border/50">
                            <div className="flex items-center gap-4">
                                <div className="p-2.5 rounded-xl bg-primary/10 text-primary">
                                    <UserIcon className="w-5 h-5" />
                                </div>
                                <div>
                                    <p className="font-bold text-sm">Display Name</p>
                                    <p className="text-xs text-muted-foreground">{user?.name || "Not set"}</p>
                                </div>
                            </div>
                            <Button variant="ghost" size="sm" className="font-bold text-xs uppercase tracking-wider text-primary">Edit</Button>
                        </div>
                        <div className="p-5 flex items-center gap-4">
                            <div className="p-2.5 rounded-xl bg-muted text-muted-foreground">
                                <Calendar className="w-5 h-5" />
                            </div>
                            <div>
                                <p className="font-bold text-sm">Account Created</p>
                                <p className="text-xs text-muted-foreground">{new Date(user?.created_at).toLocaleDateString()}</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Security */}
                <div className="space-y-4">
                    <h3 className="text-sm font-black text-muted-foreground uppercase tracking-widest">Security Subsystem</h3>
                    <div className="bg-card border border-border/50 rounded-3xl overflow-hidden shadow-sm">
                        <div onClick={() => setPasswordOpen(true)} className="p-5 flex items-center justify-between hover:bg-muted/30 transition-colors cursor-pointer group">
                            <div className="flex items-center gap-4">
                                <div className="p-2.5 rounded-xl bg-orange-500/10 text-orange-500">
                                    <Shield className="w-5 h-5" />
                                </div>
                                <div>
                                    <p className="font-bold text-sm">Access Credentials</p>
                                    <p className="text-xs text-muted-foreground group-hover:text-foreground transition-colors">Change your password</p>
                                </div>
                            </div>
                            <ChevronRight className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
                        </div>
                    </div>
                </div>
            </div>

            {/* Modals */}
            {editNameOpen && (
                <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-card border border-border/50 rounded-[2rem] p-8 max-w-sm w-full space-y-6 shadow-2xl relative">
                        <button onClick={() => setEditNameOpen(false)} className="absolute top-6 right-6 text-muted-foreground hover:text-foreground"><X className="w-5 h-5"/></button>
                        <div>
                            <h3 className="text-xl font-black">Edit Display Name</h3>
                            <p className="text-sm text-muted-foreground mt-1">This name appears on the dashboard and generated assets.</p>
                        </div>
                        <div className="space-y-4">
                            <input 
                                value={nameInput} 
                                onChange={e=>setNameInput(e.target.value)}
                                className="w-full bg-muted/50 border border-border/50 rounded-xl px-4 py-3 text-sm font-medium focus:outline-none focus:border-primary transition-colors"
                                placeholder="E.g. Alex Node"
                            />
                            {msg && <p className="text-xs font-bold text-primary">{msg}</p>}
                            <Button onClick={handleUpdateName} className="w-full rounded-xl font-bold py-6">Save Changes</Button>
                        </div>
                    </div>
                </div>
            )}

            {passwordOpen && (
                <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-card border border-border/50 rounded-[2rem] p-8 max-w-sm w-full space-y-6 shadow-2xl relative">
                        <button onClick={() => setPasswordOpen(false)} className="absolute top-6 right-6 text-muted-foreground hover:text-foreground"><X className="w-5 h-5"/></button>
                        <div>
                            <h3 className="text-xl font-black">Security Update</h3>
                            <p className="text-sm text-muted-foreground mt-1">Change your account access password securely.</p>
                        </div>
                        <div className="space-y-4">
                            <input 
                                type="password"
                                value={currentPassword} 
                                onChange={e=>setCurrentPassword(e.target.value)}
                                className="w-full bg-muted/50 border border-border/50 rounded-xl px-4 py-3 text-sm font-medium focus:outline-none focus:border-primary transition-colors"
                                placeholder="Current Password"
                            />
                            <input 
                                type="password"
                                value={newPassword} 
                                onChange={e=>setNewPassword(e.target.value)}
                                className="w-full bg-muted/50 border border-border/50 rounded-xl px-4 py-3 text-sm font-medium focus:outline-none focus:border-primary transition-colors"
                                placeholder="New Secure Password"
                            />
                            {msg && <p className="text-xs font-bold text-primary">{msg}</p>}
                            <Button onClick={handleUpdatePassword} className="w-full rounded-xl font-bold py-6 bg-orange-500 hover:bg-orange-600 text-white shadow-lg shadow-orange-500/20">Update Password</Button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
