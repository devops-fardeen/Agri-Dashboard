"use client";

import { signIn } from "@/lib/auth-client";

export function GoogleSignInButton() {
  const handleGoogleSignIn = async () => {
    // 1. Tell Better Auth to start the Google OAuth flow
    // 2. Specify where to send the user once Google finishes logging them in
    await signIn.social({
      provider: "google",
      callbackURL: "/dashboard",
    });
  };

  return (
    <button
      type="button"
      onClick={handleGoogleSignIn}
      className="flex items-center justify-center gap-3 w-full py-2.5 px-4 rounded-lg bg-[#161b22] border border-[#30363d] text-white hover:bg-[#21262d] transition-colors"
    >
      {/* Official Google 'G' Icon */}
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
      <span className="font-medium text-sm">Continue with Google</span>
    </button>
  );
}