"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "./AuthProvider";
import { Loader2 } from "lucide-react";

export default function AdminGuard({ children }: { children: React.ReactNode }) {
    const { user, loading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!loading && (!user || user.email !== "niyant214@gmail.com")) {
            router.push("/dashboard"); // Redirect non-admins to user dashboard
        }
    }, [user, loading, router]);

    if (loading || !user || user.email !== "niyant214@gmail.com") {
        return (
            <div className="h-screen flex flex-col items-center justify-center space-y-4">
                <Loader2 className="w-10 h-10 animate-spin text-primary" />
                <p className="text-muted-foreground font-bold tracking-widest uppercase text-[10px]">Verifying Administrative Clearances...</p>
            </div>
        );
    }

    return <>{children}</>;
}
