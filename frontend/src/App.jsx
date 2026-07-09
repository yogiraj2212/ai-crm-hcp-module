import React from "react";
import LogInteractionScreen from "./components/LogInteractionScreen";

// In a full app these would come from routing/auth context;
// hardcoded here for the assignment's scope.
const DEMO_HCP = { id: "hcp-001", name: "Dr. Anjali Rao - Cardiology" };
const DEMO_REP_ID = "rep-001";

export default function App() {
  return (
    <LogInteractionScreen
      hcpId={DEMO_HCP.id}
      hcpName={DEMO_HCP.name}
      repId={DEMO_REP_ID}
    />
  );
}
