"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Menu, X } from "lucide-react";
import { useAuth } from "@/components/AuthProvider";
import { Logo } from "@/components/ui/Logo";
import { cn } from "@/lib/utils";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const { user, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const navLinks = [
    { name: "Features", href: "#features" },
    { name: "Pricing", href: "#pricing" },
    { name: "FAQ", href: "#faq" },
  ];

  const handleLogoClick = (e: React.MouseEvent) => {
    if (user) {
      e.preventDefault();
      router.push("/dashboard");
    }
  };

  if (pathname.startsWith("/dashboard")) return null; // Don't show this navbar on dashboard

  return (
    <nav
      className={cn(
        "fixed top-0 left-0 right-0 z-50 transition-all duration-300",
        scrolled ? "bg-background/80 backdrop-blur-md border-b" : "bg-transparent"
      )}
    >
      <div className="container mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <Logo onClick={handleLogoClick} />

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <Link
              key={link.name}
              href={link.href}
              className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
            >
              {link.name}
            </Link>
          ))}
        </div>

        {/* Desktop CTA */}
        <div className="hidden md:flex items-center gap-4">
          {!loading && (
            <>
              {user ? (
                <Link href="/dashboard">
                  <Button variant="default" className="rounded-full px-6">
                    Dashboard
                  </Button>
                </Link>
              ) : (
                <>
                  <Link href="/login">
                    <Button variant="ghost" className="text-muted-foreground hover:text-foreground">
                      Log in
                    </Button>
                  </Link>
                  <Link href="/signup">
                    <Button className="rounded-full px-6 bg-foreground text-background hover:bg-foreground/90">
                      Get Started
                    </Button>
                  </Link>
                </>
              )}
            </>
          )}
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="md:hidden p-2 text-foreground"
        >
          {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Navigation */}
      {isOpen && (
        <div className="md:hidden absolute top-16 left-0 right-0 bg-background border-b animate-in slide-in-from-top-5">
          <div className="flex flex-col p-4 gap-4">
            {navLinks.map((link) => (
              <Link
                key={link.name}
                href={link.href}
                onClick={() => setIsOpen(false)}
                className="text-sm font-medium text-muted-foreground hover:text-foreground px-4 py-2"
              >
                {link.name}
              </Link>
            ))}
            <div className="h-px bg-border my-2" />
            {user ? (
              <Link href="/dashboard" onClick={() => setIsOpen(false)}>
                <Button className="w-full">Dashboard</Button>
              </Link>
            ) : (
              <>
                <Link href="/login" onClick={() => setIsOpen(false)}>
                  <Button variant="ghost" className="w-full justify-start">Log in</Button>
                </Link>
                <Link href="/signup" onClick={() => setIsOpen(false)}>
                  <Button className="w-full">Get Started</Button>
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;

