import Link from "next/link";
import { cn } from "@/lib/utils";

interface LogoProps {
    className?: string;
    variant?: "default" | "minimal";
    href?: string;
    onClick?: (e: React.MouseEvent) => void;
}

export function Logo({ className, variant = "default", href = "/", onClick }: LogoProps) {
    return (
        <Link
            href={href}
            onClick={onClick}
            className={cn("flex items-center gap-2.5 group select-none", className)}
        >
            <div className="relative flex h-8 w-8 items-center justify-center rounded-[10px] bg-foreground text-background shadow-sm ring-1 ring-white/10 transition-transform duration-200 group-hover:scale-105 active:scale-95">
                <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="3"
                    className="h-4 w-4"
                >
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <div className="absolute inset-0 rounded-[10px] bg-gradient-to-tr from-white/20 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
            </div>
            {variant === "default" && (
                <span className="font-semibold tracking-tight text-foreground text-[17px]">
                    Project<span className="opacity-70">Pilot</span>
                </span>
            )}
        </Link>
    );
}
