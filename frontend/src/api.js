const API_BASE = 'http://localhost:8000'

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed: ${res.status}`)
  }
  return res.json()
}

export const getAssets = () => request('/assets')
export const getIncidents = () => request('/incidents')
export const getIncidentReport = (incidentId) =>
  request(`/incidents/${incidentId}/report`).catch(() => null)
export const generateIncidentReport = (incidentId) =>
  request(`/incidents/${incidentId}/generate-report`, { method: 'POST' })