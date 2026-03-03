import { Button } from "@/components/ui/button";
import { ArrowRight, Play, Sparkles, FileText, Presentation, MessageSquare } from "lucide-react";
import { useState } from "react";
import VideoModal from "@/components/ui/VideoModal";

const HeroSection = () => {
  const [isVideoOpen, setIsVideoOpen] = useState(false);

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-24">
      <VideoModal isOpen={isVideoOpen} onClose={() => setIsVideoOpen(false)} videoUrl="/demo.webp" />

      {/* Background Effects */}
      <div className="absolute inset-0 bg-background" />

      {/* Gradient Orbs */}
      <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-primary/20 rounded-full blur-[120px] animate-pulse-slow" />
      <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-accent/20 rounded-full blur-[100px] animate-pulse-slow" style={{ animationDelay: '2s' }} />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary/10 rounded-full blur-[150px]" />

      {/* Grid Pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,hsl(220_13%_15%/0.3)_1px,transparent_1px),linear-gradient(to_bottom,hsl(220_13%_15%/0.3)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_110%)]" />

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-5xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border border-white/20 mb-8 animate-fade-in">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            <span className="text-sm font-medium text-foreground">AI-Powered Project Generation</span>
          </div>

          {/* Main Heading */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight mb-6 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
            Your College Projects,{" "}
            <span className="gradient-text">Done Right</span>
          </h1>

          {/* Subheading */}
          <p className="text-lg sm:text-xl text-muted-foreground max-w-3xl mx-auto mb-10 leading-relaxed animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
            Generate complete academic projects with AI — from abstract to code to viva preparation.
            Get report-ready PDFs, professional PPTs, and ace your viva with our AI interviewer.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16 animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
            <a href="/signup">
              <Button variant="hero" size="xl">
                Start Building Free
                <ArrowRight className="w-5 h-5" />
              </Button>
            </a>
            <Button variant="hero-outline" size="xl" onClick={() => setIsVideoOpen(true)}>
              <Play className="w-5 h-5" />
              Watch Demo
            </Button>
          </div>

          {/* Feature Cards Preview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl mx-auto animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
            <div className="group p-6 rounded-2xl ios-card hover-lift hover-glow transition-all duration-300">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary/30 to-primary/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                <FileText className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-semibold text-foreground mb-2">Complete Reports</h3>
              <p className="text-sm text-muted-foreground">Auto-generated PDFs with all sections your college needs</p>
            </div>

            <div className="group p-6 rounded-2xl ios-card hover-lift transition-all duration-300" style={{ transitionDelay: '50ms' }}>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent/30 to-accent/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                <Presentation className="w-6 h-6 text-accent" />
              </div>
              <h3 className="font-semibold text-foreground mb-2">Pro Presentations</h3>
              <p className="text-sm text-muted-foreground">Beautiful PPTs ready for your final submissions</p>
            </div>

            <div className="group p-6 rounded-2xl ios-card hover-lift transition-all duration-300" style={{ transitionDelay: '100ms' }}>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-pink-500/30 to-pink-500/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                <MessageSquare className="w-6 h-6 text-pink-400" />
              </div>
              <h3 className="font-semibold text-foreground mb-2">Viva Assistant</h3>
              <p className="text-sm text-muted-foreground">AI-powered mock interviews to ace your viva</p>
            </div>
          </div>

          {/* Trust Indicators */}
          <div className="mt-16 animate-fade-in-up" style={{ animationDelay: '0.5s' }}>
            <p className="text-sm text-muted-foreground mb-6">Trusted by students from</p>
            <div className="flex flex-wrap items-center justify-center gap-8">
              {["IIT Delhi", "VIT", "SRM", "BITS", "NIT"].map((college) => (
                <span key={college} className="text-lg font-semibold text-muted-foreground/60 hover:text-muted-foreground transition-colors">
                  {college}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
