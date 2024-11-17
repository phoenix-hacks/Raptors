// app/layout.tsx
import type { Metadata } from "next";
import { Inter } from 'next/font/google';
import { twMerge } from "tailwind-merge";
import { AuthProvider } from '@/Context/AuthContext';
import { ThemeProvider } from '@/Context/ThemeContext';  // Import ThemeProvider
import "./globals.css";

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: "CarbonCare",
  description: "CarbonCare Logistics Agent - RAG Chatbot for Sustainable Logistics",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={twMerge(inter.className, "antialiased")}>
        <ThemeProvider>
          <AuthProvider>
            {children}
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
