"use client";

import { useEffect, useState } from "react";
import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import {
  Droplets,
  Thermometer,
  CloudSun,
  AlertTriangle,
  Radio,
  LogOut,
  RefreshCw,
  Wind,
  Power,
  Navigation,
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  Square,
  BatteryCharging,
  Wifi,
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

interface WeatherData {
  temperature: number;
  humidity: number;
  windSpeed: number;
  condition: string;
  time: string;
  floodRisk: boolean;
  alertMessage?: string;
}

export default function DashboardPage() {
  const { data: session, isPending } = authClient.useSession();
  const router = useRouter();

  const [activeZone, setActiveZone] = useState<"ZONE_A" | "ZONE_B">("ZONE_A");
  const [telemetry, setTelemetry] = useState<{ latest: any; history: any[] }>({
    latest: null,
    history: [],
  });
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);

  // Pump States
  const [pumpZoneA, setPumpZoneA] = useState(false);
  const [pumpZoneB, setPumpZoneB] = useState(false);
  const [pumpLoading, setPumpLoading] = useState(false);

  // Rover Control State
  const [roverAction, setRoverAction] = useState<string>("STOP");
  const [roverSending, setRoverSending] = useState(false);

  // Weather Fetcher (Open-Meteo)
  const fetchWeather = async (): Promise<WeatherData> => {
    try {
      const res = await fetch(
        "https://api.open-meteo.com/v1/forecast?latitude=26.8467&longitude=80.9462&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation&daily=precipitation_sum&timezone=auto"
      );
      if (!res.ok) throw new Error("Weather fetch failed");
      const data = await res.json();
      const precipitation = data.current?.precipitation || 0;
      const dailyRain = data.daily?.precipitation_sum?.[0] || 0;
      const floodRisk = dailyRain > 45 || precipitation > 15;

      return {
        temperature: data.current?.temperature_2m ?? 28,
        humidity: data.current?.relative_humidity_2m ?? 65,
        windSpeed: data.current?.wind_speed_10m ?? 8,
        condition: floodRisk ? "Severe Flood Risk" : "Stable",
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        floodRisk,
        alertMessage: floodRisk
          ? "CRITICAL ALERT: Heavy precipitation detected. Flood/waterlogging risks active."
          : undefined,
      };
    } catch {
      return {
        temperature: 28.5,
        humidity: 62,
        windSpeed: 7,
        condition: "Normal",
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        floodRisk: false,
      };
    }
  };

  // Main Dashboard Data Loader
  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [telRes, zaRes, zbRes, weatherRes] = await Promise.all([
        fetch(`/api/telemetry?zoneId=${activeZone}&limit=30`)
          .then((r) => (r.ok ? r.json() : null))
          .catch(() => null),
        fetch(`/api/telemetry?zoneId=ZONE_A&limit=1`)
          .then((r) => (r.ok ? r.json() : null))
          .catch(() => null),
        fetch(`/api/telemetry?zoneId=ZONE_B&limit=1`)
          .then((r) => (r.ok ? r.json() : null))
          .catch(() => null),
        fetchWeather(),
      ]);

      if (telRes?.success && Array.isArray(telRes.data)) {
        const records = telRes.data;
        const latestRecord = records.length > 0 ? records[0] : null;
        setTelemetry({ latest: latestRecord, history: [...records].reverse() });
      } else if (telRes?.success && Array.isArray(telRes.history)) {
        setTelemetry({ latest: telRes.latest ?? null, history: telRes.history });
      } else {
        setTelemetry({ latest: null, history: [] });
      }

      // Synchronize pump actuator states from Cloud DB
      if (zaRes?.latest?.actuatorState) {
        setPumpZoneA(Boolean(zaRes.latest.actuatorState.pumpActive));
      }
      if (zbRes?.latest?.actuatorState) {
        setPumpZoneB(Boolean(zbRes.latest.actuatorState.pumpActive));
      }

      if (weatherRes) {
        setWeather(weatherRes);
      }
    } catch (err) {
      console.error("Dashboard refresh error:", err);
    } finally {
      setLoading(false);
    }
  };

  // Hardware Command Dispatcher
  const sendCommand = async (target: "PUMP_ZONE_A" | "PUMP_ZONE_B" | "ROVER", action: string) => {
    try {
      if (target.startsWith("PUMP")) setPumpLoading(true);
      if (target === "ROVER") {
        setRoverSending(true);
        setRoverAction(action);
      }

      // Optimistic update
      if (target === "PUMP_ZONE_A") setPumpZoneA(action === "ON");
      if (target === "PUMP_ZONE_B") setPumpZoneB(action === "ON");

      await fetch("/api/commands", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target, action }),
      });
    } catch (err) {
      console.error("Command failed:", err);
    } finally {
      setPumpLoading(false);
      setRoverSending(false);
    }
  };

  // Auth Protection
  useEffect(() => {
    if (!isPending && !session) {
      router.push("/test-auth");
    }
  }, [session, isPending, router]);

  // Polling Interval
  useEffect(() => {
    if (session) {
      loadDashboardData();
      const interval = setInterval(loadDashboardData, 15000);
      return () => clearInterval(interval);
    }
  }, [session, activeZone]);

  if (isPending || !session) {
    return (
      <div className="min-h-screen bg-[#0a0e14] flex items-center justify-center text-gray-400">
        Verifying AgriSmart cloud session...
      </div>
    );
  }

  const latest = telemetry?.latest?.telemetry;
  const historyList = Array.isArray(telemetry?.history) ? telemetry.history : [];
  const chartData = historyList.map((d: any) => ({
    time: d.recordedAt ? new Date(d.recordedAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "--",
    moisture: d.telemetry?.soilMoisture ?? 0,
    temp: d.telemetry?.soilTemperature ?? 0,
    humidity: d.telemetry?.ambientHumidity ?? 0,
  }));

  return (
    <div className="min-h-screen bg-[#0a0e14] text-white flex flex-col">
      {/* 1. Disaster / Flood Alert Banner */}
      {weather?.floodRisk && (
        <aside aria-label="Disaster Alert" className="bg-rose-600 px-4 py-2.5 flex items-center justify-center gap-2 text-white font-semibold text-xs shadow-md">
          <AlertTriangle className="w-4 h-4 animate-bounce" />
          <span>{weather.alertMessage}</span>
        </aside>
      )}

      {/* 2. Top Header Bar */}
      <header className="h-16 border-b border-[#21262d] px-6 flex items-center justify-between bg-[#0d1117]">
        <div className="flex items-center gap-3">
          <Radio className="w-5 h-5 text-emerald-400 animate-pulse" />
          <h1 className="font-semibold text-sm tracking-wide">AgriSmart Cloud Central (Tier 3)</h1>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-xs font-medium text-white">{session.user?.name}</p>
            <p className="text-[10px] text-gray-400">{session.user?.email}</p>
          </div>
          <button
            onClick={() =>
              authClient.signOut({
                fetchOptions: { onSuccess: () => router.push("/test-auth") },
              })
            }
            className="p-2 rounded-lg bg-[#161b22] border border-[#30363d] hover:bg-rose-950/40 text-gray-300 hover:text-rose-400 transition"
            title="Sign Out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* 3. Main Dashboard Body */}
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full space-y-6">
        {/* Farm Weather Strip */}
        <section className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-[#161b22] border border-[#30363d] flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-400">Local Time</p>
              <p className="text-lg font-bold text-white mt-1">{weather?.time || "--:--"}</p>
            </div>
            <CloudSun className="w-7 h-7 text-amber-400" />
          </div>

          <div className="p-4 rounded-xl bg-[#161b22] border border-[#30363d] flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-400">Atmosphere Temp</p>
              <p className="text-lg font-bold text-white mt-1">{weather?.temperature}°C</p>
            </div>
            <Thermometer className="w-7 h-7 text-blue-400" />
          </div>

          <div className="p-4 rounded-xl bg-[#161b22] border border-[#30363d] flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-400">Air Humidity</p>
              <p className="text-lg font-bold text-white mt-1">{weather?.humidity}%</p>
            </div>
            <Droplets className="w-7 h-7 text-emerald-400" />
          </div>

          <div className="p-4 rounded-xl bg-[#161b22] border border-[#30363d] flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-400">Wind Velocity</p>
              <p className="text-lg font-bold text-white mt-1">{weather?.windSpeed} km/h</p>
            </div>
            <Wind className="w-7 h-7 text-cyan-400" />
          </div>
        </section>

        {/* Dual Pump Actuators */}
        <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-[#161b22] border border-[#30363d] rounded-xl flex items-center justify-between">
            <div>
              <h4 className="text-sm font-semibold text-white">Zone A Pump (Crops)</h4>
              <p className="text-xs text-gray-400">
                State:{" "}
                <span className={pumpZoneA ? "text-emerald-400 font-bold" : "text-gray-400"}>
                  {pumpZoneA ? "ACTIVE / PUMPING" : "OFF / IDLE"}
                </span>
              </p>
            </div>
            <button
              onClick={() => sendCommand("PUMP_ZONE_A", pumpZoneA ? "OFF" : "ON")}
              disabled={pumpLoading}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
                pumpZoneA
                  ? "bg-rose-600 hover:bg-rose-700 text-white"
                  : "bg-emerald-600 hover:bg-emerald-700 text-white"
              }`}
            >
              <Power className="w-3.5 h-3.5" />
              {pumpZoneA ? "Turn OFF" : "Turn ON"}
            </button>
          </div>

          <div className="p-4 bg-[#161b22] border border-[#30363d] rounded-xl flex items-center justify-between">
            <div>
              <h4 className="text-sm font-semibold text-white">Zone B Pump (Orchard)</h4>
              <p className="text-xs text-gray-400">
                State:{" "}
                <span className={pumpZoneB ? "text-emerald-400 font-bold" : "text-gray-400"}>
                  {pumpZoneB ? "ACTIVE / PUMPING" : "OFF / IDLE"}
                </span>
              </p>
            </div>
            <button
              onClick={() => sendCommand("PUMP_ZONE_B", pumpZoneB ? "OFF" : "ON")}
              disabled={pumpLoading}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
                pumpZoneB
                  ? "bg-rose-600 hover:bg-rose-700 text-white"
                  : "bg-emerald-600 hover:bg-emerald-700 text-white"
              }`}
            >
              <Power className="w-3.5 h-3.5" />
              {pumpZoneB ? "Turn OFF" : "Turn ON"}
            </button>
          </div>
        </section>

        {/* Zone Selector & Live Sync Trigger */}
        <div className="flex items-center justify-between">
          <div className="flex bg-[#161b22] border border-[#30363d] p-1 rounded-lg">
            <button
              onClick={() => setActiveZone("ZONE_A")}
              className={`px-4 py-1.5 rounded-md text-xs font-semibold transition ${
                activeZone === "ZONE_A"
                  ? "bg-emerald-500 text-black shadow"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              Zone A (Crops)
            </button>
            <button
              onClick={() => setActiveZone("ZONE_B")}
              className={`px-4 py-1.5 rounded-md text-xs font-semibold transition ${
                activeZone === "ZONE_B"
                  ? "bg-emerald-500 text-black shadow"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              Zone B (Orchard)
            </button>
          </div>

          <button
            onClick={loadDashboardData}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-1.5 text-xs bg-[#161b22] border border-[#30363d] rounded-lg hover:text-white"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            Sync Now
          </button>
        </div>

        {/* Live Sensor Metrics */}
        <section className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="p-5 rounded-xl bg-[#161b22] border border-[#30363d]">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-gray-400 uppercase">Soil Moisture</span>
              <div className="p-2 rounded-lg bg-[#0d1117] text-emerald-400">
                <Droplets className="w-5 h-5" />
              </div>
            </div>
            <div className="mt-3 flex items-baseline gap-2">
              <span className="text-3xl font-bold text-white tracking-tight">
                {latest ? latest.soilMoisture : "--"}
              </span>
              <span className="text-sm font-medium text-gray-400">%</span>
            </div>
            <p className="mt-2 text-xs text-gray-400">Target Range: 60% – 75%</p>
          </div>

          <div className="p-5 rounded-xl bg-[#161b22] border border-[#30363d]">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-gray-400 uppercase">Soil Temperature</span>
              <div className="p-2 rounded-lg bg-[#0d1117] text-blue-400">
                <Thermometer className="w-5 h-5" />
              </div>
            </div>
            <div className="mt-3 flex items-baseline gap-2">
              <span className="text-3xl font-bold text-white tracking-tight">
                {latest ? latest.soilTemperature : "--"}
              </span>
              <span className="text-sm font-medium text-gray-400">°C</span>
            </div>
            <p className="mt-2 text-xs text-gray-400">Root-level temperature probe</p>
          </div>

          <div className="p-5 rounded-xl bg-[#161b22] border border-[#30363d]">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-gray-400 uppercase">Ambient Canopy Temp</span>
              <div className="p-2 rounded-lg bg-[#0d1117] text-amber-400">
                <CloudSun className="w-5 h-5" />
              </div>
            </div>
            <div className="mt-3 flex items-baseline gap-2">
              <span className="text-3xl font-bold text-white tracking-tight">
                {latest ? latest.ambientTemp : "--"}
              </span>
              <span className="text-sm font-medium text-gray-400">°C</span>
            </div>
            <p className="mt-2 text-xs text-gray-400">Air canopy sensor telemetry</p>
          </div>
        </section>

        {/* Previous Data Trend Graph + Rover Controller */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 p-5 rounded-xl bg-[#161b22] border border-[#30363d]">
            <h3 className="text-sm font-semibold text-white mb-1">
              Historical Telemetry Trends ({activeZone})
            </h3>
            <p className="text-xs text-gray-400 mb-4">
              Real-time time-series buffer synced from Edge Gateway
            </p>

            <div className="h-72 w-full">
              {chartData.length === 0 ? (
                <div className="h-full flex items-center justify-center text-sm text-gray-500">
                  No historical records for {activeZone} yet.
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="moistGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                      </linearGradient>
                      <linearGradient id="tempGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                    <XAxis dataKey="time" stroke="#6e7681" tick={{ fontSize: 11 }} />
                    <YAxis stroke="#6e7681" tick={{ fontSize: 11 }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#0d1117",
                        borderColor: "#30363d",
                        borderRadius: "8px",
                        fontSize: "12px",
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="moisture"
                      name="Moisture (%)"
                      stroke="#10b981"
                      strokeWidth={2}
                      fillOpacity={1}
                      fill="url(#moistGrad)"
                    />
                    <Area
                      type="monotone"
                      dataKey="temp"
                      name="Soil Temp (°C)"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      fillOpacity={1}
                      fill="url(#tempGrad)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          {/* Rover Control & Telemetry Panel */}
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
                  <Wifi className="w-4 h-4" /> Linked
                </span>
              </div>
            </div>

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
                <p className="text-gray-400">Command</p>
                <p className="text-emerald-400 font-bold mt-0.5">{roverAction}</p>
              </div>
            </div>

            {/* Manual Rover Directional D-Pad */}
            <div className="pt-2 flex flex-col items-center justify-center space-y-2">
              <button
                type="button"
                onClick={() => sendCommand("ROVER", "MOVE_FORWARD")}
                disabled={roverSending}
                className="p-3 bg-[#21262d] hover:bg-emerald-600 active:scale-95 rounded-lg border border-[#30363d] transition"
                title="Forward"
              >
                <ArrowUp className="w-5 h-5 text-white" />
              </button>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => sendCommand("ROVER", "MOVE_LEFT")}
                  disabled={roverSending}
                  className="p-3 bg-[#21262d] hover:bg-emerald-600 active:scale-95 rounded-lg border border-[#30363d] transition"
                  title="Turn Left"
                >
                  <ArrowLeft className="w-5 h-5 text-white" />
                </button>
                <button
                  type="button"
                  onClick={() => sendCommand("ROVER", "STOP")}
                  disabled={roverSending}
                  className="p-3 bg-rose-600/30 hover:bg-rose-600 active:scale-95 rounded-lg border border-rose-500 text-rose-300 transition"
                  title="Emergency Stop"
                >
                  <Square className="w-5 h-5" />
                </button>
                <button
                  type="button"
                  onClick={() => sendCommand("ROVER", "MOVE_RIGHT")}
                  disabled={roverSending}
                  className="p-3 bg-[#21262d] hover:bg-emerald-600 active:scale-95 rounded-lg border border-[#30363d] transition"
                  title="Turn Right"
                >
                  <ArrowRight className="w-5 h-5 text-white" />
                </button>
              </div>
              <button
                type="button"
                onClick={() => sendCommand("ROVER", "MOVE_BACKWARD")}
                disabled={roverSending}
                className="p-3 bg-[#21262d] hover:bg-emerald-600 active:scale-95 rounded-lg border border-[#30363d] transition"
                title="Backward"
              >
                <ArrowDown className="w-5 h-5 text-white" />
              </button>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}