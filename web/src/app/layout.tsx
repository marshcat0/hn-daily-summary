import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "每日技术摘要 | Daily Tech Summary",
  description:
    "AI-powered daily tech news digest from Hacker News, Reddit, and more",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html>
      <body className="font-sans">
        <div className="min-h-screen bg-white dark:bg-gray-900">{children}</div>
      </body>
    </html>
  );
}
