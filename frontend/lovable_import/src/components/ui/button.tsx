import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl text-sm font-semibold ring-offset-background transition-all duration-200 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90 shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/30 hover:-translate-y-0.5 active:translate-y-0 active:shadow-md",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90 shadow-lg shadow-destructive/25",
        outline: "border border-white/20 bg-white/5 backdrop-blur-md hover:bg-white/10 hover:border-white/30 text-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80 border border-white/10",
        ghost: "hover:bg-white/10 text-foreground",
        link: "text-primary underline-offset-4 hover:underline",
        gradient: "bg-gradient-to-r from-primary to-accent text-white shadow-lg shadow-primary/30 hover:shadow-xl hover:shadow-primary/40 hover:-translate-y-0.5 active:translate-y-0",
        hero: "bg-gradient-to-r from-primary via-accent to-primary text-white font-semibold shadow-xl shadow-primary/40 hover:shadow-2xl hover:shadow-primary/50 hover:-translate-y-1 active:translate-y-0 animate-gradient bg-[length:200%_200%]",
        "hero-outline": "border border-white/20 bg-white/5 backdrop-blur-xl text-foreground hover:bg-white/10 hover:border-white/40",
        accent: "bg-accent text-accent-foreground hover:bg-accent/90 shadow-lg shadow-accent/30 hover:-translate-y-0.5",
        glass: "backdrop-blur-xl bg-white/10 border border-white/20 text-foreground hover:bg-white/15 hover:border-white/30",
      },
      size: {
        default: "h-11 px-5 py-2.5",
        sm: "h-9 rounded-lg px-4 text-xs",
        lg: "h-12 rounded-xl px-8 text-base",
        xl: "h-14 rounded-2xl px-10 text-lg",
        icon: "h-11 w-11 rounded-xl",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />;
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
