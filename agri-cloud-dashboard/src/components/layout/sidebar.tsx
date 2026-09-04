import React from "react";
import Link from "next/link";
import { Sprout, LayoutDashboard, MapPin, Settings } from "lucide-react";

export function Sidebar() {
  const links = [
    { label: "Overview", href: "/", icon: LayoutDashboard },
    { label: "Zones", href: "/zones", icon: MapPin },
    { label: "Settings", href: "#", icon: Settings },
  ];

  return (
    <aside className="w-64 border-r border-zinc-800 bg-[#0c1219] p-4 flex flex-col justify-between">
      <div>
        <div className="flex items-center gap-2 px-2 py-3 mb-6">
          <Sprout className="h-6 w-6 text-emerald-400" />
          <span className="font-bold text-white tracking-tight">AgriSmart</span>
        </div>
        <nav className="space-y-1">
          {links.map((link) => {
            const Icon = link.icon;
            return (
              <Link
                key={link.label}
                href={link.href}
                className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-zinc-400 hover:text-white hover:bg-zinc-800/60 transition-colors"
              >
                <Icon className="h-4 w-4" />
                <span>{link.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}
