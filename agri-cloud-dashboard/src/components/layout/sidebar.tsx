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
    <aside className="w-64 border-r border-white/20 bg-white/10 backdrop-blur-2xl p-4 flex flex-col justify-between text-white">
      <div>
        <div className="flex items-center gap-2.5 px-3 py-3 mb-6 bg-white/10 rounded-2xl border border-white/25 backdrop-blur-md">
          <div className="p-2 bg-gradient-to-tr from-[#0A4174] to-[#7BBDE8] text-white rounded-xl shadow-sm">
            <Sprout className="h-5 w-5" />
          </div>
          <div>
            <span className="font-black text-white tracking-tight block text-base">AgriSmart</span>
            <span className="text-[10px] font-bold text-[#BDD8E9] tracking-widest uppercase">Cloud Central</span>
          </div>
        </div>
        <nav className="space-y-1.5">
          {links.map((link) => {
            const Icon = link.icon;
            return (
              <Link
                key={link.label}
                href={link.href}
                className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-bold text-[#BDD8E9] hover:text-white hover:bg-white/15 transition-colors border border-transparent hover:border-white/20"
              >
                <Icon className="h-4 w-4 text-[#7BBDE8]" />
                <span>{link.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}
