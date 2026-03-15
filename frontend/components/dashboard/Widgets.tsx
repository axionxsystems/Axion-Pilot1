import { cn } from "@/lib/utils";
import { Sparkles, FileText, Presentation, MessageSquare, Briefcase, Activity, Clock, ChevronRight, Rocket } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

const stats = [
    { label: "Projects Generated", value: "12", icon: Briefcase, color: "text-blue-500", bg: "bg-blue-500/10" },
    { label: "Reports Created", value: "34", icon: FileText, color: "text-purple-500", bg: "bg-purple-500/10" },
    { label: "Presentations", value: "28", icon: Presentation, color: "text-pink-500", bg: "bg-pink-500/10" },
    { label: "Upcoming Viva", value: "3", icon: MessageSquare, color: "text-emerald-500", bg: "bg-emerald-500/10" },
];

const activities = [
    { text: "Generated abstract for Face Recognition", time: "2m ago", icon: FileText, type: "report" },
    { text: "Compiled React codebase", time: "15m ago", icon: Briefcase, type: "code" },
    { text: "Created 12 Viva questions", time: "1h ago", icon: MessageSquare, type: "viva" },
    { text: "Designed PPT for Blockchain system", time: "3h ago", icon: Presentation, type: "presentation" }
];

const suggestions = [
    { title: "AI Resume Analyzer", domain: "Machine Learning", diff: "Intermediate" },
    { title: "Blockchain Voting System", domain: "Blockchain", diff: "Advanced" },
    { title: "IoT Smart Agriculture", domain: "IoT", diff: "Beginner" }
];

const recentProjects = [
    { name: "Face Recognition Attendance", progress: 100, status: "Completed" },
    { name: "Stock Predictor AI", progress: 60, status: "In Progress" },
];

export function StatsSection() {
    return (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 animate-fade-in-up">
            {stats.map((stat, i) => (
                <div key={i} className="bg-card border border-border/50 rounded-2xl p-5 shadow-sm hover:shadow-md transition-shadow group flex items-start justify-between">
                    <div>
                        <p className="text-sm text-muted-foreground font-medium mb-1">{stat.label}</p>
                        <h3 className="text-3xl font-bold text-foreground tracking-tight group-hover:text-primary transition-colors">{stat.value}</h3>
                    </div>
                    <div className={cn("p-2.5 rounded-xl", stat.bg)}>
                        <stat.icon className={cn("w-5 h-5", stat.color)} />
                    </div>
                </div>
            ))}
        </div>
    );
}

export function ActivityFeed() {
    return (
        <div className="bg-card border border-border/50 rounded-3xl p-6 shadow-sm flex flex-col h-full animate-fade-in-up" style={{ animationDelay: '100ms' }}>
            <div className="flex items-center gap-2 mb-6">
                <Activity className="w-5 h-5 text-primary" />
                <h3 className="text-lg font-bold text-foreground tracking-tight">AI Activity Feed</h3>
            </div>
            <div className="space-y-6 flex-1">
                {activities.map((act, i) => (
                    <div key={i} className="flex gap-4 group">
                        <div className="relative">
                            <div className="w-10 h-10 rounded-full bg-muted/50 flex items-center justify-center group-hover:bg-primary/10 transition-colors z-10 relative border border-border/50">
                                <act.icon className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
                            </div>
                            {i !== activities.length - 1 && (
                                <div className="absolute top-10 bottom-[-24px] left-1/2 w-px bg-border/50 -translate-x-1/2" />
                            )}
                        </div>
                        <div className="pt-2">
                            <p className="text-sm font-medium text-foreground">{act.text}</p>
                            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-0.5">
                                <Clock className="w-3 h-3" />
                                {act.time}
                            </p>
                        </div>
                    </div>
                ))}
            </div>
            <Button variant="ghost" className="w-full mt-6 text-primary hover:text-primary/80 hover:bg-primary/5">
                View All Activity
            </Button>
        </div>
    );
}

