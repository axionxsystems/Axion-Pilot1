"use client";

import { useState, useEffect } from "react";
import { 
    Cpu, 
    Mail, 
    MessageSquare, 
    Database, 
    ShieldCheck, 
    ShieldAlert, 
    RefreshCw, 
    Settings2, 
    ChevronRight, 
    Zap, 
    History,
    Activity,
    Lock,
    ExternalLink,
    AlertCircle,
    CheckCircle2,
    XCircle
} from "lucide-react";
import { api } from "@/services/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { 
    Dialog, 
    DialogContent, 
    DialogHeader, 
    DialogTitle, 
    DialogDescription,
    DialogFooter
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";

export default function AdminInfrastructure() {
    const [services, setServices] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedService, setSelectedService] = useState<any>(null);
    const [editConfig, setEditConfig] = useState<any>({});
    const [isRotating, setIsRotating] = useState<string | null>(null);

    const fetchStatus = async () => {
        try {
            const data = await api.getInfrastructureStatus();
            setServices(data);
        } catch (err) {
            console.error(err);
            toast.error("Failed to load infrastructure status");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStatus();
    }, []);

    const handleUpdate = async () => {
        try {
            await api.updateInfrastructureConfig(selectedService.id, editConfig);
            toast.success(`${selectedService.name} configuration updated`);
            setSelectedService(null);
            fetchStatus();
        } catch (err) {
            toast.error("Update failed");
        }
    };

    const handleRotate = async (serviceId: string) => {
        setIsRotating(serviceId);
        try {
            await api.rotateServiceKeys(serviceId);
            toast.success("Key rotation sequence initiated");
        } catch (err) {
            toast.error("Rotation failed");
        } finally {
            setIsRotating(null);
        }
    };

    const getIcon = (id: string) => {
        if (id.includes('ai')) return Cpu;
        if (id.includes('email')) return Mail;
        if (id.includes('sms')) return MessageSquare;
        if (id.includes('storage')) return Database;
        return Zap;
    };

    return (
        <div className="max-w-7xl mx-auto space-y-12 animate-in fade-in slide-in-from-bottom-5 duration-1000 px-6 py-10 md:px-0">
            {/* Header section */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 border-b border-white/[0.05] pb-10">
                <div className="space-y-2 group">
                    <div className="flex items-center gap-2 mb-2">
                        <div className="p-1 px-2.5 rounded-lg bg-orange-500/10 border border-orange-500/20 text-[10px] font-black text-orange-400 tracking-[3px] uppercase animate-pulse">
                            Secure Core
                        </div>
                    </div>
                    <h1 className="text-5xl md:text-6xl font-black tracking-tighter text-white flex items-center gap-4 relative leading-none">
                        <span className="bg-gradient-to-r from-orange-400 via-red-400 to-orange-500 bg-clip-text text-transparent drop-shadow-[0_0_15px_rgba(251,146,60,0.3)]">
                            Infrastructure
                        </span>
                    </h1>
                    <p className="text-zinc-500 mt-4 text-lg font-semibold tracking-tight max-w-2xl">
                        Manage external API providers, storage backends, and communication services. 
                        <span className="text-zinc-400"> Secrets are never exposed.</span>
                    </p>
                </div>
                
                <Button 
                    onClick={fetchStatus}
                    variant="outline" 
                    className="rounded-2xl bg-white/[0.03] border-white/10 hover:bg-white/[0.05] font-black tracking-widest text-[10px] uppercase gap-2 h-12 px-6"
                >
                    <RefreshCw className={loading ? "animate-spin w-4 h-4" : "w-4 h-4"} />
                    Refresh Status
                </Button>
            </div>

            {/* Quick Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                    { label: "Active Services", value: services.filter(s => s.status === 'active').length, icon: ShieldCheck, color: "text-emerald-400" },
                    { label: "API Provider Health", value: "99.99%", icon: Activity, color: "text-blue-400" },
                    { label: "Storage Capacity", value: "Unlimited", icon: Database, color: "text-purple-400" },
                ].map((m, i) => (
                    <div key={i} className="bg-[rgba(255,255,255,0.02)] border border-white/5 backdrop-blur-xl rounded-3xl p-6 flex items-center gap-5 transition-all hover:bg-white/[0.04]">
                        <div className={`p-3 rounded-2xl bg-white/5 border border-white/5 ${m.color}`}>
                            <m.icon className="w-5 h-5" />
                        </div>
                        <div>
                            <p className="text-[10px] font-black text-zinc-500 uppercase tracking-widest leading-none mb-1.5">{m.label}</p>
                            <h3 className="text-2xl font-black text-white tracking-tighter">{m.value}</h3>
                        </div>
                    </div>
                ))}
            </div>

            {/* Services Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {services.map((service) => {
                    const Icon = getIcon(service.id);
                    return (
                        <Card key={service.id} className="border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)] backdrop-blur-xl group transition-all duration-300 hover:translate-y-[-4px] overflow-hidden">
                            <CardHeader className="pb-4">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-4">
                                        <div className="p-3 rounded-2xl bg-white/5 border border-white/5 group-hover:scale-110 transition-all duration-500">
                                            <Icon className="w-6 h-6 text-zinc-300 group-hover:text-white transition-colors" />
                                        </div>
                                        <div>
                                            <CardTitle className="text-xl font-bold tracking-tight text-white mb-1">{service.name}</CardTitle>
                                            <div className="flex items-center gap-2">
                                                {service.status === 'active' ? (
                                                    <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[9px] font-black tracking-widest px-2 h-5">
                                                        <CheckCircle2 className="w-2.5 h-2.5 mr-1" />
                                                        OPERATIONAL
                                                    </Badge>
                                                ) : (
                                                    <Badge className="bg-zinc-500/10 text-zinc-500 border-white/5 text-[9px] font-black tracking-widest px-2 h-5">
                                                        <XCircle className="w-2.5 h-2.5 mr-1" />
                                                        INACTIVE
                                                    </Badge>
                                                )}
                                                <span className="text-[10px] text-zinc-600 font-bold uppercase tracking-tighter">Updated: {service.last_updated}</span>
                                            </div>
                                        </div>
                                    </div>
                                    <Button 
                                        variant="ghost" 
                                        size="icon" 
                                        className="rounded-xl hover:bg-white/5 text-zinc-500 hover:text-white"
                                        onClick={() => {
                                            setSelectedService(service);
                                            setEditConfig({}); // Clear for edit (actual values aren't revealed)
                                        }}
                                    >
                                        <Settings2 className="w-5 h-5" />
                                    </Button>
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                <div className="grid grid-cols-2 gap-4">
                                    {Object.entries(service.usage_metrics || {}).map(([label, val]: [string, any]) => (
                                        <div key={label} className="p-4 rounded-2xl bg-white/[0.02] border border-white/5">
                                            <p className="text-[9px] font-black text-zinc-500 uppercase tracking-widest mb-1">{label.replace('_', ' ')}</p>
                                            <p className="text-sm font-black text-zinc-200 tracking-tight">{val}</p>
                                        </div>
                                    ))}
                                    {(!service.usage_metrics || Object.keys(service.usage_metrics).length === 0) && (
                                        <div className="col-span-2 p-4 rounded-2xl bg-white/[0.02] border border-white/5 text-center">
                                            <p className="text-[10px] font-black text-zinc-500 uppercase tracking-widest">No active metrics found</p>
                                        </div>
                                    )}
                                </div>

                                <div className="flex gap-3">
                                    <Button 
                                        variant="outline" 
                                        className="flex-1 rounded-xl bg-white/[0.03] border-white/5 hover:bg-white/10 text-[10px] font-black uppercase tracking-widest h-10 transition-all font-mono"
                                        onClick={() => handleRotate(service.id)}
                                        disabled={isRotating === service.id}
                                    >
                                        <RefreshCw className={`w-3.5 h-3.5 mr-2 ${isRotating === service.id ? 'animate-spin' : ''}`} />
                                        {isRotating === service.id ? 'Rotating...' : 'Rotate Keys'}
                                    </Button>
                                    <Button 
                                        className="flex-1 rounded-xl shadow-lg hover:shadow-primary/10 text-[10px] font-black uppercase tracking-widest h-10"
                                        onClick={() => {
                                            setSelectedService(service);
                                            setEditConfig({});
                                        }}
                                    >
                                        Update Config
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    );
                })}
            </div>

            {/* Config Edit Modal */}
            <Dialog open={!!selectedService} onOpenChange={() => setSelectedService(null)}>
                <DialogContent className="sm:max-w-[500px] border-white/10 bg-[#0A0D14] backdrop-blur-2xl rounded-[2rem] overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-orange-500 to-red-500" />
                    
                    <DialogHeader className="pt-6 px-6">
                        <div className="flex items-center gap-3 mb-2">
                            <Lock className="w-4 h-4 text-orange-400" />
                            <DialogTitle className="text-2xl font-black text-white tracking-tighter">
                                {selectedService?.name} <span className="text-zinc-500 ml-1">Config</span>
                            </DialogTitle>
                        </div>
                        <DialogDescription className="text-zinc-500 font-medium tracking-tight">
                            Update service parameters. <span className="text-orange-400/80">API keys are write-only</span> and never displayed. 
                            Leaving fields empty will preserve existing values.
                        </DialogDescription>
                    </DialogHeader>

                    <div className="p-6 space-y-6">
                        {selectedService?.config_schema?.map((field: any) => (
                            <div key={field.field} className="space-y-2.5">
                                <Label className="text-[10px] font-black text-zinc-400 uppercase tracking-widest ml-1">{field.label}</Label>
                                {field.type === 'boolean' ? (
                                    <div className="flex items-center justify-between p-4 rounded-2xl bg-white/[0.03] border border-white/5">
                                        <span className="text-sm font-bold text-zinc-300">Enable Service</span>
                                        <Switch 
                                            checked={editConfig[field.field] ?? false}
                                            onCheckedChange={(checked) => setEditConfig({...editConfig, [field.field]: checked})}
                                        />
                                    </div>
                                ) : (
                                    <Input 
                                        type={field.type} 
                                        placeholder={field.placeholder || `Enter ${field.label.toLowerCase()}...`}
                                        className="h-14 rounded-2xl bg-white/[0.03] border-white/10 focus:border-orange-500/50 transition-all text-white placeholder:text-zinc-700 font-medium autofill:bg-transparent"
                                        value={editConfig[field.field] || ''}
                                        onChange={(e) => setEditConfig({...editConfig, [field.field]: e.target.value})}
                                    />
                                )}
                            </div>
                        ))}
                    </div>

                    <DialogFooter className="p-6 bg-white/[0.02] gap-3">
                        <Button variant="ghost" onClick={() => setSelectedService(null)} className="rounded-xl text-[10px] font-black uppercase tracking-widest">
                            Cancel
                        </Button>
                        <Button 
                            className="rounded-xl bg-orange-600 hover:bg-orange-500 text-white shadow-lg shadow-orange-600/20 text-[10px] font-black uppercase tracking-widest px-8"
                            onClick={handleUpdate}
                        >
                            Commit Changes
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
