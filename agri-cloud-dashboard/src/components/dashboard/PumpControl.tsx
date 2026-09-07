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
    <div className="glass-panel rounded-[24px] p-4 flex items-center justify-between border border-[#8eb69b]/35">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-2xl bg-[#daf1de] border border-[#8eb69b]/50 flex items-center justify-center text-[#235347]">
          <Droplets className="w-5 h-5" />
        </div>
        <div>
          <h4 className="text-sm font-extrabold text-[#051f20]">{zoneName} Pump</h4>
          <p className="text-[11px] text-[#163832] font-semibold">
            Status: <span className={isOn ? "text-[#235347] font-bold" : "text-[#163832]"}>{isOn ? "RUNNING • 45 L/h" : "OFF / STANDBY"}</span>
          </p>
        </div>
      </div>

      <button
        onClick={togglePump}
        disabled={loading}
        className={`w-12 h-6 rounded-full p-0.5 transition-colors duration-300 relative ${
          isOn ? "bg-[#235347] shadow-md" : "bg-[#daf1de]"
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