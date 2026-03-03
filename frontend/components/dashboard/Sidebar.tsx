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
    User
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
    const { logout } = useAuth();

    const links = [
        {
            name: "Dashboard",
            href: "/dashboard",
            icon: LayoutDashboard
        },
        {
            name: "New Project",
            href: "/dashboard",
            icon: PlusCircle
        },
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
                "hidden md:flex flex-col border-r bg-card/50 backdrop-blur-xl h-screen transition-all duration-300 ease-in-out relative z-30",
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

            <div className="flex-1 px-3 py-4 space-y-1">
                {links.map((link) => {
                    const isActive = pathname === link.href;
                    return (
                        <Link
                            key={link.href}
                            href={link.href}
                        >
                            <span
                                className={cn(
                                    "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors mb-1",
                                    isActive
                                        ? "bg-primary/10 text-primary"
                                        : "text-muted-foreground hover:bg-muted hover:text-foreground",
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

            <div className="p-4 border-t border-border/50">
                <Button
                    variant="ghost"
                    className={cn(
                        "w-full justify-start text-muted-foreground hover:text-destructive hover:bg-destructive/10",
                        collapsed && "justify-center px-0"
                    )}
                    onClick={logout}
                >
                    <LogOut className="h-5 w-5" />
                    {!collapsed && <span className="ml-3">Log out</span>}
                </Button>
            </div>
        </aside>
    );
}
