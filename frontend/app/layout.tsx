"use client";

import Footer from "@/components/Footer";
import Header from "@/components/Header";
import ScrollToTop from "@/components/ScrollToTop";
import AuthCheck from "@/components/AuthCheck";
import { Inter } from "next/font/google";
import "node_modules/react-modal-video/css/modal-video.css";
import "../styles/index.css";
import { SessionProvider, useSession } from "next-auth/react";
import { Providers } from "./providers";

const inter = Inter({ subsets: ["latin"] });

// Footer bileşenini sadece giriş yapmamış kullanıcılara gösteren fonksiyon bileşen
function ConditionalFooter() {
  const { data: session } = useSession();
  
  // Kullanıcı giriş yapmamışsa Footer'ı göster
  if (!session) {
    return <Footer />;
  }
  
  // Kullanıcı giriş yapmışsa Footer'ı gösterme
  return null;
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html suppressHydrationWarning lang="en">
      <head />
      <body className={`bg-[#FCFCFC] dark:bg-black ${inter.className}`}>
        <SessionProvider>
          <Providers>
            <AuthCheck />
            <Header />
            {children}
            <ConditionalFooter />
            <ScrollToTop />
          </Providers>
        </SessionProvider>
      </body>
    </html>
  );
}