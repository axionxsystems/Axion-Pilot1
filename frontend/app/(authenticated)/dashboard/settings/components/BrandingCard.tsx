"use client";

import { ChangeEvent, useEffect, useState } from "react";
import { api, Branding } from "@/services/api";
import { useAuth } from "@/components/AuthProvider";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Upload, Image, CheckCircle2, Loader2 } from "lucide-react";

export function BrandingCard() {
    const { user, refreshUser } = useAuth();
    const [branding, setBranding] = useState<Branding | null>(null);
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [logoUploading, setLogoUploading] = useState(false);
    const [message, setMessage] = useState<string | null>(null);

    const [brandName, setBrandName] = useState("");
    const [primaryColor, setPrimaryColor] = useState("#2563eb");
    const [secondaryColor, setSecondaryColor] = useState("#9333ea");
    const [accentColor, setAccentColor] = useState("#f97316");
    const [supportEmail, setSupportEmail] = useState("");

    useEffect(() => {
        if (!user?.org_id || !user?.is_admin) return;
        const orgId = user.org_id;

        const fetchBranding = async () => {
            setLoading(true);
            try {
                const data = await api.getOrgBranding(orgId);
                setBranding(data);
                setBrandName(data.brand_name || "");
                setPrimaryColor(data.primary_color || "#2563eb");
                setSecondaryColor(data.secondary_color || "#9333ea");
                setAccentColor(data.accent_color || "#f97316");
                setSupportEmail(data.support_email || "");
            } catch (err) {
                console.error("Failed to load branding", err);
            } finally {
                setLoading(false);
            }
        };

        fetchBranding();
    }, [user]);

    if (!user?.org_id || !user?.is_admin) {
        return null;
    }

    const handleSave = async () => {
        if (!user?.org_id) return;
        setSaving(true);
        setMessage(null);

        try {
            const updated = await api.updateOrgBranding(user.org_id, {
                brand_name: brandName || null,
                primary_color: primaryColor || null,
                secondary_color: secondaryColor || null,
                accent_color: accentColor || null,
                support_email: supportEmail || null,
            });
            setBranding(updated);
            setMessage("Branding settings saved.");
        } catch (err) {
            console.error(err);
            setMessage("Failed to save branding settings.");
        } finally {
            setSaving(false);
        }
    };

    const handleUploadLogo = async (event: React.ChangeEvent<HTMLInputElement>) => {
        if (!user?.org_id) return;
        const file = event.target.files?.[0];
        if (!file) return;

        setLogoUploading(true);
        setMessage(null);
        try {
            const updated = await api.uploadOrgBrandingLogo(user.org_id, file);
            setBranding(updated);
            setMessage("Logo uploaded successfully.");
            refreshUser();
        } catch (err) {
            console.error(err);
            setMessage("Failed to upload logo.");
        } finally {
            setLogoUploading(false);
        }
    };

    const handleDeleteLogo = async () => {
        if (!user?.org_id) return;
        setLogoUploading(true);
        setMessage(null);
        try {
            await api.deleteOrgBrandingLogo(user.org_id);
            setBranding((prev) => prev ? { ...prev, logo_filename: null, logo_url: null } : prev);
            setMessage("Logo removed.");
        } catch (err) {
            console.error(err);
            setMessage("Failed to delete logo.");
        } finally {
            setLogoUploading(false);
        }
    };

    return (
        <Card className="border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)] backdrop-blur-xl group transition-all duration-300 hover:translate-y-[-4px] overflow-hidden">
            <CardHeader className="pb-4">
                <div className="flex items-center gap-4">
                    <div className="relative group/icon">
                        <div className="absolute -inset-1 bg-gradient-to-r from-emerald-400 to-cyan-500 rounded-xl blur opacity-20 group-hover/icon:opacity-40 transition duration-300" />
                        <div className="relative p-2.5 rounded-xl bg-background/50 border border-white/10 flex items-center justify-center">
                            <Image className="w-5 h-5 text-emerald-400" />
                        </div>
                    </div>
                    <div>
                        <CardTitle className="text-xl font-bold tracking-tight">Enterprise Branding</CardTitle>
                        <CardDescription className="text-zinc-500 font-medium tracking-wide">
                            Customize the organization name, support address, colors, and logo shown to your users.
                        </CardDescription>
                    </div>
                </div>
            </CardHeader>
            <CardContent className="space-y-6">
                <div className="grid grid-cols-1 gap-4">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                        <div>
                            <Label htmlFor="brandName">Brand Name</Label>
                            <Input
                                id="brandName"
                                value={brandName}
                                onChange={(e) => setBrandName(e.target.value)}
                                placeholder="Organization brand"
                            />
                        </div>
                        <div>
                            <Label htmlFor="supportEmail">Support Email</Label>
                            <Input
                                id="supportEmail"
                                type="email"
                                value={supportEmail}
                                onChange={(e) => setSupportEmail(e.target.value)}
                                placeholder="support@company.com"
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        <div>
                            <Label htmlFor="primaryColor">Primary Color</Label>
                            <Input
                                id="primaryColor"
                                type="color"
                                value={primaryColor}
                                onChange={(e) => setPrimaryColor(e.target.value)}
                            />
                        </div>
                        <div>
                            <Label htmlFor="secondaryColor">Secondary Color</Label>
                            <Input
                                id="secondaryColor"
                                type="color"
                                value={secondaryColor}
                                onChange={(e) => setSecondaryColor(e.target.value)}
                            />
                        </div>
                        <div>
                            <Label htmlFor="accentColor">Accent Color</Label>
                            <Input
                                id="accentColor"
                                type="color"
                                value={accentColor}
                                onChange={(e) => setAccentColor(e.target.value)}
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-1 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="logoUpload">Logo</Label>
                            <div className="flex flex-col gap-2">
                                <input
                                    id="logoUpload"
                                    type="file"
                                    accept="image/png,image/jpeg,image/webp,image/svg+xml"
                                    onChange={handleUploadLogo}
                                    className="text-sm file:mr-4 file:rounded-full file:border-0 file:bg-white/10 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-white file:transition-all file:hover:bg-white/20"
                                />
                                {branding?.logo_url ? (
                                    <div className="flex items-center gap-4">
                                        <img src={branding.logo_url} alt="Org logo" className="h-14 w-14 rounded-xl object-contain bg-white/5 border border-white/10" />
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={handleDeleteLogo}
                                            disabled={logoUploading}
                                        >
                                            {logoUploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                                            Delete logo
                                        </Button>
                                    </div>
                                ) : null}
                            </div>
                        </div>
                    </div>

                    {message ? (
                        <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-4 text-sm text-emerald-200">
                            {message}
                        </div>
                    ) : null}

                    <div className="flex flex-wrap gap-3 mt-2">
                        <Button onClick={handleSave} disabled={saving || loading}>
                            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                            Save Branding
                        </Button>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
