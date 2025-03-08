"use client";

import Footer from "@/components/Footer";
import Header from "@/components/Header";
import ScrollToTop from "@/components/ScrollToTop";
import { Inter } from "next/font/google";
import "node_modules/react-modal-video/css/modal-video.css";
import "../styles/index.css";
import { SessionProvider } from "next-auth/react";
import { Providers } from "./providers";
import { GoogleOAuthProvider } from '@react-oauth/google';
const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html suppressHydrationWarning lang="en">
      <head />
      <body className={`bg-[#FCFCFC] dark:bg-black ${inter.className}`}>
        <GoogleOAuthProvider clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID!}>
          <SessionProvider>
            <Providers>
              <Header />
              {children}
              <Footer />
              <ScrollToTop />
            </Providers>
          </SessionProvider>
        </GoogleOAuthProvider>
      </body>
    </html>
  );
}