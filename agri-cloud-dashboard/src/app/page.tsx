import Link from "next/link";
import { 
  Sprout, 
  CheckCircle2, 
  Database, 
  ArrowRight, 
  Activity, 
  Radio, 
  ShieldCheck, 
  Layers
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";

export default function Home() {
  return (
    <div className="relative min-h-screen flex flex-col justify-between overflow-hidden bg-[#0a0e14] text-[#f0f6fc]">
      {/* Subtle Background Glows */}
      <div className="pointer-events-none absolute -top-40 left-1/2 -translate-x-1/2 h-[500px] w-[750px] rounded-full bg-emerald-500/10 blur-[130px]" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-[400px] w-[500px] rounded-full bg-cyan-500/5 blur-[120px]" />

      {/* Header */}
      <header className="relative z-10 w-full max-w-6xl mx-auto px-6 py-6 flex items-center justify-between border-b border-zinc-800/60">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
            <Sprout className="h-5 w-5" />
          </div>
          <div>
            <span className="font-bold tracking-tight text-white text-lg">AgriSmart</span>
            <span className="text-zinc-500 text-sm ml-1.5 font-medium">Cloud Central</span>
          </div>
        </div>
        <Badge variant="success" className="px-3.5 py-1 text-xs">
          <span className="relative flex h-2 w-2 mr-1">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          System Operational
        </Badge>
      </header>

      {/* Main Hero Content */}
      <main className="relative z-10 w-full max-w-5xl mx-auto px-6 py-16 flex flex-col items-center text-center">
        {/* Status Pill */}
        <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-4 py-1.5 text-xs font-semibold text-emerald-400 mb-8 backdrop-blur-md shadow-sm">
          <CheckCircle2 className="h-3.5 w-3.5" />
          <span>Bootstrap Ready (Chapter 1 Complete)</span>
        </div>

        {/* System Title */}
        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white max-w-3xl leading-[1.15]">
          AgriSmart <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">Cloud Central</span>
        </h1>

        <p className="mt-5 text-base sm:text-lg text-zinc-400 max-w-2xl font-normal leading-relaxed">
          High-performance distributed telemetry, edge-to-cloud synchronization, and automated precision agriculture dashboard system.
        </p>

        {/* Upcoming Chapter 2 Card / CTA */}
        <div className="w-full max-w-2xl mt-12">
          <Card className="border-emerald-500/20 bg-gradient-to-b from-[#121a24] to-[#0c1219] hover:border-emerald-500/40 transition-all duration-300 shadow-2xl">
            <CardHeader className="text-left pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-emerald-400">
                  <Database className="h-4 w-4" /> Next Milestone
                </div>
                <Badge variant="outline" className="text-[11px] text-zinc-400 border-zinc-700/60">
                  Upcoming
                </Badge>
              </div>
              <CardTitle className="text-xl sm:text-2xl text-white font-bold mt-2">
                Chapter 2: Database Connection &amp; Ingestion
              </CardTitle>
              <CardDescription className="text-zinc-400 mt-1">
                Configure MongoDB connection pooling, ingestion pipelines, and resilient telemetry schemas for smart sensor nodes.
              </CardDescription>
            </CardHeader>

            <CardContent className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-4 text-xs text-zinc-400 w-full sm:w-auto">
                <span className="flex items-center gap-1.5">
                  <Radio className="h-3.5 w-3.5 text-emerald-400" /> Sensor Sync
                </span>
                <span className="flex items-center gap-1.5">
                  <Activity className="h-3.5 w-3.5 text-cyan-400" /> Telemetry API
                </span>
                <span className="flex items-center gap-1.5">
                  <ShieldCheck className="h-3.5 w-3.5 text-indigo-400" /> Auth &amp; RBAC
                </span>
              </div>

              <Link href="/api/telemetry/sync" className="w-full sm:w-auto">
                <Button variant="default" size="md" className="w-full group">
                  <span>Prepare Ingestion</span>
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* Feature Stacks Preview */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-3xl mt-8 text-left">
          <div className="rounded-xl border border-zinc-800/80 bg-[#0d131c]/60 p-4 backdrop-blur-sm">
            <div className="flex items-center gap-2 text-emerald-400 text-sm font-semibold mb-1">
              <Layers className="h-4 w-4" /> App Architecture
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Route handlers, parallel dashboard segments, and modular UI structure bootstrapped.
            </p>
          </div>

          <div className="rounded-xl border border-zinc-800/80 bg-[#0d131c]/60 p-4 backdrop-blur-sm">
            <div className="flex items-center gap-2 text-cyan-400 text-sm font-semibold mb-1">
              <Database className="h-4 w-4" /> Persistence Layer
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Targeted for MongoDB Mongoose/native driver driver configuration in Chapter 2.
            </p>
          </div>

          <div className="rounded-xl border border-zinc-800/80 bg-[#0d131c]/60 p-4 backdrop-blur-sm">
            <div className="flex items-center gap-2 text-indigo-400 text-sm font-semibold mb-1">
              <Activity className="h-4 w-4" /> Real-time Metrics
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Zone telemetry streams and device heartbeat tracking ready for hookup.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 w-full max-w-6xl mx-auto px-6 py-6 border-t border-zinc-800/60 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-zinc-500">
        <p>&copy; {new Date().getFullYear()} AgriSmart Cloud Systems. All rights reserved.</p>
        <div className="flex items-center gap-4 text-zinc-400">
          <span>Next.js App Router</span>
          <span>&bull;</span>
          <span>TypeScript</span>
          <span>&bull;</span>
          <span>Tailwind CSS</span>
        </div>
      </footer>
    </div>
  );
}
