import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { submitInteractionForm } from "../slices/interactionSlice";

const INTERACTION_TYPES = ["In-person visit", "Video call", "Phone call", "Conference"];

export default function StructuredForm({ hcpId, repId }) {
  const dispatch = useDispatch();
  const { status, lastResult } = useSelector((s) => s.interaction);

  const [form, setForm] = useState({
    interactionType: INTERACTION_TYPES[0],
    date: new Date().toISOString().slice(0, 10),
    productsDiscussed: "",
    samplesGiven: "",
    notes: "",
  });

  const update = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleSubmit = (e) => {
    e.preventDefault();
    const raw_text = `Interaction type: ${form.interactionType}. Date: ${form.date}.
Products discussed: ${form.productsDiscussed}. Samples given: ${form.samplesGiven}.
Notes: ${form.notes}`;

    dispatch(
      submitInteractionForm({
        hcp_id: hcpId,
        rep_id: repId,
        input_mode: "form",
        raw_text,
        structured_payload: form,
      })
    );
  };

  return (
    <div className="card">
      <form onSubmit={handleSubmit}>
        <label htmlFor="interactionType">Interaction type</label>
        <select id="interactionType" value={form.interactionType} onChange={update("interactionType")}>
          {INTERACTION_TYPES.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>

        <label htmlFor="date">Date</label>
        <input id="date" type="date" value={form.date} onChange={update("date")} />

        <label htmlFor="productsDiscussed">Products discussed</label>
        <input
          id="productsDiscussed"
          type="text"
          placeholder="e.g. Cardovex 10mg"
          value={form.productsDiscussed}
          onChange={update("productsDiscussed")}
        />

        <label htmlFor="samplesGiven">Samples given</label>
        <input
          id="samplesGiven"
          type="text"
          placeholder="e.g. 2 boxes Cardovex samples"
          value={form.samplesGiven}
          onChange={update("samplesGiven")}
        />

        <label htmlFor="notes">Notes</label>
        <textarea
          id="notes"
          placeholder="What was discussed, how the HCP reacted, any questions raised..."
          value={form.notes}
          onChange={update("notes")}
        />

        <button className="btn-primary" type="submit" disabled={status === "loading"}>
          {status === "loading" ? "Logging..." : "Log interaction"}
        </button>
      </form>

      {lastResult && <ResultSummary result={lastResult} />}
    </div>
  );
}

function ResultSummary({ result }) {
  return (
    <div className="result-card">
      <h3>Logged &amp; analyzed</h3>
      <p><strong>Summary:</strong> {result.summary}</p>
      <p>
        <strong>Sentiment:</strong>{" "}
        <span className={`badge ${result.sentiment}`}>{result.sentiment}</span>
      </p>
      {result.compliance_flags?.length > 0 && (
        <p><strong>Compliance flags:</strong> {result.compliance_flags.join(", ")}</p>
      )}
      <p><strong>Next best action:</strong> {result.next_best_action}</p>
      <p><strong>Follow-up date:</strong> {result.followup_date}</p>
    </div>
  );
}
