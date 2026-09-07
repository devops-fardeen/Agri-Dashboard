"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { signIn, signUp, useSession } from "@/lib/auth-client";
import {
  Sprout,
  ShieldCheck,
  ArrowRight,
  Lock,
  Mail,
  User,
  AlertCircle,
  CheckCircle2,
  Eye,
  EyeOff,
  Sparkles,
  Zap,
} from "lucide-react";

function AuthCard() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialMode = searchParams.get("mode") === "signup" ? "signup" : "signin";

  const { data: session, isPending } = useSession();

  const [mode, setMode] = useState<"signin" | "signup">(initialMode);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [demoLoading, setDemoLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // If already logged in, forward to dashboard
  useEffect(() => {
    if (!isPending && session) {
      router.push("/");
    }
  }, [session, isPending, router]);

  // Google OAuth Login
  const handleGoogleSignIn = async () => {
    setErrorMsg(null);
    setGoogleLoading(true);
    try {
      await signIn.social({
        provider: "google",
        callbackURL: "/",
      });
    } catch (err: any) {
      console.error("Google sign in error:", err);
      setErrorMsg(err?.message || "Failed to initialize Google authentication. Please try email login.");
      setGoogleLoading(false);
    }
  };

  // Email/Password Submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setSuccessMsg(null);

    if (!email.trim() || !password) {
      setErrorMsg("Please enter both email and password.");
      return;
    }

    if (mode === "signup") {
      if (!name.trim()) {
        setErrorMsg("Please provide your full name.");
        return;
      }
      if (password.length < 6) {
        setErrorMsg("Password must be at least 6 characters long.");
        return;
      }
      if (password !== confirmPassword) {
        setErrorMsg("Passwords do not match. Please recheck.");
        return;
      }

      setLoading(true);
      try {
        await signUp.email(
          {
            email: email.trim().toLowerCase(),
            password: password,
            name: name.trim(),
            callbackURL: "/",
          },
          {
            onRequest: () => setLoading(true),
            onSuccess: () => {
              setSuccessMsg("Account created! Redirecting to dashboard...");
              setTimeout(() => router.push("/"), 800);
            },
            onError: (ctx) => {
              setLoading(false);
              setErrorMsg(ctx.error.message || "Failed to create account. Email may already be in use.");
            },
          }
        );
      } catch (err: any) {
        setLoading(false);
        setErrorMsg(err?.message || "Account creation failed.");
      }
    } else {
      // Sign In
      setLoading(true);
      try {
        await signIn.email(
          {
            email: email.trim().toLowerCase(),
            password: password,
            callbackURL: "/",
          },
          {
            onRequest: () => setLoading(true),
            onSuccess: () => {
              setSuccessMsg("Signed in successfully! Redirecting...");
              setTimeout(() => router.push("/"), 600);
            },
            onError: (ctx) => {
              setLoading(false);
              setErrorMsg(ctx.error.message || "Invalid email or password. Please verify credentials.");
            },
          }
        );
      } catch (err: any) {
        setLoading(false);
        setErrorMsg(err?.message || "Sign in failed.");
      }
    }
  };

  // Demo Fast-Pass Login (Instant Access)
  const handleDemoLogin = async () => {
    setErrorMsg(null);
    setDemoLoading(true);
    const demoEmail = "demo.operator@agrismart.io";
    const demoPass = "Farmer@2026!";

    try {
      // Try signing in first
      await signIn.email(
        {
          email: demoEmail,
          password: demoPass,
          callbackURL: "/",
        },
        {
          onSuccess: () => {
            setSuccessMsg("Demo operator session loaded! Redirecting...");
            setTimeout(() => router.push("/"), 500);
          },
          onError: async () => {
            // If demo doesn't exist yet, auto register it
            await signUp.email(
              {
                email: demoEmail,
                password: demoPass,
                name: "Demo Farm Operator",
                callbackURL: "/",
              },
              {
                onSuccess: () => {
                  setSuccessMsg("Demo account initialized! Redirecting...");
                  setTimeout(() => router.push("/"), 500);
                },
                onError: (ctx) => {
                  setDemoLoading(false);
                  setErrorMsg("Demo login error: " + ctx.error.message);
                },
              }
            );
          },
        }
      );
    } catch (err: any) {
      setDemoLoading(false);
      setErrorMsg(err?.message || "Demo login failed.");
    }
  };

  return (
    <div className="w-full max-w-md glass-panel-glow rounded-[32px] p-6 sm:p-8 space-y-5 shadow-2xl relative overflow-hidden border border-[#8eb69b]/40">
      {/* Ambient background glow */}
      <div className="absolute -top-20 left-1/2 -translate-x-1/2 w-64 h-64 bg-[#8eb69b]/25 rounded-full blur-3xl pointer-events-none" />

      {/* Header & Logo */}
      <div className="text-center relative z-10 space-y-2">
        <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-tr from-[#051f20] to-[#235347] p-0.5 shadow-md">
          <div className="w-full h-full rounded-2xl bg-white flex items-center justify-center text-[#235347]">
            <Sprout className="w-7 h-7" />
          </div>
        </div>
        <div>
          <h1 className="text-2xl font-black text-[#051f20] tracking-tight">
            {mode === "signin" ? "Sign In to AgriSmart" : "Create Farm Account"}
          </h1>
          <p className="text-xs font-semibold text-[#163832] tracking-wide uppercase mt-0.5">
            Autonomous Greenhouse & Field Cloud
          </p>
        </div>
      </div>

      {/* Mode Switcher Tabs (Sign In / Sign Up) */}
      <div className="relative z-10 grid grid-cols-2 p-1 rounded-2xl bg-[#daf1de]/60 border border-[#8eb69b]/40">
        <button
          type="button"
          onClick={() => {
            setMode("signin");
            setErrorMsg(null);
            setSuccessMsg(null);
          }}
          className={`py-2 px-3 rounded-xl text-xs font-bold transition-all ${
            mode === "signin"
              ? "bg-[#051f20] text-[#daf1de] shadow-md"
              : "text-[#163832] hover:text-[#051f20]"
          }`}
        >
          Sign In
        </button>
        <button
          type="button"
          onClick={() => {
            setMode("signup");
            setErrorMsg(null);
            setSuccessMsg(null);
          }}
          className={`py-2 px-3 rounded-xl text-xs font-bold transition-all ${
            mode === "signup"
              ? "bg-[#051f20] text-[#daf1de] shadow-md"
              : "text-[#163832] hover:text-[#051f20]"
          }`}
        >
          Create Account
        </button>
      </div>

      {/* Status Alerts */}
      {errorMsg && (
        <div className="relative z-10 p-3 rounded-2xl bg-[#fff1f2] border border-[#be123c]/30 text-[#be123c] text-xs font-semibold flex items-start gap-2.5 animate-shake">
          <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {successMsg && (
        <div className="relative z-10 p-3 rounded-2xl bg-[#f0fdf4] border border-[#235347]/30 text-[#235347] text-xs font-semibold flex items-start gap-2.5">
          <CheckCircle2 className="w-4 h-4 mt-0.5 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* PRIMARY GOOGLE BUTTON */}
      <div className="relative z-10">
        <button
          type="button"
          onClick={handleGoogleSignIn}
          disabled={googleLoading || loading || demoLoading}
          className="w-full flex items-center justify-center gap-3 py-3 px-4 rounded-2xl bg-white hover:bg-[#daf1de]/40 border border-[#8eb69b]/50 text-[#051f20] font-bold text-xs shadow-sm hover:shadow transition-all active:scale-[0.98] disabled:opacity-60 cursor-pointer"
        >
          {googleLoading ? (
            <div className="w-4 h-4 border-2 border-[#8eb69b]/30 border-t-[#235347] rounded-full animate-spin" />
          ) : (
            <svg className="w-4 h-4" viewBox="0 0 24 24">
              <path
                fill="#EA4335"
                d="M12 5c1.6 0 3 .6 4.1 1.6l3.1-3.1C17.3 1.7 14.8 1 12 1 7.5 1 3.7 3.6 1.9 7.3l3.7 2.9C6.5 7.4 9 5 12 5z"
              />
              <path
                fill="#4285F4"
                d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.6h6.5c-.3 1.5-1.1 2.8-2.4 3.7l3.7 2.9c2.2-2 3.7-5 3.7-8.9z"
              />
              <path
                fill="#FBBC05"
                d="M5.6 14.8c-.2-.7-.4-1.5-.4-2.3s.1-1.6.4-2.3L1.9 7.3C.7 9.7 0 12 0 14.5s.7 4.8 1.9 7.2l3.7-2.9z"
              />
              <path
                fill="#34A853"
                d="M12 23.5c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3 0-5.5-2-6.4-4.8L1.9 17c1.8 3.7 5.6 6.5 10.1 6.5z"
              />
            </svg>
          )}
          <span>{mode === "signin" ? "Continue with Google" : "Sign Up with Google"}</span>
        </button>
      </div>

      {/* DIVIDER */}
      <div className="relative flex items-center justify-center">
        <div className="border-t border-[#8eb69b]/30 w-full" />
        <span className="bg-[#f0f7f2] px-3 text-[10px] font-extrabold text-[#163832] uppercase tracking-wider absolute">
          Or with credentials
        </span>
      </div>

      {/* FORM */}
      <form onSubmit={handleSubmit} className="relative z-10 space-y-3.5">
        {mode === "signup" && (
          <div>
            <label className="block text-[11px] font-bold text-[#163832] uppercase tracking-wider mb-1">
              Full Name
            </label>
            <div className="relative">
              <User className="w-4 h-4 text-[#163832]/60 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Fardeen Patel"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white/80 border border-[#8eb69b]/40 text-[#051f20] placeholder-[#163832]/40 focus:outline-none focus:border-[#235347] focus:ring-2 focus:ring-[#235347]/20 text-xs font-medium transition-all"
              />
            </div>
          </div>
        )}

        <div>
          <label className="block text-[11px] font-bold text-[#163832] uppercase tracking-wider mb-1">
            Email Address
          </label>
          <div className="relative">
            <Mail className="w-4 h-4 text-[#163832]/60 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="farmer@agrismart.io"
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white/80 border border-[#8eb69b]/40 text-[#051f20] placeholder-[#163832]/40 focus:outline-none focus:border-[#235347] focus:ring-2 focus:ring-[#235347]/20 text-xs font-medium transition-all"
            />
          </div>
        </div>

        <div>
          <label className="block text-[11px] font-bold text-[#163832] uppercase tracking-wider mb-1">
            Password
          </label>
          <div className="relative">
            <Lock className="w-4 h-4 text-[#163832]/60 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type={showPassword ? "text" : "password"}
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              className="w-full pl-10 pr-10 py-2.5 rounded-xl bg-white/80 border border-[#8eb69b]/40 text-[#051f20] placeholder-[#163832]/40 focus:outline-none focus:border-[#235347] focus:ring-2 focus:ring-[#235347]/20 text-xs font-medium transition-all"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[#163832]/60 hover:text-[#051f20]"
            >
              {showPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
            </button>
          </div>
        </div>

        {mode === "signup" && (
          <div>
            <label className="block text-[11px] font-bold text-[#163832] uppercase tracking-wider mb-1">
              Confirm Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-[#163832]/60 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type={showPassword ? "text" : "password"}
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white/80 border border-[#8eb69b]/40 text-[#051f20] placeholder-[#163832]/40 focus:outline-none focus:border-[#235347] focus:ring-2 focus:ring-[#235347]/20 text-xs font-medium transition-all"
              />
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={loading || googleLoading || demoLoading}
          className="w-full py-3 px-4 rounded-2xl bg-[#051f20] hover:bg-[#0b2b26] text-[#daf1de] font-bold text-xs shadow-lg flex items-center justify-center gap-2 transition-all cursor-pointer active:scale-[0.98] disabled:opacity-60"
        >
          {loading ? (
            <div className="w-4 h-4 border-2 border-[#8eb69b]/30 border-t-[#daf1de] rounded-full animate-spin" />
          ) : (
            <>
              <span>{mode === "signin" ? "Sign In to Dashboard" : "Register Farm Account"}</span>
              <ArrowRight className="w-3.5 h-3.5 text-[#8eb69b]" />
            </>
          )}
        </button>
      </form>

      {/* QUICK DEMO LOGIN BUTTON */}
      <div className="relative z-10 pt-1">
        <button
          type="button"
          onClick={handleDemoLogin}
          disabled={loading || googleLoading || demoLoading}
          className="w-full py-2.5 px-3 rounded-xl bg-[#daf1de]/70 hover:bg-[#daf1de] border border-[#8eb69b]/50 text-[#051f20] text-[11px] font-bold flex items-center justify-center gap-1.5 transition active:scale-95 cursor-pointer shadow-sm"
        >
          {demoLoading ? (
            <div className="w-3.5 h-3.5 border-2 border-[#051f20]/30 border-t-[#051f20] rounded-full animate-spin" />
          ) : (
            <Zap className="w-3.5 h-3.5 text-[#235347]" />
          )}
          <span>⚡ Instant Demo Access (One-Click Login)</span>
        </button>
      </div>

      {/* FOOTER SWITCHER & SECURITY BADGE */}
      <div className="relative z-10 pt-1 space-y-3 text-center">
        <p className="text-xs font-semibold text-[#163832]">
          {mode === "signin" ? (
            <>
              Need an operator account?{" "}
              <button
                type="button"
                onClick={() => {
                  setMode("signup");
                  setErrorMsg(null);
                  setSuccessMsg(null);
                }}
                className="text-[#235347] hover:underline font-extrabold cursor-pointer"
              >
                Create Account
              </button>
            </>
          ) : (
            <>
              Already registered?{" "}
              <button
                type="button"
                onClick={() => {
                  setMode("signin");
                  setErrorMsg(null);
                  setSuccessMsg(null);
                }}
                className="text-[#235347] hover:underline font-extrabold cursor-pointer"
              >
                Sign In Here
              </button>
            </>
          )}
        </p>

        <div className="pt-2 border-t border-[#8eb69b]/25 flex items-center justify-center gap-1.5 text-[10px] text-[#163832] font-semibold">
          <ShieldCheck className="w-3.5 h-3.5 text-[#235347]" />
          <span>AES-256 Cloud Telemetry Link Secured</span>
        </div>
      </div>
    </div>
  );
}

export default function UnifiedAuthPage() {
  return (
    <main className="min-h-screen flex items-center justify-center p-4 bg-[#f0f7f2] relative overflow-hidden">
      <Suspense
        fallback={
          <div className="w-full max-w-md p-8 glass-panel-glow rounded-[32px] text-center text-xs text-[#163832] flex flex-col items-center gap-2">
            <div className="w-6 h-6 border-2 border-[#8eb69b]/30 border-t-[#235347] rounded-full animate-spin" />
            Loading authentication...
          </div>
        }
      >
        <AuthCard />
      </Suspense>
    </main>
  );
}