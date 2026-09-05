"use client";

import { useState } from "react";
import { Power } from "lucide-react";

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
    <div className="p-4 bg-[#161b22] border border-[#30363d] rounded-xl flex items-center justify-between">
      <div>
        <h4 className="text-sm font-semibold text-white">{zoneName} Pump</h4>
        <p className="text-xs text-gray-400">
          Status: <span className={isOn ? "text-emerald-400 font-bold" : "text-gray-400"}>{isOn ? "RUNNING" : "OFF"}</span>
        </p>
      </div>

      <button
        onClick={togglePump}
        disabled={loading}
        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition shadow ${
          isOn
            ? "bg-rose-600 hover:bg-rose-700 text-white"
            : "bg-emerald-600 hover:bg-emerald-700 text-white"
        }`}
      >
        <Power className="w-3.5 h-3.5" />
        {loading ? "Queueing..." : isOn ? "Turn OFF" : "Turn ON"}
      </button>
    </div>
  );
}