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
    <aside className="w-64 border-r border-[#8eb69b]/35 bg-white/85 backdrop-blur-lg p-4 flex flex-col justify-between">
      <div>
        <div className="flex items-center gap-2.5 px-3 py-3 mb-6 bg-[#daf1de]/50 rounded-2xl border border-[#8eb69b]/30">
          <div className="p-2 bg-[#051f20] text-[#daf1de] rounded-xl shadow-sm">
            <Sprout className="h-5 w-5" />
          </div>
          <div>
            <span className="font-black text-[#051f20] tracking-tight block text-base">AgriSmart</span>
            <span className="text-[10px] font-bold text-[#163832] tracking-widest uppercase">Cloud Central</span>
          </div>
        </div>
        <nav className="space-y-1.5">
          {links.map((link) => {
            const Icon = link.icon;
            return (
              <Link
                key={link.label}
                href={link.href}
                className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-bold text-[#163832] hover:text-[#051f20] hover:bg-[#daf1de]/60 transition-colors"
              >
                <Icon className="h-4 w-4 text-[#235347]" />
                <span>{link.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}
