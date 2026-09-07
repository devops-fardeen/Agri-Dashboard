import * as React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "success" | "secondary" | "outline" | "sage";
}

export function Badge({
  className,
  variant = "default",
  ...props
}: BadgeProps) {
  const variantStyles = {
    default: "bg-[#051f20] text-[#daf1de] border-[#051f20]",
    success: "bg-[#daf1de] text-[#051f20] border-[#8eb69b] font-bold",
    secondary: "bg-[#daf1de]/60 text-[#163832] border-[#8eb69b]/40",
    sage: "bg-[#235347] text-[#daf1de] border-[#235347] font-bold",
    outline: "border-[#8eb69b]/60 text-[#163832] bg-white/70",
  };

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold transition-colors",
        variantStyles[variant],
        className
      )}
      {...props}
    />
  );
}
