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
      "bg-[#051f20] text-[#daf1de] hover:bg-[#0b2b26] font-bold shadow-lg shadow-[#051f20]/20 active:scale-[0.98]",
    secondary:
      "bg-[#235347] text-white hover:bg-[#163832] font-bold shadow-md shadow-[#235347]/20 active:scale-[0.98]",
    outline:
      "border border-[#8eb69b]/60 bg-white/80 text-[#051f20] hover:bg-[#daf1de]/60 active:scale-[0.98]",
    ghost:
      "bg-transparent text-[#163832] hover:bg-[#daf1de]/50 hover:text-[#051f20]",
  };

  const sizeStyles = {
    sm: "h-8 px-3 text-xs rounded-lg",
    md: "h-10 px-4 text-sm rounded-xl",
    lg: "h-12 px-6 text-base rounded-2xl",
  };

  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 font-semibold transition-all duration-200 disabled:pointer-events-none disabled:opacity-50 cursor-pointer",
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
      {...props}
    />
  );
}
