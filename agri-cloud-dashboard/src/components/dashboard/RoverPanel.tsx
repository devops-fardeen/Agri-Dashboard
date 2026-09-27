"use client";

import { useState } from "react";
import { Navigation, ArrowUp, ArrowDown, ArrowLeft, ArrowRight, Square, BatteryCharging, Wifi } from "lucide-react";

export function RoverPanel() {
  const [activeCommand, setActiveCommand] = useState<string>("STOP");
  const [sending, setSending] = useState(false);

  const sendRoverCommand = async (action: string) => {
    try {
      setSending(true);
      setActiveCommand(action);
      await fetch("/api/commands", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target: "ROVER", action }),
      });
    } catch (err) {
      console.error("Failed to transmit rover command:", err);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="modern-card p-5 space-y-4 border border-[#E8EEF5] dark:border-[#212C42]">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-2xl bg-[#E0F2FE] dark:bg-[#0284C7]/20 border border-[#BAE6FD] dark:border-[#0284C7]/40 flex items-center justify-center text-[#0284C7] dark:text-[#38BDF8]">
            <Navigation className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-extrabold text-[#0F172A] dark:text-[#F8FAFC]">Field Scout Rover</h3>
            <p className="text-xs text-[#8A94A6] dark:text-[#94A3B8] font-semibold">Autonomous edge navigation unit</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1 text-xs text-[#059669] dark:text-[#34D399] font-bold bg-[#D1FAE5] dark:bg-[#059669]/20 px-2.5 py-0.5 rounded-full border border-[#A7F3D0] dark:border-[#059669]/30">
            <BatteryCharging className="w-3.5 h-3.5 text-[#059669] dark:text-[#34D399]" /> 84%
          </span>
        </div>
      </div>

      {/* Rover Status Indicators */}
      <div className="grid grid-cols-3 gap-2 text-center text-xs">
        <div className="p-2.5 bg-white dark:bg-[#1A2234] rounded-2xl border border-[#E8EEF5] dark:border-[#212C42] shadow-xs">
          <p className="text-[#8A94A6] dark:text-[#94A3B8] text-[10px] uppercase font-bold">Heading</p>
          <p className="text-[#0F172A] dark:text-[#F8FAFC] font-extrabold mt-0.5">NW (312°)</p>
        </div>
        <div className="p-2.5 bg-white dark:bg-[#1A2234] rounded-2xl border border-[#E8EEF5] dark:border-[#212C42] shadow-xs">
          <p className="text-[#8A94A6] dark:text-[#94A3B8] text-[10px] uppercase font-bold">Speed</p>
          <p className="text-[#0F172A] dark:text-[#F8FAFC] font-extrabold mt-0.5">0.6 m/s</p>
        </div>
        <div className="p-2.5 bg-white dark:bg-[#1A2234] rounded-2xl border border-[#E8EEF5] dark:border-[#212C42] shadow-xs">
          <p className="text-[#8A94A6] dark:text-[#94A3B8] text-[10px] uppercase font-bold">Action</p>
          <p className="text-[#0284C7] dark:text-[#38BDF8] font-extrabold mt-0.5 truncate">{activeCommand}</p>
        </div>
      </div>

      {/* D-Pad Directional Controls */}
      <div className="flex flex-col items-center justify-center gap-1.5 py-1">
        <button
          onClick={() => sendRoverCommand("MOVE_FORWARD")}
          className="w-11 h-10 rounded-xl dpad-btn flex items-center justify-center font-bold cursor-pointer"
          title="Forward"
        >
          <ArrowUp className="w-4 h-4" />
        </button>
        <div className="flex items-center gap-2">
          <button
            onClick={() => sendRoverCommand("MOVE_LEFT")}
            className="w-11 h-10 rounded-xl dpad-btn flex items-center justify-center font-bold cursor-pointer"
            title="Left"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <button
            onClick={() => sendRoverCommand("STOP")}
            className="w-12 h-10 rounded-xl bg-[#EF4444] hover:bg-[#DC2626] text-white flex items-center justify-center active:scale-90 transition shadow-md cursor-pointer"
            title="EMERGENCY STOP"
          >
            <Square className="w-4 h-4 fill-white" />
          </button>
          <button
            onClick={() => sendRoverCommand("MOVE_RIGHT")}
            className="w-11 h-10 rounded-xl dpad-btn flex items-center justify-center font-bold cursor-pointer"
            title="Right"
          >
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
        <button
          onClick={() => sendRoverCommand("MOVE_BACKWARD")}
          className="w-11 h-10 rounded-xl dpad-btn flex items-center justify-center font-bold cursor-pointer"
          title="Backward"
        >
          <ArrowDown className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}