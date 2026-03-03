import { 
  FileText, 
  Presentation, 
  Code, 
  MessageSquare, 
  Brain,
  Download,
  Shield,
  Zap
} from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "AI Project Generator",
    description: "Enter your topic and get a complete project with abstract, methodology, architecture, and results.",
    gradient: "from-primary to-blue-400",
  },
  {
    icon: FileText,
    title: "Academic Reports",
    description: "Auto-generate IEEE/university format reports with all required sections and citations.",
    gradient: "from-accent to-pink-400",
  },
  {
    icon: Presentation,
    title: "Professional PPTs",
    description: "Beautiful presentation slides that follow academic standards and impress evaluators.",
    gradient: "from-green-400 to-emerald-400",
  },
  {
    icon: Code,
    title: "Source Code",
    description: "Get working, well-commented code ready to run and submit on GitHub.",
    gradient: "from-orange-400 to-amber-400",
  },
  {
    icon: MessageSquare,
    title: "Viva Preparation",
    description: "AI interviewer simulates real viva questions based on your project and department.",
    gradient: "from-pink-400 to-rose-400",
  },
  {
    icon: Download,
    title: "One-Click Downloads",
    description: "Export everything — PDF reports, PPTX, source code ZIP — in seconds.",
    gradient: "from-cyan-400 to-teal-400",
  },
  {
    icon: Shield,
    title: "Plagiarism-Safe",
    description: "Unique content generated for each project, ready for submission.",
    gradient: "from-indigo-400 to-violet-400",
  },
  {
    icon: Zap,
    title: "Instant Results",
    description: "Get your complete project bundle in under 5 minutes, not days.",
    gradient: "from-yellow-400 to-orange-400",
  },
];

const FeaturesSection = () => {
  return (
    <section id="features" className="py-24 relative overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/5 rounded-full blur-[150px]" />
      
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border border-white/10 mb-6">
            <Zap className="w-4 h-4 text-primary" />
            <span className="text-sm font-medium text-foreground">Features</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-foreground mb-6 tracking-tight">
            Everything You Need to{" "}
            <span className="gradient-text">Ace Your Project</span>
          </h2>
          <p className="text-lg text-muted-foreground leading-relaxed">
            From ideation to viva, ProjectPilot AI handles every step of your academic project journey.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            
            return (
              <div
                key={index}
                className="group p-6 rounded-2xl ios-card-solid hover-lift transition-all duration-300"
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300 shadow-lg`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-foreground mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
