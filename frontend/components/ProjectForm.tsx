"use client";

import { useState, useEffect } from "react";
import { api, ProjectRequest } from "../services/api";
import { Sparkles, Code2, BookOpen, Layers, Rocket, Loader2, AlignLeft, Layout } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const domains = [
    "Machine Learning",
    "Web Development",
    "Data Science",
    "IoT (Internet of Things)",
    "Blockchain",
    "Cybersecurity",
    "Cloud Computing",
    "Artificial Intelligence",
    "App Development (Android/iOS)",
    "Embedded Systems",
    "Big Data Analysis",
    "AR/VR Technology",
    "Game Development",
    "NLP (Natural Language Processing)"
];

const difficulties = ["Beginner", "Intermediate", "Advanced"];

export default function ProjectForm({ onProjectGenerated }: { onProjectGenerated: (data: any) => void }) {
    const [loading, setLoading] = useState(false);
    const [templates, setTemplates] = useState<any[]>([]);
    const [selectedTemplateId, setSelectedTemplateId] = useState<number | null>(null);
    const [formData, setFormData] = useState<ProjectRequest>({
        api_key: "",
        domain: "Machine Learning",
        topic: "",
        description: "",
        difficulty: "Intermediate",
        tech_stack: "",
        year: "Final Year",
    });

    useEffect(() => {
        const fetchTemplates = async () => {
            try {
                const data = await api.getPublicTemplates();
                setTemplates(data || []);
            } catch (err) {
                console.error("Failed to fetch templates", err);
            }
        };
        fetchTemplates();
    }, []);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
        if (selectedTemplateId) setSelectedTemplateId(null);
    };

    const handleSelectTemplate = (t: any) => {
        setFormData({
            ...formData,
            domain: t.domain,
            difficulty: t.difficulty,
            tech_stack: t.tech_stack,
            topic: t.name,
            description: t.description
        });
        setSelectedTemplateId(t.id);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            const data = await api.generateProject(formData);
            onProjectGenerated(data);
        } catch (error) {
            alert("Error: " + error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-8 animate-fade-in-up">
            {/* Template Selection */}
            {templates.length > 0 && (
                <div className="space-y-4">
                    <div className="flex items-center justify-between px-1">
                        <label className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground flex items-center gap-2">
                            <Sparkles className="w-3 h-3 text-primary" />
                            Pick a Blueprint (Quick Start)
                        </label>
                    </div>
                    <div className="flex gap-4 overflow-x-auto pb-4 px-1 scrollbar-hide no-scrollbar">
                        {templates.map((t) => (
                            <button
                                key={t.id}
                                type="button"
                                onClick={() => handleSelectTemplate(t)}
                                className={cn(
                                    "flex-shrink-0 w-64 p-5 rounded-3xl border text-left transition-all duration-300 group relative overflow-hidden",
                                    selectedTemplateId === t.id 
                                        ? "bg-primary text-primary-foreground border-primary shadow-xl shadow-primary/20 -translate-y-1" 
                                        : "bg-card border-border/50 hover:border-primary/50 text-foreground hover:shadow-lg hover:shadow-primary/5 hover:-translate-y-1"
                                )}
                            >
                                <div className={cn(
                                    "p-2.5 w-fit rounded-xl mb-4 transition-colors",
                                    selectedTemplateId === t.id ? "bg-white/20" : "bg-primary/10 text-primary"
                                )}>
                                    <Layout className="w-5 h-5" />
                                </div>
                                <h3 className="font-bold text-sm mb-1 line-clamp-1">{t.name}</h3>
                                <p className={cn(
                                    "text-[10px] font-black uppercase tracking-widest mb-3",
                                    selectedTemplateId === t.id ? "text-white/70" : "text-primary/70"
                                )}>
                                    {t.domain}
                                </p>
                                <div className="flex flex-wrap gap-2">
                                    <span className={cn(
                                        "px-2 py-0.5 rounded-full text-[8px] font-black uppercase tracking-tighter border",
                                        selectedTemplateId === t.id ? "bg-white/10 border-white/20" : "bg-muted border-border/50"
                                    )}>
                                        {t.difficulty}
                                    </span>
                                </div>
                            </button>
                        ))}
                    </div>
                </div>
            )}

            <div className="bg-card border border-border/50 rounded-3xl p-8 shadow-sm">
                <header className="mb-8">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                            <Rocket className="w-5 h-5 text-primary" />
                        </div>
                        <h2 className="text-2xl font-bold tracking-tight text-foreground">
                            {selectedTemplateId ? "Customizing Blueprint" : "Manual Generation"}
                        </h2>
                    </div>
                    <p className="text-muted-foreground text-sm ml-0 md:ml-[52px]">Select your preferences to build an AI project in seconds.</p>
                </header>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Provider & API Key */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="space-y-2 md:col-span-1">
                            <label className="text-xs font-bold text-muted-foreground uppercase tracking-wider ml-1">
                                AI Engine
                            </label>
                            <div className="relative group">
                                <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors">
                                    <Sparkles className="w-4 h-4" />
                                </div>
                                <select
                                    name="ai_provider"
                                    value={formData.ai_provider || "gemini"}
                                    onChange={handleChange}
                                    className="w-full bg-background border border-border/50 rounded-xl py-3 pl-10 pr-10 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 appearance-none cursor-pointer hover:bg-muted/30 transition-colors font-medium"
                                >
                                    <option value="gemini">Standard Engine (Recommended)</option>
                                    <option value="openai">OpenAI (ChatGPT)</option>
                                    <option value="anthropic">Anthropic (Claude)</option>
                                    <option value="xai">xAI (Grok)</option>

                                </select>
                                <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-muted-foreground">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-2 md:col-span-2">
                            <div className="flex justify-between items-center ml-1">
                                <label className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                                    API Key (Optional)
                                </label>
                                <span className="text-[10px] text-primary/60 font-medium">Uses system default if empty</span>
                            </div>
                            <div className="relative group">
                                <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors">
                                    <Code2 className="w-4 h-4" />
                                </div>
                                <input
                                    type="password"
                                    name="auth_key"
                                    autoComplete="off"
                                    value={formData.api_key}
                                    onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                                    className="w-full bg-background border border-border/50 rounded-xl py-3 pl-10 pr-4 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all duration-200 font-mono"
                                    placeholder={`Enter ${formData.ai_provider === 'openai' ? 'sk-...' : formData.ai_provider === 'anthropic' ? 'sk-ant-...' : formData.ai_provider === 'gemini' ? 'AIza...' : 'gsk_...'} key or leave empty`}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Domain & Difficulty */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-muted-foreground uppercase tracking-wider ml-1">
                                Domain
                            </label>
                            <div className="relative group">
                                <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors">
                                    <Layers className="w-4 h-4" />
                                </div>
                                <select
                                    name="domain"
                                    value={formData.domain}
                                    onChange={handleChange}
                                    className="w-full bg-background border border-border/50 rounded-xl py-3 pl-10 pr-10 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 appearance-none cursor-pointer hover:bg-muted/30 transition-colors"
                                >
                                    {domains.map((d) => (
                                        <option key={d} value={d} className="bg-background text-foreground">{d}</option>
                                    ))}
                                </select>
                                <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-muted-foreground">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                                </div>
                            </div>
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-muted-foreground uppercase tracking-wider ml-1">
                                Difficulty
                            </label>
                            <div className="relative group">
                                <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors">
                                    <BookOpen className="w-4 h-4" />
                                </div>
                                <select
                                    name="difficulty"
                                    value={formData.difficulty}
                                    onChange={handleChange}
                                    className="w-full bg-background border border-border/50 rounded-xl py-3 pl-10 pr-10 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 appearance-none cursor-pointer hover:bg-muted/30 transition-colors"
                                >
                                    {difficulties.map((diff) => (
                                        <option key={diff} value={diff} className="bg-background text-foreground">{diff}</option>
                                    ))}
                                </select>
                                <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-muted-foreground">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Tech Stack & Topic */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-muted-foreground uppercase tracking-wider ml-1">
                                Tech Stack
                            </label>
                            <input
                                type="text"
                                name="tech_stack"
                                value={formData.tech_stack}
                                onChange={handleChange}
                                className="w-full bg-background border border-border/50 rounded-xl py-3 px-4 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all duration-200"
                                placeholder="e.g. Next.js, FastAPI"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-muted-foreground uppercase tracking-wider ml-1">
                                Project Topic
                            </label>
                            <input
                                type="text"
                                name="topic"
                                value={formData.topic}
                                onChange={handleChange}
                                placeholder="e.g. Stock Prediction"
                                className="w-full bg-background border border-border/50 rounded-xl py-3 px-4 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all duration-200"
                            />
                        </div>
                    </div>

                    {/* Description */}
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-muted-foreground uppercase tracking-wider ml-1 flex items-center gap-2">
                            <AlignLeft className="w-3.5 h-3.5" />
                            Project Description
                        </label>
                        <textarea
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                            placeholder="Mention specific features or integration requirements..."
                            rows={4}
                            className="w-full bg-background border border-border/50 rounded-xl py-3 px-4 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all duration-200 resize-none leading-relaxed"
                        />
                    </div>

                    <Button 
                        type="submit" 
                        disabled={loading}
                        className="w-full h-12 text-base font-bold shadow-lg shadow-primary/20"
                    >
                        {loading ? (
                            <Loader2 className="w-5 h-5 animate-spin mr-2" />
                        ) : (
                            <Sparkles className="w-5 h-5 mr-2" />
                        )}
                        Generate Project
                    </Button>
                </form>
            </div>
        </div>
    );
}
