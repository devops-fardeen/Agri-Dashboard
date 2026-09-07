import React from "react";
import { Badge } from "@/components/ui/badge";
import { Sprout } from "lucide-react";

export function Navbar() {
  return (
    <header className="h-16 border-b border-[#8eb69b]/35 bg-white/75 backdrop-blur-md px-6 flex items-center justify-between shadow-xs">
      <div className="flex items-center gap-2">
        <Sprout className="w-5 h-5 text-[#235347]" />
        <span className="font-extrabold text-sm text-[#051f20] tracking-tight">Agricultural Cloud Telemetry</span>
      </div>
      <Badge variant="success">● Connected</Badge>
    </header>
  );
}
