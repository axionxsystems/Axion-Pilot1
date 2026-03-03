import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Menu, X, Sparkles } from "lucide-react";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  const navLinks = [
    { name: "Features", href: "#features" },
    { name: "How It Works", href: "#how-it-works" },
    { name: "Pricing", href: "#pricing" },
    { name: "FAQ", href: "#faq" },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50">
      <div className="mx-4 mt-4">
        <div className="glass rounded-2xl border border-white/10 shadow-ios">
          <div className="container mx-auto px-6">
            <div className="flex items-center justify-between h-16">
              {/* Logo */}
              <Link to="/" className="flex items-center gap-3 group">
                <div className="relative">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg shadow-primary/30 group-hover:shadow-xl group-hover:shadow-primary/40 transition-all duration-300">
                    <Sparkles className="w-5 h-5 text-white" />
                  </div>
                </div>
                <span className="text-lg font-bold text-foreground tracking-tight">
                  Project<span className="gradient-text">Pilot</span>
                </span>
              </Link>

              {/* Desktop Navigation */}
              <div className="hidden lg:flex items-center gap-1">
                {navLinks.map((link) => (
                  <a
                    key={link.name}
                    href={link.href}
                    className="px-4 py-2 text-muted-foreground hover:text-foreground transition-colors duration-200 text-sm font-medium rounded-lg hover:bg-white/5"
                  >
                    {link.name}
                  </a>
                ))}
              </div>

              {/* Desktop CTA */}
              <div className="hidden lg:flex items-center gap-3">
                <Button variant="ghost" size="sm">
                  Sign In
                </Button>
                <Button variant="gradient" size="sm">
                  Get Started
                </Button>
              </div>

              {/* Mobile Menu Button */}
              <button
                onClick={() => setIsOpen(!isOpen)}
                className="lg:hidden p-2 rounded-xl hover:bg-white/10 transition-colors"
              >
                {isOpen ? (
                  <X className="w-6 h-6 text-foreground" />
                ) : (
                  <Menu className="w-6 h-6 text-foreground" />
                )}
              </button>
            </div>

            {/* Mobile Navigation */}
            {isOpen && (
              <div className="lg:hidden py-4 border-t border-white/10 animate-fade-in">
                <div className="flex flex-col gap-1">
                  {navLinks.map((link) => (
                    <a
                      key={link.name}
                      href={link.href}
                      onClick={() => setIsOpen(false)}
                      className="px-4 py-3 text-muted-foreground hover:text-foreground hover:bg-white/5 rounded-xl transition-all duration-200 text-sm font-medium"
                    >
                      {link.name}
                    </a>
                  ))}
                  <div className="flex flex-col gap-3 pt-4 mt-2 border-t border-white/10">
                    <Button variant="ghost" className="w-full justify-center">
                      Sign In
                    </Button>
                    <Button variant="gradient" className="w-full justify-center">
                      Get Started
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
