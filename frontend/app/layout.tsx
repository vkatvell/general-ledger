import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner"
import { Navbar } from "@/components/Navbar"

export const metadata: Metadata = {
  title: "General Ledger UI",
  description: "Basic UI for general ledger backend project",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        {children}
        <Toaster richColors/>
      </body>
    </html>
  );
}
