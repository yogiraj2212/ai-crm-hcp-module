import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { setMode } from "../slices/interactionSlice";
import StructuredForm from "./StructuredForm";
import ChatInterface from "./ChatInterface";

export default function LogInteractionScreen({ hcpId, hcpName, repId }) {
  const dispatch = useDispatch();
  const mode = useSelector((s) => s.interaction.mode);

  return (
    <div className="app-shell">
      <div className="app-header">
        <h1>Log Interaction</h1>
        <span className="hcp-name">HCP: {hcpName}</span>
      </div>

      <div className="mode-toggle">
        <button
          className={mode === "form" ? "active" : ""}
          onClick={() => dispatch(setMode("form"))}
        >
          Structured Form
        </button>
        <button
          className={mode === "chat" ? "active" : ""}
          onClick={() => dispatch(setMode("chat"))}
        >
          Chat
        </button>
      </div>

      {mode === "form" ? (
        <StructuredForm hcpId={hcpId} repId={repId} />
      ) : (
        <ChatInterface hcpId={hcpId} repId={repId} />
      )}
    </div>
  );
}
