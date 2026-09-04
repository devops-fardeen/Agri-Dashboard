import * as React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "secondary" | "outline" | "ghost";
  size?: "sm" | "md" | "lg";
}

export function Button({
  className,
  variant = "default",
  size = "md",
  ...props
}: ButtonProps) {
  const variantStyles = {
    default:
      "bg-emerald-500 text-zinc-950 hover:bg-emerald-400 font-semibold shadow-lg shadow-emerald-500/20 active:scale-[0.98]",
    secondary:
      "bg-zinc-800 text-zinc-100 hover:bg-zinc-700 active:scale-[0.98]",
    outline:
      "border border-zinc-700/80 bg-transparent text-zinc-200 hover:bg-zinc-800/60 active:scale-[0.98]",
    ghost:
      "bg-transparent text-zinc-300 hover:bg-zinc-800/50 hover:text-white",
  };

  const sizeStyles = {
    sm: "h-8 px-3 text-xs rounded-lg",
    md: "h-10 px-4 text-sm rounded-xl",
    lg: "h-12 px-6 text-base rounded-xl",
  };

  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 font-medium transition-all duration-200 disabled:pointer-events-none disabled:opacity-50 cursor-pointer",
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
      {...props}
    />
  );
}
