"use client";

import { useState } from "react";
import { api, ProjectRequest } from "../services/api";
import { Sparkles, Code2, BookOpen, Layers, Rocket, Loader2, AlignLeft } from "lucide-react";
import { Button } from "@/components/ui/button";

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
    const [formData, setFormData] = useState<ProjectRequest>({
        api_key: "",
        domain: "Machine Learning",
        topic: "",
        description: "",
        difficulty: "Intermediate",
        tech_stack: "",
        year: "Final Year",
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
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
        <div className="bg-card border border-border/50 rounded-3xl p-8 shadow-sm animate-fade-in-up">
            <header className="mb-8">
                <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                        <Rocket className="w-5 h-5 text-primary" />
                    </div>
                    <h2 className="text-2xl font-bold tracking-tight text-foreground">
                        Generate Project
                    </h2>
                </div>
                <p className="text-muted-foreground text-sm ml-[52px]">Select your preferences to build an AI project in seconds.</p>
            </header>

            <form onSubmit={handleSubmit} className="space-y-6">
                {/* API Key */}
                <div className="space-y-2">
                    <label className="text-xs font-bold text-muted-foreground uppercase tracking-wider ml-1">
                        Groq API Key (Optional)
                    </label>
                    <div className="relative group">
                        <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors">
                            <Code2 className="w-4 h-4" />
                        </div>
                        <input
                            type="password"
                            name="api_key"
                            value={formData.api_key}
                            onChange={handleChange}
                            className="w-full bg-background border border-border/50 rounded-xl py-3 pl-10 pr-4 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all duration-200"
                            placeholder="gsk_..."
                        />
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
    );
}
