/**
 * TypingIndicator
 * Three bouncing dots shown while the LLM is generating a response.
 */
export default function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 mb-6 anim-slide-up">
      {/* Avatar */}
      <div
        className="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 mt-1"
        style={{ background: 'var(--accent-dim)', border: '1px solid rgba(0,217,166,0.18)' }}
      >
        <span style={{ fontSize: '0.7rem' }}>🩺</span>
      </div>

      {/* Bubble */}
      <div className="bubble-bot px-5 py-3.5">
        <div className="flex items-center gap-1.5">
          {[1, 2, 3].map((n) => (
            <span
              key={n}
              className={`dot-${n} inline-block w-2 h-2 rounded-full`}
              style={{ background: 'var(--text-muted)' }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
