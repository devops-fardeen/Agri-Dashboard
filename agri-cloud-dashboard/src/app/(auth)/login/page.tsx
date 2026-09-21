"use client";

import React, { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { AuthCard } from "@/components/AuthCard";

function LoginContent() {
  const searchParams = useSearchParams();
  const initialMode = searchParams.get("mode") === "signup" ? "signup" : "signin";

  return <AuthCard initialMode={initialMode} />;
}

export default function LoginPage() {
  return (
    <main className="min-h-screen min-h-[100dvh] flex items-center justify-center p-3 sm:p-6 py-6 sm:py-10 relative overflow-y-auto overflow-x-hidden">
      {/* Ambient background glows with 7-color palette */}
      <div className="absolute -top-40 -left-40 w-96 h-96 bg-[#7BBDE8]/20 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-[#4E8EA2]/25 rounded-full blur-3xl pointer-events-none" />

      <Suspense
        fallback={
          <div className="w-full max-w-md p-8 modern-card rounded-[32px] text-center text-xs text-[#8A94A6] flex flex-col items-center gap-2">
            <div className="w-6 h-6 border-2 border-[#2563EB]/30 border-t-[#2563EB] rounded-full animate-spin" />
            Loading authentication...
          </div>
        }
      >
        <LoginContent />
      </Suspense>
    </main>
  );
}