/**
 * medicAPI.js
 * Typed service layer for all SympDecoder backend calls.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

/**
 * POST /chat
 * Full pipeline: Safety → NLP → RAG → LLM
 * @param {string} message
 * @param {string|null} sessionId
 * @returns {{ response, sources, severity, is_emergency, session_id }}
 */
export const sendMessage = (message, sessionId = null) =>
  request('/chat', {
    method: 'POST',
    body: JSON.stringify({ message, session_id: sessionId }),
  })

/**
 * POST /analyze-symptom
 * NLP pipeline only — fast, no LLM call.
 * @param {string} message
 * @returns {{ intent, symptoms, severity, is_emergency, ... }}
 */
export const analyzeSymptom = (message) =>
  request('/analyze-symptom', {
    method: 'POST',
    body: JSON.stringify({ message }),
  })

/**
 * POST /feedback
 * Rate a bot response.
 * @param {string} sessionId
 * @param {'HELPFUL'|'NOT_HELPFUL'|'INACCURATE'|'EMERGENCY_MISSED'} rating
 * @param {number} messageId
 */
export const submitFeedback = (sessionId, rating, messageId) =>
  request('/feedback', {
    method: 'POST',
    body: JSON.stringify({
      session_id: sessionId,
      rating,
      message_id: String(messageId),
    }),
  })

/**
 * GET /knowledge-sources
 * Lists all indexed medical document chunks.
 */
export const getKnowledgeSources = () => request('/knowledge-sources')

/**
 * GET /health-check
 * Returns service health status.
 */
export const healthCheck = () => request('/health-check')
