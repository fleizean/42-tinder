import Match from "@/components/Match/Match";
import Breadcrumb from "@/components/Common/Breadcrumb";

import { Metadata } from "next";
import { Toaster } from "react-hot-toast";

export const metadata: Metadata = {
  title: "Ana Sayfa | CrushIt",
  description: "CrushIt sizin için CV kalitenizi arttıracak bir platformdur.",
  // other metadata
};

const MatchPage = () => {
  return (
    <>
       <Toaster position="top-right" />
      <Match />
    </>
  );
};

export default MatchPage;
