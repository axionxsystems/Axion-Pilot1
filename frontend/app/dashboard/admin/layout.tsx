"use client";

import AdminGuard from "@/components/AdminGuard";
import AdminHeader from "@/components/admin/AdminHeader";

export default function AdminLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <AdminGuard>
            <div className="max-w-7xl mx-auto px-4 md:px-0">
                <AdminHeader />
                <div className="animate-in fade-in zoom-in-95 duration-500">
                    {children}
                </div>
            </div>
        </AdminGuard>
    );
}
