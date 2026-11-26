const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

async function parseJsonResponse(response) {
  let data = null;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const message =
      data?.detail || `Request failed with status ${response.status}.`;
    throw new Error(message);
  }
  return data;
}

export async function uploadDocuments(files, sessionId) {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }
  if (sessionId) {
    formData.append("session_id", sessionId);
  }

  const response = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: formData,
  });
  return parseJsonResponse(response);
}

export async function askQuestion(sessionId, question) {
  const response = await fetch(`${API_BASE}/api/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, question }),
  });
  return parseJsonResponse(response);
}

export async function clearSession(sessionId) {
  if (!sessionId) return;
  await fetch(`${API_BASE}/api/session/${encodeURIComponent(sessionId)}`, {
    method: "DELETE",
  });
}
