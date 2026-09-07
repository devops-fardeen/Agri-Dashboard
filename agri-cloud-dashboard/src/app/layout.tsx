import type { Metadata, Viewport } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: "AgriSmart Cloud Central — Smart Agriculture Ecosystem",
  description: "Next-gen precision farming dashboard with custom earth & slate warm palette.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  themeColor: "#f7f2ed",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="light" suppressHydrationWarning>
      <body
        className={`${jakarta.className} min-h-screen bg-[#f7f2ed] text-[#10232a] antialiased selection:bg-[#b58863] selection:text-white`}
        suppressHydrationWarning
      >
        {children}
      </body>
    </html>
  );
}