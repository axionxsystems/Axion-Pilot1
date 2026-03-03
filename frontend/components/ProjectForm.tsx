"use client";

import { useState } from "react";
import { api, ProjectRequest } from "../services/api";
import { Sparkles, Code2, BookOpen, Layers, Calendar, Rocket, Loader2 } from "lucide-react";

export default function ProjectForm({ onProjectGenerated }: { onProjectGenerated: (data: any) => void }) {
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState<ProjectRequest>({
        api_key: "",
        domain: "Machine Learning",
        topic: "",
        difficulty: "Intermediate",
        tech_stack: "Python, React",
        year: "Final Year",
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
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
        <div className="glass p-8 rounded-3xl shadow-2xl border border-white/10 backdrop-blur-xl relative overflow-hidden group hover:border-white/20 transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />

            <div className="relative z-10">
                <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
                    <span className="p-2 rounded-xl bg-gradient-to-br from-primary to-accent shadow-lg shadow-primary/20">
                        <Rocket className="w-5 h-5 text-white" />
                    </span>
                    <span className="bg-clip-text text-transparent bg-gradient-to-r from-white to-white/70">
                        Generate Project
                    </span>
                </h2>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="space-y-2">
                        <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider ml-1">
                            Groq API Key
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
                                className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all duration-200"
                                placeholder="gsk_... (Optional if set in backend)"
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider ml-1">
                                Domain
                            </label>
                            <div className="relative">
                                <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                                    <Layers className="w-4 h-4" />
                                </div>
                                <select
                                    name="domain"
                                    value={formData.domain}
                                    onChange={handleChange}
                                    className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 appearance-none cursor-pointer hover:bg-white/10 transition-colors"
                                >
                                    {["Machine Learning", "Web Development", "Data Science", "IoT", "Blockchain"].map((d) => (
                                        <option key={d} value={d} className="bg-slate-900">{d}</option>
                                    ))}
                                </select>
                            </div>
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider ml-1">
                                Difficulty
                            </label>
                            <div className="relative">
                                <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                                    <BookOpen className="w-4 h-4" />
                                </div>
                                <select
                                    name="difficulty"
                                    value={formData.difficulty}
                                    onChange={handleChange}
                                    className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 appearance-none cursor-pointer hover:bg-white/10 transition-colors"
                                >
                                    <option className="bg-slate-900">Beginner</option>
                                    <option className="bg-slate-900">Intermediate</option>
                                    <option className="bg-slate-900">Advanced</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider ml-1">
                            Tech Stack
                        </label>
                        <input
                            type="text"
                            name="tech_stack"
                            value={formData.tech_stack}
                            onChange={handleChange}
                            className="w-full bg-white/5 border border-white/10 rounded-xl py-3 px-4 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all duration-200"
                            placeholder="e.g. Python, React, TensorFlow"
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider ml-1">
                            Specific Topic (Result)
                        </label>
                        <input
                            type="text"
                            name="topic"
                            value={formData.topic}
                            onChange={handleChange}
                            placeholder="e.g. Stock Price Prediction"
                            className="w-full bg-white/5 border border-white/10 rounded-xl py-3 px-4 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all duration-200"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full group relative flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-gradient-to-r from-primary to-accent hover:opacity-90 transition-all duration-300 shadow-lg shadow-primary/25 disabled:opacity-50 disabled:cursor-not-allowed mt-4"
                    >
                        {loading ? (
                            <Loader2 className="w-5 h-5 animate-spin text-white" />
                        ) : (
                            <>
                                <Sparkles className="w-5 h-5 text-white group-hover:scale-110 transition-transform" />
                                <span className="font-semibold text-white">Generate Project</span>
                            </>
                        )}
                    </button>
                </form>
            </div>
        </div>
    );
}
