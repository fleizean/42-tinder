import ScrollUp from "@/components/Common/ScrollUp";
import Features from "@/components/Features";
import Hero from "@/components/Hero";
import Pricing from "@/components/SuccessStories";
import Quote from "@/components/Quote";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "CrushIt",
  description: "CrushIt sizin için CV kalitenizi arttıracak bir platformdur.",
  // other metadata
};

export default function Home() {
  return (
    <>
      <ScrollUp />
      <Hero />
      <Features />
      <Quote />
      <Pricing />
    </>
  );
}
