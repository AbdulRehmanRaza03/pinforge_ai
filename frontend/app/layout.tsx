import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "react-hot-toast";

export const metadata: Metadata = {
  title: "PinForge AI — Pinterest Automation That Feels Human",
  description: "Schedule, automate, and optimize your Pinterest pins with AI. Safe, official API only.",
  icons: { icon: "/favicon.ico" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="font-body antialiased">
        {children}
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: "#0d0d1f",
              color: "#f8fafc",
              border: "1px solid rgba(147,51,234,0.3)",
              borderRadius: "12px",
              fontFamily: "'DM Sans', sans-serif",
            },
            success: { iconTheme: { primary: "#10b981", secondary: "#070712" } },
            error: { iconTheme: { primary: "#ef4444", secondary: "#070712" } },
          }}
        />
      </body>
    </html>
  );
}
