export const API_BASE = window.location.origin;

export async function fetchStations() {
  const res = await fetch(`${API_BASE}/api/stations`);
  if (!res.ok) throw new Error('Failed to fetch stations');
  return res.json();
}

export async function fetchSinglePrediction(station, date, hour) {
  const res = await fetch(`${API_BASE}/api/predict/single`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ station, date, hour: parseInt(hour) })
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Prediction failed');
  }
  return res.json();
}

export async function fetchForecast(station, date) {
  const res = await fetch(`${API_BASE}/api/predict/forecast`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ station, date, seed_midnight: 0, seed_11pm_prev: 0 })
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Forecast failed');
  }
  return res.json();
}
