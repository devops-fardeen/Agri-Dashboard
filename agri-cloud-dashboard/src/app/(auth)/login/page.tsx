import { GoogleSignInButton } from "@/components/GoogleSignInButton";

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0a0e14] px-4">
      <div className="max-w-md w-full p-6 bg-[#161b22] border border-[#30363d] rounded-xl space-y-4">
        <h1 className="text-xl font-bold text-white text-center">Sign In to AgriSmart</h1>
        
        {/* The Google Button */}
        <GoogleSignInButton />

        <div className="text-center text-xs text-gray-500">
          Or continue with email and password below
        </div>
      </div>
    </div>
  );
}