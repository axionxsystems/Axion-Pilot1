"use client";
import { useState } from "react";
import { api } from "../services/api";
import { Bot, Send, Key, User, Sparkles } from "lucide-react";

export default function VivaAssistant({ projectData }: { projectData: any }) {
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState<{ role: string, content: string }[]>([]);
    const [loading, setLoading] = useState(false);
    const [apiKey, setApiKey] = useState("");

    const handleSend = async () => {
        if (!input.trim() || !apiKey) return;

        const newMsg = { role: "user", content: input };
        setMessages([...messages, newMsg]);
        setInput("");
        setLoading(true);

        try {
            const history = [...messages, newMsg];
            const res = await api.chatViva(apiKey, history, projectData);
            setMessages([...history, { role: "assistant", content: res.response }]);
        } catch (err: any) {
            alert("Error: " + err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="glass mt-8 p-6 rounded-3xl border border-white/10 relative overflow-hidden">
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2 rounded-xl bg-emerald-500/20 text-emerald-400">
                    <Bot className="w-6 h-6" />
                </div>
                <div>
                    <h2 className="text-xl font-bold text-white">Viva Assistant</h2>
                    <p className="text-xs text-muted-foreground">Ask questions about your project architecture</p>
                </div>
            </div>

            {!apiKey && (
                <div className="mb-6 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
                    <label className="text-xs font-semibold text-emerald-400 block mb-2 flex items-center gap-2">
                        <Key className="w-4 h-4" />
                        Enter Groq API Key to Start Chat
                    </label>
                    <input
                        type="password"
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        className="w-full text-sm p-3 rounded-lg bg-black/40 border border-emerald-500/30 text-emerald-100 placeholder:text-emerald-500/50 focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
                        placeholder="gsk_..."
                    />
                </div>
            )}

            <div className="bg-black/40 rounded-2xl border border-white/5 h-[400px] overflow-y-auto p-4 mb-4 space-y-4 scrollbar-ios">
                {messages.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center text-slate-500 opacity-60">
                        <Bot className="w-12 h-12 mb-3" />
                        <p className="text-sm">Ready to help you prepare!</p>
                    </div>
                )}
                {messages.map((m, i) => (
                    <div key={i} className={`flex gap-3 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        {m.role === 'assistant' && (
                            <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0">
                                <Bot className="w-4 h-4 text-emerald-400" />
                            </div>
                        )}
                        <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${m.role === 'user'
                                ? 'bg-primary text-white rounded-br-none'
                                : 'bg-white/10 text-slate-200 rounded-bl-none border border-white/5'
                            }`}>
                            {m.content}
                        </div>
                        {m.role === 'user' && (
                            <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0">
                                <User className="w-4 h-4 text-primary" />
                            </div>
                        )}
                    </div>
                ))}
                {loading && (
                    <div className="flex gap-3">
                        <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center">
                            <Bot className="w-4 h-4 text-emerald-400" />
                        </div>
                        <div className="bg-white/5 rounded-2xl rounded-bl-none px-4 py-3 flex items-center gap-2">
                            <span className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" />
                            <span className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce delay-100" />
                            <span className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce delay-200" />
                        </div>
                    </div>
                )}
            </div>

            <div className="relative">
                <input
                    className="w-full bg-white/5 border border-white/10 rounded-xl pl-4 pr-12 py-4 text-sm text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition-all"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask a question..."
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                    disabled={!apiKey || loading}
                />
                <button
                    onClick={handleSend}
                    disabled={loading || !apiKey}
                    className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg transition-colors disabled:opacity-0 disabled:pointer-events-none"
                >
                    <Send className="w-4 h-4" />
                </button>
            </div>
        </div>
    )
}
