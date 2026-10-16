const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');
export async function getAnalytics() {
  const res = await fetch(`${API_BASE}/api/analytics`);
  if (!res.ok) throw new Error(`Analytics request failed (${res.status})`);
  return res.json();
}
export async function recommendRooms(payload) {
  const res = await fetch(`${API_BASE}/api/recommend`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.detail || `Recommendation request failed (${res.status})`);
  return body;
}
