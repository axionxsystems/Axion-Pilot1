"use client";

import { useState } from "react";
import { useAuth } from "../../../components/AuthProvider";
import { api } from "../../../services/api";
import { 
    User, 
    Key, 
    ShieldCheck, 
    CheckCircle2, 
    Loader2, 
    Mail, 
    Sparkles,
    AlertCircle
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

export default function SettingsPage() {
    const { user } = useAuth();
    const [currentPassword, setCurrentPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

    const handlePasswordUpdate = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setMessage(null);
        try {
            await api.updatePassword(currentPassword, newPassword);
            setMessage({ type: 'success', text: 'Password updated successfully!' });
            setCurrentPassword("");
            setNewPassword("");
        } catch (err: any) {
            setMessage({ type: 'error', text: err.message || "Failed to update password" });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-fade-in-up">
            <div>
                <h1 className="text-3xl font-bold tracking-tight text-foreground">Settings</h1>
                <p className="text-muted-foreground mt-1">Manage your account preferences and security.</p>
            </div>

            <div className="grid gap-8">
                {/* Profile Section */}
                <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-xl">
                            <User className="w-5 h-5 text-primary" />
                            Account Profile
                        </CardTitle>
                        <CardDescription>Your registered account information</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid sm:grid-cols-2 gap-4">
                            <div className="p-4 rounded-xl bg-muted/30 border border-border/50 flex items-center justify-between">
                                <div className="space-y-1">
                                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Email</p>
                                    <p className="text-sm font-medium flex items-center gap-2">
                                        <Mail className="w-4 h-4 text-muted-foreground" />
                                        {user?.email}
                                    </p>
                                </div>
                                <ShieldCheck className="w-5 h-5 text-success" />
                            </div>

                            <div className="p-4 rounded-xl bg-muted/30 border border-border/50 flex items-center justify-between">
                                <div className="space-y-1">
                                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Plan</p>
                                    <p className="text-sm font-medium flex items-center gap-2">
                                        <Sparkles className="w-4 h-4 text-accent" />
                                        <span className="capitalize">{user?.plan || 'Free'}</span>
                                    </p>
                                </div>
                                <div className="px-2 py-0.5 rounded-full bg-primary/10 text-[10px] font-bold text-primary border border-primary/20 uppercase">
                                    Active
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Password Section */}
                <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-xl">
                            <Key className="w-5 h-5 text-accent" />
                            Security
                        </CardTitle>
                        <CardDescription>Update your password to keep your account secure</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {message && (
                            <div className={`mb-6 p-4 rounded-xl text-sm flex items-center gap-3 animate-in fade-in slide-in-from-top-2 ${
                                message.type === 'success'
                                    ? 'bg-success/10 border border-success/20 text-success'
                                    : 'bg-destructive/10 border border-destructive/20 text-destructive'
                            }`}>
                                {message.type === 'success' ? <CheckCircle2 className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
                                {message.text}
                            </div>
                        )}

                        <form onSubmit={handlePasswordUpdate} className="space-y-5 max-w-md">
                            <div className="space-y-2">
                                <label className="text-xs font-bold text-muted-foreground uppercase tracking-tight ml-1">
                                    Current Password
                                </label>
                                <Input
                                    type="password"
                                    value={currentPassword}
                                    onChange={(e) => setCurrentPassword(e.target.value)}
                                    className="bg-background/50 border-border/50 h-11"
                                    placeholder="••••••••"
                                    required
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-xs font-bold text-muted-foreground uppercase tracking-tight ml-1">
                                    New Password
                                </label>
                                <Input
                                    type="password"
                                    value={newPassword}
                                    onChange={(e) => setNewPassword(e.target.value)}
                                    className="bg-background/50 border-border/50 h-11"
                                    placeholder="••••••••"
                                    required
                                />
                            </div>

                            <Button 
                                type="submit" 
                                disabled={loading}
                                className="w-full sm:w-auto px-8"
                            >
                                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                Update Password
                            </Button>
                        </form>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
