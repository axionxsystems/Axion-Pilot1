"use client";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
    LayoutDashboard,
    PlusCircle,
    Settings,
    CreditCard,
    LogOut,
    ChevronLeft,
    User,
    Layers,
    Shield,
    Sparkles,
    Zap
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Logo } from "@/components/ui/Logo";
import { useAuth } from "@/components/AuthProvider";

interface SidebarProps {
    className?: string;
}

export function Sidebar({ className }: SidebarProps) {
    const pathname = usePathname();
    const [collapsed, setCollapsed] = useState(false);
    const { logout, user } = useAuth();

    const links = [
        {
            name: "Dashboard",
            href: "/dashboard",
            icon: LayoutDashboard,
            color: "text-blue-400"
        },
        {
            name: "My Projects",
            href: "/dashboard/projects",
            icon: Layers,
            color: "text-purple-400"
        },
        ...(user?.is_admin ? [
            {
                name: "Admin Hub",
                href: "/dashboard/admin",
                icon: Shield,
                color: "text-red-400"
            },
            {
                name: "Infrastructure",
                href: "/dashboard/admin/infrastructure",
                icon: Zap,
                color: "text-orange-400"
            }
        ] : []),
        {
            name: "Profile",
            href: "/dashboard/profile",
            icon: User,
            color: "text-emerald-400"
        },
        {
            name: "Billing",
            href: "/dashboard/billing",
            icon: CreditCard,
            color: "text-orange-400"
        },
        {
            name: "Settings",
            href: "/dashboard/settings",
            icon: Settings,
            color: "text-zinc-400"
        }
    ];

    return (
        <aside
            className={cn(
                "hidden md:flex flex-col border-r border-white/[0.05] bg-[rgba(10,13,20,0.8)] backdrop-blur-3xl h-screen transition-all duration-500 ease-[cubic-bezier(0.4,0,0.2,1)] relative z-30",
                collapsed ? "w-24" : "w-72",
                className
            )}
        >
            {/* Header / Logo */}
            <div className="p-8 flex items-center justify-between h-24 relative">
                {!collapsed && (
                    <div className="animate-in fade-in slide-in-from-left-4 duration-500">
                        <Logo />
                    </div>
                )}
                {collapsed && (
                    <div className="animate-in fade-in zoom-in duration-500 mx-auto">
                        <Logo variant="minimal" />
                    </div>
                )}
                
                <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 rounded-2xl absolute -right-4 top-20 bg-[rgba(255,255,255,0.03)] border border-white/10 shadow-2xl backdrop-blur-xl z-50 text-zinc-500 hover:text-white hover:bg-white/10 transition-all duration-300"
                    onClick={() => setCollapsed(!collapsed)}
                >
                    <ChevronLeft className={cn("h-4 w-4 transition-transform duration-500", collapsed && "rotate-180")} />
                </Button>
            </div>

            {/* Navigation Links */}
            <div className="flex-1 px-4 py-6 space-y-2 overflow-y-auto scrollbar-hide">
                {!collapsed && (
                    <p className="px-4 text-[10px] font-black text-zinc-600 uppercase tracking-[3px] mb-4 animate-in fade-in duration-700">Main Menu</p>
                )}
                
                {links.map((link) => {
                    const isActive = link.href === "/dashboard" 
                        ? pathname === "/dashboard"
                        : pathname.startsWith(link.href);
                        
                    return (
                        <Link
                            key={link.href}
                            href={link.href}
                            className="block group"
                        >
                            <span
                                className={cn(
                                    "flex items-center gap-4 px-4 py-3.5 rounded-[1.25rem] text-sm font-bold transition-all duration-300 relative overflow-hidden",
                                    isActive
                                        ? "bg-white/[0.03] text-white shadow-[0_10px_30px_-10px_rgba(0,0,0,0.5)] border border-white/10"
                                        : "text-zinc-500 hover:text-zinc-200 hover:bg-white/[0.02]",
                                    collapsed && "justify-center px-0 h-14 w-14 mx-auto"
                                )}
                            >
                                {/* Active Indicator Glow Bar */}
                                {isActive && (
                                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-primary rounded-full shadow-[0_0_15px_rgba(59,130,246,0.8)] animate-in slide-in-from-left-full duration-500" />
                                )}

                                <link.icon className={cn(
                                    "h-5 w-5 transition-all duration-300 group-hover:scale-110",
                                    isActive ? "text-primary" : "text-zinc-500 group-hover:text-zinc-300"
                                )} />
                                
                                {!collapsed && (
                                    <span className="tracking-tight transition-all duration-300 group-hover:translate-x-1">{link.name}</span>
                                )}

                                {/* Hover Glow Effect (Background) */}
                                <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 -z-10" />
                            </span>
                        </Link>
                    );
                })}
            </div>

            {/* Footer / User / Logout */}
            <div className="p-6 space-y-4">
                {!collapsed && (
                    <div className="p-4 rounded-3xl bg-gradient-to-br from-blue-500/10 to-indigo-500/10 border border-blue-500/20 relative overflow-hidden group/pro animate-in fade-in slide-in-from-bottom-4 duration-700">
                        <div className="absolute -right-4 -top-4 w-16 h-16 bg-blue-500/10 blur-2xl group-hover/pro:scale-150 transition-transform duration-700" />
                        <div className="flex items-center gap-3 mb-2 relative z-10">
                            <Zap className="w-4 h-4 text-blue-400 fill-blue-400/20" />
                            <span className="text-[10px] font-black text-blue-400 uppercase tracking-widest">Pro Version</span>
                        </div>
                        <p className="text-[11px] text-zinc-400 font-medium leading-relaxed mb-3">Get unlimited AI reports & 4K exports.</p>
                        <Link href="/dashboard/billing" className="block w-full">
                            <button className="w-full py-2 bg-blue-500 hover:bg-blue-400 text-white text-[10px] font-black uppercase tracking-widest rounded-xl transition-all shadow-lg shadow-blue-500/20 active:scale-95">Upgrade</button>
                        </Link>
                    </div>
                )}

                <div className="pt-4 border-t border-white/[0.05] space-y-2">
                    <Button
                        variant="ghost"
                        className={cn(
                            "w-full justify-start h-12 rounded-[1.25rem] text-zinc-500 hover:text-red-400 hover:bg-red-500/10 transition-all duration-300 font-bold text-sm group/logout",
                            collapsed && "justify-center px-0 h-14 w-14 mx-auto"
                        )}
                        onClick={logout}
                    >
                        <LogOut className="h-5 w-5 transition-transform group-hover/logout:-translate-x-1" />
                        {!collapsed && <span className="ml-4 transition-all duration-300 group-hover/logout:translate-x-1">Sign Out</span>}
                    </Button>
                </div>
            </div>
        </aside>
    );
}
