import type { Metadata } from "next";
import { Source_Sans_3, Source_Serif_4 } from "next/font/google";

import "./globals.css";
import { Providers } from "@/app/providers";

// Cặp font mã nguồn mở, có bộ chữ tiếng Việt (tham khảo Stanford Decanter).
const sans = Source_Sans_3({ subsets: ["latin", "vietnamese"], variable: "--font-source-sans", display: "swap" });
const serif = Source_Serif_4({ subsets: ["latin", "vietnamese"], variable: "--font-source-serif", display: "swap" });

export const metadata: Metadata = {
  title: "CampusHub",
  description: "Cổng học tập và học vụ CampusHub v3",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi" className={`${sans.variable} ${serif.variable}`}>
      <body className="font-sans antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
