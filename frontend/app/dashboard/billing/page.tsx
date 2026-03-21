"use client";

import { useAuth } from "@/components/AuthProvider";
import { useState, useEffect } from "react";
import { api } from "@/services/api";
import { Zap, Crown, Rocket, Check, Sparkles, BarChart3, FileText, MonitorPlay, MessageSquare, Layers } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const plans = [
    {
        id: "free",
        name: "Free",
        price: "₹0",
        period: "forever",
        icon: Zap,
        color: "text-emerald-500",
        bg: "bg-emerald-500/10",
        border: "border-emerald-500/20",
        features: [
            "3 Projects / month",
            "Basic Report Generation",
            "Standard PPT Export",
            "5 Viva Questions / project",
            "Community Support",
        ],
        limits: { projects: 3, reports: 3, presentations: 3, viva: 5 }
    },
    {
        id: "pro",
        name: "Pro",
        price: "₹499",
        period: "/ month",
        icon: Crown,
        color: "text-primary",
        bg: "bg-primary/10",
        border: "border-primary/30",
        popular: true,
        features: [
            "25 Projects / month",
            "Advanced Report with Diagrams",
            "Professional PPT with Animations",
            "Unlimited Viva Questions",
            "Priority AI Processing",
            "Full Project Export (ZIP)",
            "Email Support",
        ],
        limits: { projects: 25, reports: 25, presentations: 25, viva: 999 }
    },
    {
        id: "enterprise",
        name: "Enterprise",
        price: "₹1,999",
        period: "/ month",
        icon: Rocket,
        color: "text-accent",
        bg: "bg-accent/10",
        border: "border-accent/30",
        features: [
            "Unlimited Projects",
            "White-label Reports",
            "Custom PPT Templates",
            "AI Viva Coach (unlimited)",
            "Dedicated AI Engine",
            "API Access",
            "Priority Support + SLA",
            "Team Collaboration",
        ],
        limits: { projects: 9999, reports: 9999, presentations: 9999, viva: 9999 }
    }
];

export default function BillingPage() {
    const { user } = useAuth();
    const [stats, setStats] = useState<any>(null);
    const currentPlan = plans.find(p => p.id === (user?.plan || "free")) || plans[0];

    useEffect(() => {
        api.getUserStats().then(setStats).catch(console.error);
    }, []);

    const usageItems = [
        { label: "Projects Generated", used: stats?.projects_generated || 0, limit: currentPlan.limits.projects, icon: Layers, color: "bg-blue-500" },
        { label: "Reports Created", used: stats?.reports_created || 0, limit: currentPlan.limits.reports, icon: FileText, color: "bg-purple-500" },
        { label: "Presentations", used: stats?.presentations_created || 0, limit: currentPlan.limits.presentations, icon: MonitorPlay, color: "bg-pink-500" },
        { label: "Viva Questions", used: stats?.viva_questions || 0, limit: currentPlan.limits.viva, icon: MessageSquare, color: "bg-emerald-500" },
    ];

    return (
        <div className="max-w-6xl mx-auto space-y-10 animate-in fade-in duration-700 pb-20">
            <div>
                <h1 className="text-3xl font-black tracking-tight">Billing & Plans</h1>
                <p className="text-muted-foreground mt-2 font-medium">Manage your subscription and monitor usage.</p>
            </div>

            {/* Current Plan Banner */}
            <div className={cn("relative overflow-hidden rounded-3xl border p-8 shadow-sm", currentPlan.border, currentPlan.bg)}>
                <div className="absolute top-0 right-0 w-64 h-64 rounded-full blur-[120px] opacity-30" style={{background: "var(--primary)"}} />
                <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                    <div className="flex items-center gap-5">
                        <div className={cn("p-4 rounded-2xl shadow-inner", currentPlan.bg)}>
                            <currentPlan.icon className={cn("w-8 h-8", currentPlan.color)} />
                        </div>
                        <div>
                            <p className="text-xs font-black uppercase tracking-widest text-muted-foreground">Current Plan</p>
                            <h2 className="text-3xl font-black text-foreground">{currentPlan.name}</h2>
                            <p className="text-sm text-muted-foreground font-medium mt-1">
                                {currentPlan.price}<span className="text-xs">{currentPlan.period}</span>
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <span className="px-4 py-1.5 rounded-full bg-emerald-500/10 text-emerald-500 text-xs font-black uppercase tracking-widest border border-emerald-500/20">Active</span>
                    </div>
                </div>
            </div>

            {/* Usage Stats */}
            <div className="space-y-5">
                <h3 className="text-sm font-black uppercase tracking-widest text-muted-foreground">Usage This Month</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {usageItems.map((item, i) => {
                        const pct = Math.min((item.used / item.limit) * 100, 100);
                        return (
                            <div key={i} className="bg-card border border-border/50 rounded-2xl p-5 shadow-sm space-y-3">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className={cn("p-2 rounded-xl", `${item.color}/10`)}>
                                            <item.icon className={cn("w-4 h-4", item.color.replace("bg-","text-"))} />
                                        </div>
                                        <span className="text-sm font-bold text-foreground">{item.label}</span>
                                    </div>
                                    <span className="text-xs font-black text-muted-foreground">
                                        {item.used} / {item.limit >= 9999 ? "∞" : item.limit}
                                    </span>
                                </div>
                                <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
                                    <div className={cn("h-full rounded-full transition-all duration-1000", item.color)} style={{ width: `${pct}%` }} />
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Plans Grid */}
            <div className="space-y-5">
                <h3 className="text-sm font-black uppercase tracking-widest text-muted-foreground">Available Plans</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {plans.map((plan) => {
                        const isCurrent = plan.id === (user?.plan || "free");
                        return (
                            <div key={plan.id} className={cn(
                                "relative bg-card border rounded-3xl p-8 shadow-sm space-y-6 transition-all hover:shadow-md",
                                plan.popular ? "border-primary/40 ring-1 ring-primary/20" : "border-border/50",
                                isCurrent && "ring-2 ring-primary/30"
                            )}>
                                {plan.popular && (
                                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-primary text-primary-foreground text-[10px] font-black uppercase tracking-widest rounded-full shadow-lg shadow-primary/20">
                                        Most Popular
                                    </div>
                                )}
                                <div className="space-y-3">
                                    <div className={cn("p-3 rounded-2xl w-fit", plan.bg)}>
                                        <plan.icon className={cn("w-6 h-6", plan.color)} />
                                    </div>
                                    <h4 className="text-xl font-black text-foreground">{plan.name}</h4>
                                    <div>
                                        <span className="text-3xl font-black text-foreground">{plan.price}</span>
                                        <span className="text-sm text-muted-foreground font-bold">{plan.period}</span>
                                    </div>
                                </div>
                                <ul className="space-y-3">
                                    {plan.features.map((f, j) => (
                                        <li key={j} className="flex items-start gap-2.5 text-sm text-foreground/80 font-medium">
                                            <Check className={cn("w-4 h-4 mt-0.5 flex-shrink-0", plan.color)} />
                                            {f}
                                        </li>
                                    ))}
                                </ul>
                                <Button
                                    className={cn(
                                        "w-full rounded-xl font-bold py-6",
                                        isCurrent ? "bg-muted text-muted-foreground cursor-default" : plan.popular ? "bg-primary shadow-lg shadow-primary/20" : ""
                                    )}
                                    variant={isCurrent ? "outline" : plan.popular ? "default" : "outline"}
                                    disabled={isCurrent}
                                >
                                    {isCurrent ? "Current Plan" : `Upgrade to ${plan.name}`}
                                </Button>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
