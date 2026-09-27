"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Sprout,
  ArrowLeft,
  Droplets,
  Thermometer,
  ShieldCheck,
  Settings2,
  Sliders,
  Sparkles,
  MapPin,
  CheckCircle2,
} from "lucide-react";

export default function ZonesPage() {
  const [selectedZone, setSelectedZone] = useState<"A" | "B">("A");
  const [targetMoistA, setTargetMoistA] = useState(65);
  const [targetMoistB, setTargetMoistB] = useState(55);

  return (
    <main className="min-h-screen bg-[var(--background)] text-[var(--foreground)] p-4 sm:p-6 pb-24 transition-colors duration-300">
      <div className="max-w-md md:max-w-3xl mx-auto space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Link
            href="/"
            className="w-10 h-10 rounded-full bg-white dark:bg-[#1A2234] border border-[#E8EEF5] dark:border-[#212C42] flex items-center justify-center text-[#0F172A] dark:text-[#F8FAFC] hover:bg-[#EEF2F6] dark:hover:bg-[#222C42] transition shadow-xs"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="text-center">
            <h1 className="text-xl font-black text-[#0F172A] dark:text-[#F8FAFC] tracking-tight">Zone Management</h1>
            <p className="text-xs text-[#8A94A6] dark:text-[#94A3B8] font-semibold">Irrigation & Microclimate Boundaries</p>
          </div>
          <div className="w-10" />
        </div>

        {/* Zone Selector */}
        <div className="flex gap-3">
          <button
            onClick={() => setSelectedZone("A")}
            className={`flex-1 p-4 rounded-2xl transition-all border cursor-pointer ${
              selectedZone === "A"
                ? "bg-[#0284C7] text-white border-[#0284C7] shadow-lg"
                : "modern-card text-[#0F172A] dark:text-[#F8FAFC] hover:border-[#3B82F6]"
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-base font-black">Zone A</span>
              <span className={`w-2.5 h-2.5 rounded-full ${selectedZone === "A" ? "bg-white" : "bg-[#0284C7]"}`} />
            </div>
            <p className="text-xs opacity-90 font-medium">🍅 Tomato Open Field</p>
            <span className="text-[10px] font-mono mt-2 block opacity-75">Node: EDGE_01</span>
          </button>

          <button
            onClick={() => setSelectedZone("B")}
            className={`flex-1 p-4 rounded-2xl transition-all border cursor-pointer ${
              selectedZone === "B"
                ? "bg-[#059669] text-white border-[#059669] shadow-lg"
                : "modern-card text-[#0F172A] dark:text-[#F8FAFC] hover:border-[#10B981]"
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-base font-black">Zone B</span>
              <span className={`w-2.5 h-2.5 rounded-full ${selectedZone === "B" ? "bg-white" : "bg-[#059669]"}`} />
            </div>
            <p className="text-xs opacity-90 font-medium">🌿 Micro-Misting Greenhouse</p>
            <span className="text-[10px] font-mono mt-2 block opacity-75">Node: EDGE_02</span>
          </button>
        </div>

        {/* Zone Details & Thresholds */}
        <div className="modern-card p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-[#E8EEF5] dark:border-[#212C42] pb-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-[#E0F2FE] dark:bg-[#0284C7]/20 rounded-xl border border-[#BAE6FD] dark:border-[#0284C7]/40 text-[#0284C7] dark:text-[#38BDF8]">
                <MapPin className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-extrabold text-[#0F172A] dark:text-[#F8FAFC]">
                  {selectedZone === "A" ? "Field A — Tomato Plot 1" : "Field B — High Tunnel Hydro"}
                </h3>
                <p className="text-xs text-[#8A94A6] dark:text-[#94A3B8] font-semibold">LoRa Channel {selectedZone === "A" ? "1" : "2"} • 433 MHz</p>
              </div>
            </div>
            <span className="px-3 py-1 rounded-full bg-[#D1FAE5] dark:bg-[#059669]/20 text-[#059669] dark:text-[#34D399] text-xs font-bold border border-[#A7F3D0] dark:border-[#059669]/30">
              Active Control
            </span>
          </div>

          {/* Moisture Threshold Slider */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-[#64748B] dark:text-[#94A3B8] flex items-center gap-1.5">
                <Droplets className="w-4 h-4 text-[#0284C7]" /> Target Soil Hydration
              </span>
              <span className="text-lg font-black text-[#0F172A] dark:text-[#F8FAFC]">
                {selectedZone === "A" ? targetMoistA : targetMoistB}%
              </span>
            </div>
            <input
              type="range"
              min="30"
              max="90"
              value={selectedZone === "A" ? targetMoistA : targetMoistB}
              onChange={(e) =>
                selectedZone === "A"
                  ? setTargetMoistA(Number(e.target.value))
                  : setTargetMoistB(Number(e.target.value))
              }
              className="w-full accent-[#0284C7] cursor-pointer"
            />
            <div className="flex justify-between text-[11px] text-[#8A94A6] dark:text-[#94A3B8] font-semibold">
              <span>Dry / Stressed (30%)</span>
              <span>Optimal Tomato (60-75%)</span>
              <span>Saturated (90%)</span>
            </div>
          </div>

          {/* Environmental Targets */}
          <div className="grid grid-cols-2 gap-3 pt-2">
            <div className="p-4 rounded-2xl bg-[#F8FAFC] dark:bg-[#1A2234] border border-[#E8EEF5] dark:border-[#212C42] space-y-1">
              <span className="text-[11px] text-[#8A94A6] dark:text-[#94A3B8] font-bold uppercase">Canopy Temp Target</span>
              <p className="text-xl font-black text-[#0F172A] dark:text-[#F8FAFC]">22°C – 28°C</p>
              <p className="text-[10px] text-[#059669] dark:text-[#34D399] font-semibold">Automatic ventilation link</p>
            </div>
            <div className="p-4 rounded-2xl bg-[#F8FAFC] dark:bg-[#1A2234] border border-[#E8EEF5] dark:border-[#212C42] space-y-1">
              <span className="text-[11px] text-[#8A94A6] dark:text-[#94A3B8] font-bold uppercase">Max Daily Fertigation</span>
              <p className="text-xl font-black text-[#0F172A] dark:text-[#F8FAFC]">3 Cycles / Day</p>
              <p className="text-[10px] text-[#0284C7] dark:text-[#38BDF8] font-semibold">Pulse drip scheduling</p>
            </div>
          </div>

          <button
            onClick={() => alert("Zone parameters saved and synced with edge station!")}
            className="w-full py-3.5 rounded-2xl bg-[#0F172A] dark:bg-[#0284C7] hover:bg-[#1E293B] dark:hover:bg-[#0369A1] text-white font-bold text-sm shadow-xl flex items-center justify-center gap-2 transition cursor-pointer active:scale-98"
          >
            <CheckCircle2 className="w-4 h-4 text-[#34D399]" />
            <span>Save & Dispatch to Edge Station</span>
          </button>
        </div>
      </div>
    </main>
  );
}
