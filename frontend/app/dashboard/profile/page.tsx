"use client";

import { useAuth } from "@/components/AuthProvider";
import { Button } from "@/components/ui/button";
import { Camera, Mail, Shield, Zap, CreditCard, ChevronRight } from "lucide-react";
import Image from "next/image";

export default function ProfilePage() {
    const { user } = useAuth();

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-700">
            <h1 className="text-3xl font-bold tracking-tight">Settings</h1>

            {/* Profile Header (Apple ID Style) */}
            <div className="flex items-center gap-6 p-6 rounded-2xl bg-card border shadow-sm">
                <div className="relative">
                    <div className="w-24 h-24 rounded-full bg-gradient-to-br from-neutral-200 to-neutral-300 dark:from-neutral-700 dark:to-neutral-800 flex items-center justify-center text-4xl overflow-hidden">
                        {user?.avatar_url ? (
                            <Image src={user.avatar_url} alt="Profile" width={96} height={96} className="object-cover" />
                        ) : (
                            <span className="text-muted-foreground font-medium">
                                {user?.email?.charAt(0).toUpperCase()}
                            </span>
                        )}
                    </div>
                    <button className="absolute bottom-0 right-0 p-1.5 rounded-full bg-primary text-primary-foreground shadow-sm hover:bg-primary/90 transition-colors">
                        <Camera className="w-4 h-4" />
                    </button>
                </div>
                <div className="space-y-1">
                    <h2 className="text-2xl font-semibold">{user?.name || "User"}</h2>
                    <p className="text-muted-foreground">{user?.email}</p>
                    <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground mt-2">
                        <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 border border-emerald-500/20">
                            Remote Plan
                        </span>
                        <span className="px-2 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/20">
                            Member
                        </span>
                    </div>
                </div>
            </div>

            {/* Settings Groups */}
            <div className="grid gap-6">

                {/* Account */}
                <section className="space-y-4">
                    <h3 className="text-sm font-medium text-muted-foreground px-1 uppercase tracking-wider">Account</h3>
                    <div className="rounded-xl border bg-card shadow-sm divide-y divide-border/50 overflow-hidden">
                        <div className="p-4 flex items-center justify-between hover:bg-muted/50 transition-colors cursor-pointer group">
                            <div className="flex items-center gap-4">
                                <div className="p-2 rounded-lg bg-blue-500/10 text-blue-500">
                                    <Mail className="w-5 h-5" />
                                </div>
                                <div>
                                    <p className="font-medium text-sm">Email Address</p>
                                    <p className="text-xs text-muted-foreground">{user?.email}</p>
                                </div>
                            </div>
                            <Button variant="ghost" size="sm">Edit</Button>
                        </div>
                        <div className="p-4 flex items-center justify-between hover:bg-muted/50 transition-colors cursor-pointer group">
                            <div className="flex items-center gap-4">
                                <div className="p-2 rounded-lg bg-purple-500/10 text-purple-500">
                                    <Shield className="w-5 h-5" />
                                </div>
                                <div>
                                    <p className="font-medium text-sm">Password & Security</p>
                                    <p className="text-xs text-muted-foreground">Last changed 3 months ago</p>
                                </div>
                            </div>
                            <ChevronRight className="w-5 h-5 text-muted-foreground/50 group-hover:text-muted-foreground" />
                        </div>
                    </div>
                </section>

                {/* Subscription */}
                <section className="space-y-4">
                    <h3 className="text-sm font-medium text-muted-foreground px-1 uppercase tracking-wider">Billing</h3>
                    <div className="rounded-xl border bg-card shadow-sm divide-y divide-border/50 overflow-hidden">
                        <div className="p-4 flex items-center justify-between hover:bg-muted/50 transition-colors cursor-pointer group">
                            <div className="flex items-center gap-4">
                                <div className="p-2 rounded-lg bg-green-500/10 text-green-500">
                                    <Zap className="w-5 h-5" />
                                </div>
                                <div>
                                    <p className="font-medium text-sm">Current Plan</p>
                                    <p className="text-xs text-muted-foreground">Pro Semester Pack</p>
                                </div>
                            </div>
                            <Button variant="outline" size="sm">Upgrade</Button>
                        </div>
                        <div className="p-4 flex items-center justify-between hover:bg-muted/50 transition-colors cursor-pointer group">
                            <div className="flex items-center gap-4">
                                <div className="p-2 rounded-lg bg-orange-500/10 text-orange-500">
                                    <CreditCard className="w-5 h-5" />
                                </div>
                                <div>
                                    <p className="font-medium text-sm">Payment Methods</p>
                                    <p className="text-xs text-muted-foreground">Visa ending in 4242</p>
                                </div>
                            </div>
                            <ChevronRight className="w-5 h-5 text-muted-foreground/50 group-hover:text-muted-foreground" />
                        </div>
                    </div>
                </section>

            </div>
        </div>
    );
}