export function SuggestionPanel() {
    return (
        <div className="bg-card border border-border/50 rounded-3xl p-6 shadow-sm animate-fade-in-up" style={{ animationDelay: '200ms' }}>
            <div className="flex items-center gap-2 mb-6">
                <Sparkles className="w-5 h-5 text-accent" />
                <h3 className="text-lg font-bold text-foreground tracking-tight">AI Suggestions</h3>
            </div>
            <div className="space-y-3">
                {suggestions.map((sug, i) => (
                    <button key={i} className="w-full text-left bg-muted/30 border border-border/50 rounded-2xl p-4 hover:bg-muted/50 hover:border-primary/30 transition-all group flex items-center justify-between">
                        <div>
                            <p className="font-semibold text-foreground text-sm leading-tight group-hover:text-primary transition-colors">{sug.title}</p>
                            <div className="flex items-center gap-2 mt-2">
                                <span className="text-[10px] uppercase font-bold text-muted-foreground bg-muted px-2 py-0.5 rounded-full">{sug.domain}</span>
                                <span className="text-[10px] uppercase font-bold text-muted-foreground bg-muted px-2 py-0.5 rounded-full">{sug.diff}</span>
                            </div>
                        </div>
                        <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-transform group-hover:translate-x-1" />
                    </button>
                ))}
            </div>
        </div>
    );
}

export function RecentProjectsList() {
    return (
        <div className="bg-card border border-border/50 rounded-3xl p-6 shadow-sm animate-fade-in-up" style={{ animationDelay: '150ms' }}>
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                    <Briefcase className="w-5 h-5 text-primary" />
                    <h3 className="text-lg font-bold text-foreground tracking-tight">Recent Projects</h3>
                </div>
                <Link href="/dashboard/projects" className="text-xs font-semibold text-primary hover:underline">
                    View All
                </Link>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {recentProjects.map((proj, i) => (
                    <div key={i} className="bg-background border border-border/50 rounded-2xl p-5 hover:border-primary/30 transition-colors group">
                        <div className="flex justify-between items-start mb-4">
                            <h4 className="font-bold text-foreground">{proj.name}</h4>
                            <span className={cn(
                                "text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full",
                                proj.progress === 100 ? "bg-emerald-500/10 text-emerald-500" : "bg-blue-500/10 text-blue-500"
                            )}>
                                {proj.status}
                            </span>
                        </div>
                        <div className="space-y-1">
                            <div className="flex justify-between text-xs text-muted-foreground font-medium mb-1">
                                <span>Generation Progress</span>
                                <span>{proj.progress}%</span>
                            </div>
                            <div className="w-full bg-muted rounded-full h-1.5 overflow-hidden">
                                <div 
                                    className={cn("h-full rounded-full transition-all duration-1000", proj.progress === 100 ? "bg-emerald-500" : "bg-primary")}
                                    style={{ width: `${proj.progress}%` }}
                                />
                            </div>
                        </div>
                        <Button variant="outline" size="sm" className="w-full mt-5 group-hover:bg-primary group-hover:text-white group-hover:border-primary transition-all">
                            Open Project
                        </Button>
                    </div>
                ))}
            </div>
        </div>
    );
}

export function ProjectProgressTracker() {
    const trackerStages = [
        { name: "Report Generation", progress: 80, color: "bg-blue-500" },
        { name: "Presentation Builder", progress: 60, color: "bg-purple-500" },
        { name: "Code Packaging", progress: 100, color: "bg-emerald-500" },
    ];

    return (
        <div className="bg-card border border-border/50 rounded-3xl p-6 shadow-sm animate-fade-in-up" style={{ animationDelay: '250ms' }}>
            <div className="flex items-center gap-2 mb-6">
                <Rocket className="w-5 h-5 text-primary" />
                <h3 className="text-lg font-bold text-foreground tracking-tight">Generation Progress</h3>
            </div>
            <div className="space-y-6">
                {trackerStages.map((stage, i) => (
                    <div key={i} className="space-y-2">
                        <div className="flex justify-between text-sm font-medium">
                            <span className="text-foreground">{stage.name}</span>
                            <span className="text-muted-foreground">{stage.progress}%</span>
                        </div>
                        <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
                            <div 
                                className={cn("h-full rounded-full transition-all duration-1000 animate-pulse-glow", stage.color)}
                                style={{ width: `${stage.progress}%` }}
                            />
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
