"use client";

import { useState, useEffect } from "react";
import { api } from "../../../../services/api";
import { 
    Cpu, 
    Settings, 
    Zap, 
    Code, 
    FileText, 
    Layers, 
    Save, 
    RefreshCw,
    Loader2
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function AISettingsPage() {
    const [config, setConfig] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState("");

    useEffect(() => {
        const fetchSettings = async () => {
            try {
                const data = await api.getAdminAISettings();
                setConfig(data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchSettings();
    }, []);

    const handleSave = async () => {
        setSaving(true);
        try {
            await api.updateAdminAISettings(config);
            setMessage("Settings saved successfully!");
            setTimeout(() => setMessage(""), 3000);
        } catch (err: any) {
            alert(err.message);
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <div className="h-[60vh] flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-black text-foreground">AI Intelligence Control</h1>
                    <p className="text-muted-foreground mt-1">Configure global AI models and generation parameters.</p>
                </div>
                <button 
                    onClick={handleSave}
                    disabled={saving}
                    className="flex items-center gap-2 bg-primary text-primary-foreground px-6 py-3 rounded-2xl font-bold hover:scale-[1.02] active:scale-95 transition-all shadow-lg shadow-primary/25 disabled:opacity-50"
                >
                    {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                    Save Changes
                </button>
            </div>

            {message && (
                <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 p-4 rounded-xl text-sm font-bold animate-in zoom-in-95">
                    {message}
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Global AI Config */}
                <div className="bg-card border border-border/50 rounded-[2.5rem] p-8 shadow-sm space-y-6">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2.5 bg-blue-500/10 rounded-xl">
                            <Cpu className="w-5 h-5 text-blue-500" />
                        </div>
                        <h2 className="text-xl font-bold">Model Parameters</h2>
                    </div>

                    <div className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-xs font-black uppercase tracking-widest text-muted-foreground">Active LLM Model</label>
                            <select 
                                value={config.model}
                                onChange={(e) => setConfig({...config, model: e.target.value})}
                                className="w-full p-3 bg-muted/50 border-none rounded-xl font-bold outline-none"
                            >
                                <option value="gemini-1.5-flash">Gemini 1.5 Flash (Recommended)</option>
                                <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                                <option value="gpt-4o">GPT-4o</option>
                            </select>
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs font-black uppercase tracking-widest text-muted-foreground flex justify-between">
                                Temperature
                                <span className="text-primary">{config.temperature}</span>
                            </label>
                            <input 
                                type="range" min="0" max="1" step="0.1"
                                value={config.temperature}
                                onChange={(e) => setConfig({...config, temperature: parseFloat(e.target.value)})}
                                className="w-full accent-primary"
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs font-black uppercase tracking-widest text-muted-foreground">Max Generation Tokens</label>
                            <input 
                                type="number"
                                value={config.max_tokens}
                                onChange={(e) => setConfig({...config, max_tokens: parseInt(e.target.value)})}
                                className="w-full p-3 bg-muted/50 border-none rounded-xl font-bold outline-none"
                            />
                        </div>
                    </div>
                </div>

                {/* Advanced Toggles */}
                <div className="bg-card border border-border/50 rounded-[2.5rem] p-8 shadow-sm space-y-6">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2.5 bg-purple-500/10 rounded-xl">
                            <Zap className="w-5 h-5 text-purple-500" />
                        </div>
                        <h2 className="text-xl font-bold">Execution Features</h2>
                    </div>

                    <div className="space-y-4">
                        {[
                            { key: 'advanced_mode', label: 'Advanced Project Mode', icon: Layers, desc: 'Enable multi-layered project structure.' },
                            { key: 'deep_code', label: 'Deep Code Generation', icon: Code, desc: 'Generate complete, runnable function bodies.' },
                            { key: 'extended_docs', label: 'Extended Documentation', icon: FileText, desc: 'Add detailed architectural explanations.' },
                            { key: 'arch_planning', label: 'Architecture Planning', icon: Settings, desc: 'Include UML and ERD specifications.' },
                        ].map((feature) => (
                            <div key={feature.key} className="flex items-start justify-between p-4 bg-muted/30 rounded-2xl hover:bg-muted/50 transition-colors">
                                <div className="flex gap-3">
                                    <feature.icon className="w-5 h-5 text-muted-foreground mt-0.5" />
                                    <div>
                                        <p className="text-sm font-bold text-foreground">{feature.label}</p>
                                        <p className="text-[10px] text-muted-foreground font-medium">{feature.desc}</p>
                                    </div>
                                </div>
                                <label className="relative inline-flex items-center cursor-pointer">
                                    <input 
                                        type="checkbox" 
                                        className="sr-only peer" 
                                        checked={config.features[feature.key]}
                                        onChange={(e) => setConfig({
                                            ...config, 
                                            features: { ...config.features, [feature.key]: e.target.checked }
                                        })}
                                    />
                                    <div className="w-11 h-6 bg-muted-foreground/20 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary shadow-inner"></div>
                                </label>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
