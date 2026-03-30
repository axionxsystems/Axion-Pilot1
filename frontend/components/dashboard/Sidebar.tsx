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
    Pencil
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
            href: user?.is_admin ? "/dashboard/admin" : "/dashboard",
            icon: LayoutDashboard
        },
        {
            name: "My Projects",
            href: "/dashboard/projects",
            icon: Layers
        },
        ...(user?.is_admin ? [{
            name: "Admin Hub",
            href: "/dashboard/admin",
            icon: Shield
        }] : []),
        {
            name: "Profile",
            href: "/dashboard/profile",
            icon: User
        },
        {
            name: "Billing",
            href: "/dashboard/billing",
            icon: CreditCard
        },
        {
            name: "Settings",
            href: "/dashboard/settings",
            icon: Settings
        }
    ];

    return (
        <aside
            className={cn(
                "hidden md:flex flex-col border-r border-border/40 bg-card/40 backdrop-blur-2xl h-screen transition-all duration-300 ease-in-out relative z-30",
                collapsed ? "w-20" : "w-64",
                className
            )}
        >
            <div className="p-6 flex items-center justify-between h-16">
                {!collapsed && <Logo />}
                {collapsed && <Logo variant="minimal" />}
                <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 rounded-full absolute -right-3 top-6 bg-background border shadow-sm z-50 text-muted-foreground hover:text-foreground"
                    onClick={() => setCollapsed(!collapsed)}
                >
                    <ChevronLeft className={cn("h-3 w-3 transition-transform", collapsed && "rotate-180")} />
                </Button>
            </div>

            <div className="flex-1 px-3 py-4 space-y-1 overflow-y-auto scrollbar-hide">
                {links.map((link) => {
                    const isActive = pathname === link.href;
                    return (
                        <Link
                            key={link.href}
                            href={link.href}
                        >
                            <span
                                className={cn(
                                    "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 mb-1",
                                    isActive
                                        ? "bg-primary/10 text-primary shadow-sm"
                                        : "text-muted-foreground hover:bg-muted/50 hover:text-foreground",
                                    collapsed && "justify-center px-2"
                                )}
                            >
                                <link.icon className="h-5 w-5" />
                                {!collapsed && <span>{link.name}</span>}
                            </span>
                        </Link>
                    );
                })}
            </div>

            <div className="p-4 border-t border-border/40">
                <Button
                    variant="ghost"
                    className={cn(
                        "w-full justify-start text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-xl transition-all duration-200",
                        collapsed && "justify-center px-0"
                    )}
                    onClick={logout}
                >
                    <LogOut className="h-5 w-5" />
                    {!collapsed && <span className="ml-3 font-medium">Log out</span>}
                </Button>
            </div>
        </aside>
    );
}
