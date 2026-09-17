import type { Metadata, Viewport } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  variable: "--font-jakarta",
});

export const metadata: Metadata = {
  title: "AgriSmart Cloud Central — Smart Agriculture Ecosystem",
  description: "Next-gen precision farming dashboard with teal & mint modern bento design.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  themeColor: "#EEF1F5",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`light ${jakarta.variable}`} suppressHydrationWarning>
      <body
        className={`${jakarta.className} min-h-screen bg-[#EEF1F5] text-[#121417] antialiased selection:bg-[#121417] selection:text-white`}
        suppressHydrationWarning
      >
        {children}
      </body>
    </html>
  );
}