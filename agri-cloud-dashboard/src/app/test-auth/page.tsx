"use client";

import { signIn, signOut, useSession } from "@/lib/auth-client";

export default function TestAuthPage() {
  const { data: session, isPending } = useSession();

  const handleGoogleLogin = async () => {
    await signIn.social({
      provider: "google",
      callbackURL: "/test-auth",
    });
  };

  return (
    <main className="min-h-screen flex items-center justify-center p-4 bg-[#0a0e14]">
      <div className="w-full max-w-md p-6 bg-[#161b22] border border-[#30363d] rounded-xl shadow-xl space-y-6">
        <div className="text-center">
          <h1 className="text-xl font-bold text-white">Google Auth Verification</h1>
          <p className="text-xs text-gray-400 mt-1">SIH 2026 Smart Farming Central</p>
        </div>

        {isPending ? (
          <div className="text-center text-sm text-gray-400 py-6">
            Loading session status...
          </div>
        ) : session ? (
          <div className="space-y-4">
            <div className="p-4 bg-[#0d1117] border border-green-800/50 rounded-lg space-y-2">
              <div className="flex items-center gap-2 text-green-400 text-sm font-semibold">
                <span>●</span> Authenticated Successfully
              </div>
              <div className="text-xs text-gray-300 space-y-1 pt-1">
                <p><span className="text-gray-500">Name:</span> {session.user?.name}</p>
                <p><span className="text-gray-500">Email:</span> {session.user?.email}</p>
              </div>
            </div>

            <button
              onClick={() => signOut()}
              className="w-full py-2.5 px-4 bg-red-600/20 border border-red-600 text-red-400 hover:bg-red-600 hover:text-white rounded-lg text-sm font-medium transition"
            >
              Sign Out
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-sm text-gray-400 text-center">
              Click below to initiate the Google OAuth handoff.
            </p>

            <button
              type="button"
              onClick={handleGoogleLogin}
              className="w-full flex items-center justify-center gap-3 py-2.5 px-4 rounded-lg bg-white text-gray-900 font-medium text-sm hover:bg-gray-100 transition shadow"
            >
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
              Sign in with Google
            </button>
          </div>
        )}
      </div>
    </main>
  );
}