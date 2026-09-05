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
    <div className="p-5 rounded-xl bg-[#161b22] border border-[#30363d] space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Navigation className="w-5 h-5 text-emerald-400" />
          <h3 className="font-semibold text-sm text-white">Field Scout Rover</h3>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <span className="flex items-center gap-1 text-emerald-400">
            <BatteryCharging className="w-4 h-4" /> 84%
          </span>
          <span className="flex items-center gap-1 text-blue-400">
            <Wifi className="w-4 h-4" /> Edge Linked
          </span>
        </div>
      </div>

      {/* Rover Status Display */}
      <div className="grid grid-cols-3 gap-2 text-center text-xs">
        <div className="p-2 bg-[#0d1117] rounded border border-[#21262d]">
          <p className="text-gray-400">Heading</p>
          <p className="text-white font-bold mt-0.5">NW (312°)</p>
        </div>
        <div className="p-2 bg-[#0d1117] rounded border border-[#21262d]">
          <p className="text-gray-400">Speed</p>
          <p className="text-white font-bold mt-0.5">0.6 m/s</p>
        </div>
        <div className="p-2 bg-[#0d1117] rounded border border-[#21262d]">
          <p className="text-gray-400">Current Action</p>
          <p className="text-emerald-400 font-bold mt-0.5">{activeCommand}</p>
        </div>
      </div>

      {/* Manual D-Pad Navigation Controls */}
      <div className="pt-2 flex flex-col items-center justify-center space-y-2">
        <button
          onClick={() => sendRoverCommand("MOVE_FORWARD")}
          className="p-3 bg-[#21262d] hover:bg-emerald-600 active:scale-95 rounded-lg border border-[#30363d] transition"
        >
          <ArrowUp className="w-5 h-5 text-white" />
        </button>
        <div className="flex items-center gap-2">
          <button
            onClick={() => sendRoverCommand("MOVE_LEFT")}
            className="p-3 bg-[#21262d] hover:bg-emerald-600 active:scale-95 rounded-lg border border-[#30363d] transition"
          >
            <ArrowLeft className="w-5 h-5 text-white" />
          </button>
          <button
            onClick={() => sendRoverCommand("STOP")}
            className="p-3 bg-rose-600/30 hover:bg-rose-600 active:scale-95 rounded-lg border border-rose-500 text-rose-300 transition"
          >
            <Square className="w-5 h-5" />
          </button>
          <button
            onClick={() => sendRoverCommand("MOVE_RIGHT")}
            className="p-3 bg-[#21262d] hover:bg-emerald-600 active:scale-95 rounded-lg border border-[#30363d] transition"
          >
            <ArrowRight className="w-5 h-5 text-white" />
          </button>
        </div>
        <button
          onClick={() => sendRoverCommand("MOVE_BACKWARD")}
          className="p-3 bg-[#21262d] hover:bg-emerald-600 active:scale-95 rounded-lg border border-[#30363d] transition"
        >
          <ArrowDown className="w-5 h-5 text-white" />
        </button>
      </div>
    </div>
  );
}