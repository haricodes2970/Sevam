import { useState } from 'react'
import SeverityBadge from './SeverityBadge'
import { submitFeedback } from '../api/medicAPI'

/**
 * MessageBubble
 * Renders either a user message (right-aligned teal)
 * or a bot message (left-aligned dark card with severity, sources, feedback).
 */
export default function MessageBubble({ message, sessionId }) {
  const [voted, setVoted] = useState(null) // 'up' | 'down' | null

  const isBot = message.role === 'bot'

  const handleFeedback = async (rating) => {
    if (voted) return
    setVoted(rating === 'HELPFUL' ? 'up' : 'down')
    try {
      await submitFeedback(sessionId, rating, message.id)
    } catch {
      // Feedback is best-effort — don't block the UI
    }
  }

  const time = new Date(message.timestamp).toLocaleTimeString('en', {
    hour: '2-digit',
    minute: '2-digit',
  })

  /* ── User bubble ─────────────────────────────────────── */
  if (!isBot) {
    return (
      <div className="flex items-end justify-end gap-2.5 mb-5 anim-slide-up">
        <div className="max-w-xs md:max-w-md lg:max-w-lg">
          <div className="bubble-user px-4 py-3">{message.content}</div>
          <div className="mt-1 text-right">
            <span className="text-xs font-mono" style={{ color: 'var(--text-muted)' }}>
              {time}
            </span>
          </div>
        </div>
        <div
          className="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 mb-5"
          style={{ background: 'rgba(0,217,166,0.15)', border: '1px solid rgba(0,217,166,0.25)' }}
        >
          <span style={{ fontSize: '0.7rem' }}>👤</span>
        </div>
      </div>
    )
  }

  /* ── Bot bubble ──────────────────────────────────────── */
  const sev = (message.severity || '').toUpperCase()
  const bubbleClass = [
    'bubble-bot px-5 py-4',
    sev === 'EMERGENCY' ? 'sev-emergency' : '',
    sev === 'HIGH'      ? 'sev-high'      : '',
  ].join(' ')

  return (
    <div className="flex items-start gap-3 mb-6 anim-slide-up">
      {/* Bot avatar */}
      <div
        className="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 mt-1"
        style={{ background: 'var(--accent-dim)', border: '1px solid rgba(0,217,166,0.18)' }}
      >
        <span style={{ fontSize: '0.7rem' }}>🩺</span>
      </div>

      <div className="flex-1 min-w-0 max-w-2xl">
        {/* Main bubble */}
        <div className={bubbleClass}>
          {/* Top meta row */}
          <div className="flex items-center gap-2 mb-3 flex-wrap">
            <span
              className="text-xs font-mono"
              style={{ color: 'var(--accent)', opacity: 0.65 }}
            >
              SympDecoder
            </span>
            {message.severity && <SeverityBadge severity={message.severity} />}
          </div>

          {/* Response text */}
          <div className="whitespace-pre-wrap" style={{ color: 'var(--text-primary)' }}>
            {message.content}
          </div>
        </div>

        {/* Bottom row: sources + feedback + timestamp */}
        <div className="flex items-center justify-between mt-2 flex-wrap gap-y-1.5 gap-x-3">

          {/* Sources */}
          <div className="flex items-center gap-1.5 flex-wrap">
            {message.sources && message.sources.length > 0 && (
              <>
                <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  Sources:
                </span>
                {message.sources.map((src) => (
                  <span key={src} className="source-chip">{src}</span>
                ))}
              </>
            )}
          </div>

          {/* Feedback + time */}
          <div className="flex items-center gap-2 ml-auto">
            {voted === null ? (
              <>
                <button
                  className="btn-feedback"
                  onClick={() => handleFeedback('HELPFUL')}
                  title="Mark as helpful"
                >
                  👍 Helpful
                </button>
                <button
                  className="btn-feedback"
                  onClick={() => handleFeedback('NOT_HELPFUL')}
                  title="Mark as not helpful"
                >
                  👎 Not helpful
                </button>
              </>
            ) : (
              <span
                className="text-xs font-mono"
                style={{ color: 'var(--sev-low)' }}
              >
                ✓ Feedback recorded
              </span>
            )}
            <span className="text-xs font-mono" style={{ color: 'var(--text-muted)' }}>
              {time}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
