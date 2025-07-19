import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "phiDelta - AI Research Assistant",
  description: "Advanced AI-powered research and analysis platform",
  icons: {
    icon: [
      {
        url: "/squarelogophidelta.png",
        sizes: "32x32",
        type: "image/png",
      },
      {
        url: "/squarelogophidelta.png", 
        sizes: "16x16",
        type: "image/png",
      }
    ],
    apple: {
      url: "/squarelogophidelta.png",
      sizes: "180x180",
      type: "image/png",
    },
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
