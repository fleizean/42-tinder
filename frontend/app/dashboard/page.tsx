import Dashboard from "@/components/Dashboard/Dashboard";
import Breadcrumb from "@/components/Common/Breadcrumb";

import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Ana Sayfa | CrushIt",
  description: "CrushIt sizin için CV kalitenizi arttıracak bir platformdur.",
  // other metadata
};

const DashboardPage = () => {
  return (
    <>
      <Dashboard />
    </>
  );
};

export default DashboardPage;
