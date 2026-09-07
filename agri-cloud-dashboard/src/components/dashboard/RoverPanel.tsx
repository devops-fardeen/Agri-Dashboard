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
    <div className="glass-panel-glow rounded-[28px] p-5 space-y-4 border border-[#8eb69b]/40">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-2xl bg-[#daf1de] border border-[#8eb69b]/50 flex items-center justify-center text-[#235347]">
            <Navigation className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-extrabold text-[#051f20]">Field Scout Rover</h3>
            <p className="text-xs text-[#163832] font-semibold">Autonomous edge navigation unit</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1 text-xs text-[#051f20] font-bold bg-[#daf1de] px-2.5 py-0.5 rounded-full border border-[#8eb69b]/50">
            <BatteryCharging className="w-3.5 h-3.5 text-[#235347]" /> 84%
          </span>
        </div>
      </div>

      {/* Rover Status Indicators */}
      <div className="grid grid-cols-3 gap-2 text-center text-xs">
        <div className="p-2.5 bg-white rounded-2xl border border-[#8eb69b]/35 shadow-sm">
          <p className="text-[#163832] text-[10px] uppercase font-bold">Heading</p>
          <p className="text-[#051f20] font-extrabold mt-0.5">NW (312°)</p>
        </div>
        <div className="p-2.5 bg-white rounded-2xl border border-[#8eb69b]/35 shadow-sm">
          <p className="text-[#163832] text-[10px] uppercase font-bold">Speed</p>
          <p className="text-[#051f20] font-extrabold mt-0.5">0.6 m/s</p>
        </div>
        <div className="p-2.5 bg-white rounded-2xl border border-[#8eb69b]/35 shadow-sm">
          <p className="text-[#163832] text-[10px] uppercase font-bold">Action</p>
          <p className="text-[#235347] font-extrabold mt-0.5 truncate">{activeCommand}</p>
        </div>
      </div>

      {/* D-Pad Directional Controls */}
      <div className="flex flex-col items-center justify-center gap-1.5 py-1">
        <button
          onClick={() => sendRoverCommand("MOVE_FORWARD")}
          className="w-11 h-10 rounded-xl glass-pill flex items-center justify-center text-[#051f20] hover:bg-[#8eb69b]/30 active:scale-90 transition shadow-sm font-bold"
          title="Forward"
        >
          <ArrowUp className="w-4 h-4 text-[#051f20]" />
        </button>
        <div className="flex items-center gap-2">
          <button
            onClick={() => sendRoverCommand("MOVE_LEFT")}
            className="w-11 h-10 rounded-xl glass-pill flex items-center justify-center text-[#051f20] hover:bg-[#8eb69b]/30 active:scale-90 transition shadow-sm font-bold"
            title="Left"
          >
            <ArrowLeft className="w-4 h-4 text-[#051f20]" />
          </button>
          <button
            onClick={() => sendRoverCommand("STOP")}
            className="w-12 h-10 rounded-xl bg-gradient-to-r from-[#be123c] to-[#9f1239] text-white flex items-center justify-center active:scale-90 transition shadow-md"
            title="EMERGENCY STOP"
          >
            <Square className="w-4 h-4 fill-white" />
          </button>
          <button
            onClick={() => sendRoverCommand("MOVE_RIGHT")}
            className="w-11 h-10 rounded-xl glass-pill flex items-center justify-center text-[#051f20] hover:bg-[#8eb69b]/30 active:scale-90 transition shadow-sm font-bold"
            title="Right"
          >
            <ArrowRight className="w-4 h-4 text-[#051f20]" />
          </button>
        </div>
        <button
          onClick={() => sendRoverCommand("MOVE_BACKWARD")}
          className="w-11 h-10 rounded-xl glass-pill flex items-center justify-center text-[#051f20] hover:bg-[#8eb69b]/30 active:scale-90 transition shadow-sm font-bold"
          title="Backward"
        >
          <ArrowDown className="w-4 h-4 text-[#051f20]" />
        </button>
      </div>
    </div>
  );
}