import React from "react";
import { Badge } from "@/components/ui/badge";

export function Navbar() {
  return (
    <header className="h-16 border-b border-zinc-800 bg-[#0a0e14]/80 backdrop-blur px-6 flex items-center justify-between">
      <div className="font-medium text-sm text-zinc-300">Agricultural Cloud Telemetry</div>
      <Badge variant="success">Connected</Badge>
    </header>
  );
}
