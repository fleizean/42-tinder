import Dashboard from "@/components/Dashboard/Dashboard";
import Breadcrumb from "@/components/Common/Breadcrumb";

import { Metadata } from "next";
import { Toaster } from "react-hot-toast";

export const metadata: Metadata = {
  title: "Ana Sayfa | CrushIt",
  description: "CrushIt sizin için CV kalitenizi arttıracak bir platformdur.",
  // other metadata
};

const DashboardPage = () => {
  return (
    <>
       <Toaster position="top-right" />
      <Dashboard />
    </>
  );
};

export default DashboardPage;
