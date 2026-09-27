"use client";

import { useState } from "react";
import { Droplets, Power } from "lucide-react";

interface PumpControlProps {
  zoneId: "ZONE_A" | "ZONE_B";
  zoneName: string;
}

export function PumpControl({ zoneId, zoneName }: PumpControlProps) {
  const [isOn, setIsOn] = useState(false);
  const [loading, setLoading] = useState(false);

  const togglePump = async () => {
    const nextState = !isOn;
    try {
      setLoading(true);
      await fetch("/api/commands", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target: zoneId === "ZONE_A" ? "PUMP_ZONE_A" : "PUMP_ZONE_B",
          action: nextState ? "ON" : "OFF",
        }),
      });
      setIsOn(nextState);
    } catch (err) {
      console.error("Failed to toggle pump:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modern-card p-4 flex items-center justify-between border border-[#E8EEF5] dark:border-[#212C42]">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-2xl bg-[#E0F2FE] dark:bg-[#0284C7]/20 border border-[#BAE6FD] dark:border-[#0284C7]/40 flex items-center justify-center text-[#0284C7] dark:text-[#38BDF8]">
          <Droplets className="w-5 h-5" />
        </div>
        <div>
          <h4 className="text-sm font-extrabold text-[#0F172A] dark:text-[#F8FAFC]">{zoneName} Pump</h4>
          <p className="text-[11px] text-[#64748B] dark:text-[#94A3B8] font-semibold">
            Status: <span className={isOn ? "text-[#059669] dark:text-[#34D399] font-bold" : "text-[#8A94A6] dark:text-[#64748B]"}>{isOn ? "RUNNING • 45 L/h" : "OFF / STANDBY"}</span>
          </p>
        </div>
      </div>

      <button
        onClick={togglePump}
        disabled={loading}
        className={`w-12 h-6 rounded-full p-0.5 transition-colors duration-300 relative cursor-pointer ${
          isOn ? "bg-[#0284C7] shadow-md" : "bg-[#CBD5E1] dark:bg-[#334155]"
        }`}
        title="Toggle Pump State"
      >
        <div
          className={`w-5 h-5 rounded-full bg-white shadow-md transform transition-transform duration-300 ${
            isOn ? "translate-x-6" : "translate-x-0"
          }`}
        />
      </button>
    </div>
  );
}