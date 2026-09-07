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
    <main className="min-h-screen bg-[#f0f7f2] text-[#051f20] p-4 sm:p-6 pb-24">
      <div className="max-w-md md:max-w-3xl mx-auto space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Link
            href="/"
            className="w-10 h-10 rounded-full glass-pill flex items-center justify-center text-[#163832] hover:text-[#051f20] hover:border-[#235347] transition shadow-xs"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="text-center">
            <h1 className="text-xl font-black text-[#051f20] tracking-tight">Zone Management</h1>
            <p className="text-xs text-[#163832] font-semibold">Irrigation & Microclimate Boundaries</p>
          </div>
          <div className="w-10" />
        </div>

        {/* Zone Selector */}
        <div className="flex gap-3">
          <button
            onClick={() => setSelectedZone("A")}
            className={`flex-1 p-4 rounded-2xl transition-all border ${
              selectedZone === "A"
                ? "bg-[#051f20] text-[#daf1de] border-[#051f20] shadow-lg"
                : "glass-panel text-[#163832] border-[#8eb69b]/40 hover:border-[#235347]"
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-base font-black">Zone A</span>
              <span className={`w-2.5 h-2.5 rounded-full ${selectedZone === "A" ? "bg-[#8eb69b]" : "bg-[#235347]"}`} />
            </div>
            <p className="text-xs opacity-90 font-medium">🍅 Tomato Open Field</p>
            <span className="text-[10px] font-mono mt-2 block opacity-75">Node: EDGE_01</span>
          </button>

          <button
            onClick={() => setSelectedZone("B")}
            className={`flex-1 p-4 rounded-2xl transition-all border ${
              selectedZone === "B"
                ? "bg-[#051f20] text-[#daf1de] border-[#051f20] shadow-lg"
                : "glass-panel text-[#163832] border-[#8eb69b]/40 hover:border-[#235347]"
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-base font-black">Zone B</span>
              <span className={`w-2.5 h-2.5 rounded-full ${selectedZone === "B" ? "bg-[#8eb69b]" : "bg-[#235347]"}`} />
            </div>
            <p className="text-xs opacity-90 font-medium">🌿 Micro-Misting Greenhouse</p>
            <span className="text-[10px] font-mono mt-2 block opacity-75">Node: EDGE_02</span>
          </button>
        </div>

        {/* Zone Details & Thresholds */}
        <div className="glass-panel-glow rounded-3xl p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-[#8eb69b]/30 pb-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-[#daf1de] rounded-xl border border-[#8eb69b]/50 text-[#235347]">
                <MapPin className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-extrabold text-[#051f20]">
                  {selectedZone === "A" ? "Field A — Tomato Plot 1" : "Field B — High Tunnel Hydro"}
                </h3>
                <p className="text-xs text-[#163832] font-semibold">LoRa Channel {selectedZone === "A" ? "1" : "2"} • 433 MHz</p>
              </div>
            </div>
            <span className="px-3 py-1 rounded-full bg-[#daf1de] text-[#051f20] text-xs font-bold border border-[#8eb69b]/50">
              Active Control
            </span>
          </div>

          {/* Moisture Threshold Slider */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-[#163832] flex items-center gap-1.5">
                <Droplets className="w-4 h-4 text-[#235347]" /> Target Soil Hydration
              </span>
              <span className="text-lg font-black text-[#051f20]">
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
              className="w-full accent-[#235347] cursor-pointer"
            />
            <div className="flex justify-between text-[11px] text-[#163832] font-semibold">
              <span>Dry / Stressed (30%)</span>
              <span>Optimal Tomato (60-75%)</span>
              <span>Saturated (90%)</span>
            </div>
          </div>

          {/* Environmental Targets */}
          <div className="grid grid-cols-2 gap-3 pt-2">
            <div className="p-4 rounded-2xl bg-white border border-[#8eb69b]/35 space-y-1">
              <span className="text-[11px] text-[#163832] font-bold uppercase">Canopy Temp Target</span>
              <p className="text-xl font-black text-[#051f20]">22°C – 28°C</p>
              <p className="text-[10px] text-[#235347] font-semibold">Automatic ventilation link</p>
            </div>
            <div className="p-4 rounded-2xl bg-white border border-[#8eb69b]/35 space-y-1">
              <span className="text-[11px] text-[#163832] font-bold uppercase">Max Daily Fertigation</span>
              <p className="text-xl font-black text-[#051f20]">3 Cycles / Day</p>
              <p className="text-[10px] text-[#235347] font-semibold">Pulse drip scheduling</p>
            </div>
          </div>

          <button
            onClick={() => alert("Zone parameters saved and synced with edge station!")}
            className="w-full py-3.5 rounded-2xl bg-[#051f20] hover:bg-[#0b2b26] text-[#daf1de] font-bold text-sm shadow-xl flex items-center justify-center gap-2 transition cursor-pointer active:scale-98"
          >
            <CheckCircle2 className="w-4 h-4 text-[#8eb69b]" />
            <span>Save & Dispatch to Edge Station</span>
          </button>
        </div>
      </div>
    </main>
  );
}
