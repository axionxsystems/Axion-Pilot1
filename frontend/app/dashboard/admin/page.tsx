"use client";

import { useState, useEffect } from "react";
import { api } from "../../../services/api";
import { useAuth } from "../../../components/AuthProvider";
import { 
    Users, 
    Layers, 
    FileText, 
    Presentation, 
    Activity as ActivityIcon,
    TrendingUp,
    PieChart as PieIcon,
    AlertCircle,
    Loader2,
    CheckCircle2,
    ChevronRight,
    Search
} from "lucide-react";
import { 
    BarChart, 
    Bar, 
    XAxis, 
    YAxis, 
    CartesianGrid, 
    Tooltip, 
    ResponsiveContainer, 
    LineChart, 
    Line,
    PieChart,
    Pie,
    Cell,
    AreaChart,
    Area
} from "recharts";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

export default function AdminDashboardPage() {
    const { user } = useAuth();
    const [stats, setStats] = useState<any>(null);
    const [activity, setActivity] = useState<any[]>([]);
    const [historyData, setHistoryData] = useState<any[]>([]);
    const [domainData, setDomainData] = useState<any[]>([]);
    const [difficultyData, setDifficultyData] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (user && !user.is_admin) {
            setError("Unauthorized access. Admin only.");
            setLoading(false);
            return;
        }

        const fetchAllData = async () => {
            try {
                const [statsRes, activityRes, historyRes, domainRes, difficultyRes] = await Promise.all([
                    api.getAdminStats(),
                    api.getAdminActivity(),
                    api.getAdminChartProjectsPerDay(),
                    api.getAdminChartProjectsPerDomain(),
                    api.getAdminChartProjectsPerDifficulty()
                ]);

                setStats(statsRes);
                setActivity(activityRes.items || activityRes || []);
                setHistoryData(historyRes);
                setDomainData(domainRes);
                setDifficultyData(difficultyRes);
            } catch (err: any) {
                console.error("Admin data fetch failed", err);
                setError(err.message || "Failed to load dashboard data");
            } finally {
                setLoading(false);
            }
        };

        if (user) {
            fetchAllData();
        }
    }, [user]);

    if (loading) {
        return (
            <div className="h-[80vh] flex flex-col items-center justify-center space-y-4">
                <Loader2 className="w-12 h-12 text-primary animate-spin" />
                <p className="text-muted-foreground font-medium animate-pulse">Initializing Terminal...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="h-[80vh] flex flex-col items-center justify-center p-8 text-center max-w-md mx-auto space-y-6">
                <div className="w-20 h-20 rounded-full bg-destructive/10 flex items-center justify-center text-destructive">
                    <AlertCircle className="w-10 h-10" />
                </div>
                <div>
                    <h2 className="text-2xl font-black text-foreground mb-2">Access Denied</h2>
                    <p className="text-muted-foreground">{error}</p>
                </div>
                <button 
                    onClick={() => window.location.href = "/dashboard"}
                    className="bg-foreground text-background px-6 py-3 rounded-2xl font-bold hover:bg-primary hover:text-white transition-all w-full"
                >
                    Back to Dashboard
                </button>
            </div>
        );
    }

    const COLORS = ['#2563EB', '#7C3AED', '#22C55E', '#F59E0B', '#EF4444', '#06B6D4'];

    return (
        <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">

            {/* ── Command Center Header ─────────────────────────────────────── */}
            <div className="relative rounded-[2rem] overflow-hidden border border-red-500/20 bg-gradient-to-br from-zinc-900/80 via-background to-red-950/20 p-8 md:p-10">
                {/* Grid pattern overlay */}
                <div className="absolute inset-0 opacity-5 pointer-events-none"
                    style={{ backgroundImage: "linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)", backgroundSize: "40px 40px" }} />
                {/* Red glow */}
                <div className="absolute -top-10 -right-10 w-64 h-64 bg-red-500/10 rounded-full blur-3xl pointer-events-none" />
                <div className="absolute -bottom-10 -left-10 w-48 h-48 bg-orange-500/5 rounded-full blur-3xl pointer-events-none" />

                <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                    <div>
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md bg-red-500/10 border border-red-500/30 text-red-400 text-[10px] font-black uppercase tracking-[0.2em] mb-3 font-mono">
                            <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse" />
                            SUDO ACCESS — RESTRICTED
                        </div>
                        <h1 className="text-4xl md:text-5xl font-black tracking-tight text-foreground font-mono">
                            Platform Control<br />
                            <span className="text-red-400">Center</span>
                        </h1>
                        <p className="text-muted-foreground mt-2 text-sm font-medium font-mono">
                            Logged in as <span className="text-red-400 font-bold">{user?.email}</span> · All actions are logged.
                        </p>
                    </div>

                    {/* Status + Date */}
                    <div className="flex flex-col items-end gap-3">
                        <div className="flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 rounded-xl px-4 py-2">
                            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_6px_#4ade80]" />
                            <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest font-mono">SYSTEM LIVE</span>
                        </div>
                        <div className="text-xs text-muted-foreground font-mono text-right">
                            <div className="font-bold text-foreground">{new Date().toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long" })}</div>
                            <div>{new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} IST</div>
                        </div>
                    </div>
                </div>

                {/* KPI strip */}
                <div className="relative z-10 grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6">
                    {[
                        { label: "Total Users", value: stats?.total_users ?? "—", suffix: "accounts", color: "text-blue-400", border: "border-blue-500/20 bg-blue-500/5" },
                        { label: "Projects", value: stats?.total_projects ?? "—", suffix: "generated", color: "text-violet-400", border: "border-violet-500/20 bg-violet-500/5" },
                        { label: "Reports", value: stats?.total_reports ?? "—", suffix: "produced", color: "text-emerald-400", border: "border-emerald-500/20 bg-emerald-500/5" },
                        { label: "PPTs", value: stats?.total_presentations ?? "—", suffix: "created", color: "text-amber-400", border: "border-amber-500/20 bg-amber-500/5" },
                    ].map(k => (
                        <div key={k.label} className={`rounded-2xl border ${k.border} px-4 py-3`}>
                            <div className={`text-2xl font-black font-mono ${k.color}`}>{k.value}</div>
                            <div className="text-[10px] text-muted-foreground uppercase tracking-widest font-bold mt-0.5">{k.label}</div>
                            <div className="text-[10px] text-muted-foreground/50">{k.suffix}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Admin Navigation Hub */}
            <div className="flex flex-wrap items-center gap-1.5 p-1 bg-muted/40 border border-border/40 rounded-[1.25rem] w-fit">
                {[
                    { label: "Overview", href: "/dashboard/admin" },
                    { label: "Accounts", href: "/dashboard/admin/users" },
                    { label: "Projects", href: "/dashboard/admin/projects" },
                    { label: "Moderation", href: "/dashboard/admin/moderation" },
                    { label: "Templates", href: "/dashboard/admin/templates" },
                    { label: "AI Config", href: "/dashboard/admin/settings" },
                ].map((link) => (
                    <button
                        key={link.href}
                        onClick={() => window.location.href = link.href}
                        className={cn(
                            "px-5 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all",
                            window.location.pathname === link.href ? "bg-card text-red-400 shadow-sm ring-1 ring-red-500/20" : "text-muted-foreground hover:text-foreground"
                        )}
                    >
                        {link.label}
                    </button>
                ))}
            </div>


            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Difficulty Distribution Chart */}
                <div className="lg:col-span-12 bg-card border border-border/50 rounded-[2.5rem] p-8 shadow-sm">
                    <div className="flex items-center justify-between mb-8">
                        <div>
                            <h3 className="text-xl font-bold text-foreground">Difficulty Distribution</h3>
                            <p className="text-sm text-muted-foreground">Projects by complexity level</p>
                        </div>
                    </div>
                    <div className="h-[250px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={difficultyData}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                                <XAxis 
                                    dataKey="difficulty" 
                                    axisLine={false} 
                                    tickLine={false} 
                                    tick={{fontSize: 12, fill: '#94a3b8'}}
                                />
                                <YAxis axisLine={false} tickLine={false} tick={{fontSize: 12, fill: '#94a3b8'}} />
                                <Tooltip 
                                    cursor={{fill: 'transparent'}}
                                    contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 30px -10px rgba(0,0,0,0.1)' }}
                                />
                                <Bar 
                                    dataKey="count" 
                                    radius={[8, 8, 0, 0]}
                                >
                                    {difficultyData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={index === 0 ? '#10B981' : index === 1 ? '#3B82F6' : '#EF4444'} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Growth Chart */}
                <div className="lg:col-span-8 bg-card border border-border/50 rounded-[2.5rem] p-8 shadow-sm">
                    <div className="flex items-center justify-between mb-8">
                        <div>
                            <h3 className="text-xl font-bold text-foreground">Generation Growth</h3>
                            <p className="text-sm text-muted-foreground">Projects created over time</p>
                        </div>
                        <select className="bg-muted/50 border-none text-xs font-bold rounded-xl px-4 py-2 outline-none">
                            <option>Last 14 Days</option>
                            <option>Last 30 Days</option>
                        </select>
                    </div>
                    <div className="h-[350px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={historyData}>
                                <defs>
                                    <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#2563EB" stopOpacity={0.1}/>
                                        <stop offset="95%" stopColor="#2563EB" stopOpacity={0}/>
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                                <XAxis 
                                    dataKey="date" 
                                    axisLine={false} 
                                    tickLine={false} 
                                    tick={{fontSize: 12, fill: '#94a3b8'}}
                                    tickFormatter={(str) => {
                                        try {
                                            return str ? format(new Date(str), 'MMM d') : '';
                                        } catch(e) {
                                            return '';
                                        }
                                    }}
                                />
                                <YAxis axisLine={false} tickLine={false} tick={{fontSize: 12, fill: '#94a3b8'}} />
                                <Tooltip 
                                    contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 30px -10px rgba(0,0,0,0.1)' }}
                                />
                                <Area 
                                    type="monotone" 
                                    dataKey="count" 
                                    stroke="#2563EB" 
                                    strokeWidth={3} 
                                    fillOpacity={1} 
                                    fill="url(#colorCount)" 
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Domain Distribution */}
                <div className="lg:col-span-4 bg-card border border-border/50 rounded-[2.5rem] p-8 shadow-sm">
                    <h3 className="text-xl font-bold text-foreground mb-1">Domain Share</h3>
                    <p className="text-sm text-muted-foreground mb-8">Popular technical niches</p>
                    <div className="h-[250px] w-full mb-8">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={domainData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
                                    paddingAngle={5}
                                    dataKey="count"
                                    nameKey="domain"
                                >
                                    {domainData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="space-y-4">
                        {domainData.slice(0, 4).map((d, i) => (
                            <div key={i} className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                                    <span className="text-sm font-medium text-muted-foreground">{d.domain}</span>
                                </div>
                                <span className="text-sm font-bold text-foreground">{d.count}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Bottom Section: Activity and Recent */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Recent Activity Feed */}
                <div className="lg:col-span-12 bg-card border border-border/50 rounded-[2.5rem] shadow-sm overflow-hidden">
                    <div className="p-8 border-b border-border/40 flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <div className="p-3 bg-primary/10 rounded-2xl">
                                <ActivityIcon className="w-6 h-6 text-primary" />
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-foreground">Platform Activity Feed</h3>
                                <p className="text-sm text-muted-foreground">Streaming live platform operations</p>
                            </div>
                        </div>
                        <button className="text-xs font-black text-primary hover:underline tracking-widest uppercase">Export Logs</button>
                    </div>
                    <div className="divide-y divide-border/40 max-h-[500px] overflow-y-auto scrollbar-hide">
                        {activity.length === 0 ? (
                            <div className="p-12 text-center text-muted-foreground">No recent activity found.</div>
                        ) : (
                            activity.map((log, i) => (
                                <div key={log.id || i} className="p-6 flex items-center justify-between hover:bg-muted/30 transition-colors group">
                                    <div className="flex items-center gap-5">
                                        <div className={cn(
                                            "w-12 h-12 rounded-2xl flex items-center justify-center text-lg shadow-sm border border-white/10",
                                            log.action_type === "USER_REG" ? "bg-blue-500/10 text-blue-500" :
                                            log.action_type === "PROJECT_GEN" ? "bg-purple-500/10 text-purple-500" :
                                            log.action_type === "REPORT_GEN" ? "bg-emerald-500/10 text-emerald-500" :
                                            "bg-amber-500/10 text-amber-500"
                                        )}>
                                            {log.action_type === "USER_REG" ? <Users className="w-5 h-5" /> :
                                             log.action_type === "PROJECT_GEN" ? <Layers className="w-5 h-5" /> :
                                             log.action_type === "REPORT_GEN" ? <FileText className="w-5 h-5" /> :
                                             <Sparkles className="w-5 h-5" />}
                                        </div>
                                        <div>
                                            <p className="text-sm font-bold text-foreground group-hover:text-primary transition-colors">{log.description}</p>
                                            <div className="flex items-center gap-3 mt-1">
                                                <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/60">{log.action_type}</span>
                                                <div className="w-1 h-1 rounded-full bg-border" />
                                                <span className="text-[10px] font-bold text-primary truncate max-w-[120px]">{log.user_email || 'System'}</span>
                                                <div className="w-1 h-1 rounded-full bg-border" />
                                                <span className="text-[10px] font-bold text-muted-foreground">{log.created_at ? format(new Date(log.created_at), 'HH:mm:ss, MMM dd') : 'Recent'}</span>
                                            </div>
                                        </div>
                                    </div>
                                    <button className="p-2 rounded-xl border border-transparent hover:border-border hover:bg-card text-muted-foreground opacity-0 group-hover:opacity-100 transition-all">
                                        <ChevronRight className="w-5 h-5" />
                                    </button>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

function Sparkles(props: any) {
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
            <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
            <path d="M5 3v4" />
            <path d="M19 17v4" />
            <path d="M3 5h4" />
            <path d="M17 19h4" />
        </svg>
    )
}
