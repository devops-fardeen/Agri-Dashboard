import React from "react";
import { Badge } from "@/components/ui/badge";
import { Sprout } from "lucide-react";

export function Navbar() {
  return (
    <header className="h-16 border-b border-white/20 bg-white/10 backdrop-blur-2xl px-6 flex items-center justify-between shadow-sm text-white">
      <div className="flex items-center gap-2">
        <Sprout className="w-5 h-5 text-[#7BBDE8]" />
        <span className="font-extrabold text-sm text-white tracking-tight">Agricultural Cloud Telemetry</span>
      </div>
      <Badge variant="success" className="bg-[#10B981]/20 text-[#34D399] border border-[#10B981]/40 backdrop-blur-md">
        ● Connected
      </Badge>
    </header>
  );
}
