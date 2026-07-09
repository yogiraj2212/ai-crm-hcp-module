import React, { useState, useRef, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { sendMessage } from "../slices/interactionSlice";

export default function ChatInterface({ hcpId, repId }) {
  const dispatch = useDispatch();
  const { chatHistory, status, lastResult } = useSelector((s) => s.interaction);
  const [draft, setDraft] = useState("");
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [chatHistory]);

  const handleSend = (e) => {
    e.preventDefault();
    if (!draft.trim()) return;
    dispatch(sendMessage({ hcp_id: hcpId, rep_id: repId, message: draft, history: chatHistory }));
    setDraft("");
  };

  return (
    <div className="card">
      <div className="chat-window" ref={scrollRef}>
        {chatHistory.length === 0 && (
          <div className="chat-bubble assistant">
            Hi! Tell me about the visit you just had - which HCP, what you
            discussed, and how it went. I'll log it for you.
          </div>
        )}
        {chatHistory.map((m, i) => (
          <div key={i} className={`chat-bubble ${m.role === "user" ? "user" : "assistant"}`}>
            {m.content}
          </div>
        ))}
        {status === "loading" && (
          <div className="chat-bubble assistant">Thinking...</div>
        )}
      </div>

      <form className="chat-input-row" onSubmit={handleSend}>
        <input
          type="text"
          placeholder="e.g. Just met Dr. Rao, discussed Cardovex, she wants more efficacy data"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
        />
        <button className="btn-primary" type="submit" disabled={status === "loading"}>
          Send
        </button>
      </form>

      {lastResult && (
        <div className="result-card">
          <h3>✓ Logged &amp; analyzed</h3>
          <p><strong>Summary:</strong> {lastResult.summary}</p>
          <p>
            <strong>Sentiment:</strong>{" "}
            <span className={`badge ${lastResult.sentiment}`}>{lastResult.sentiment}</span>
          </p>
          {lastResult.compliance_flags?.length > 0 && (
            <p><strong>Compliance flags:</strong> {lastResult.compliance_flags.join(", ")}</p>
          )}
          <p><strong>Next best action:</strong> {lastResult.next_best_action}</p>
          <p><strong>Follow-up date:</strong> {lastResult.followup_date}</p>
        </div>
      )}
    </div>
  );
}
