const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export async function submitForm(payload) {
  const res = await fetch(`${BASE_URL}/api/interactions/form`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to submit interaction");
  return res.json();
}

export async function sendChatMessage(payload) {
  const res = await fetch(`${BASE_URL}/api/interactions/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to send message");
  return res.json();
}
