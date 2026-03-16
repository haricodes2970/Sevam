/**
 * EmergencyAlert
 * Full-screen red overlay triggered when is_emergency === true.
 * Displays emergency numbers and a dismiss option.
 */
export default function EmergencyAlert({ message, onDismiss }) {
  const NUMBERS = [
    { label: 'International', num: '112' },
    { label: 'US / Canada',   num: '911' },
    { label: 'India (Amb.)',  num: '108' },
  ]

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 anim-overlay"
      style={{ background: 'rgba(0,0,0,0.88)', backdropFilter: 'blur(10px)' }}
    >
      <div
        className="max-w-md w-full rounded-2xl p-8 anim-card-in anim-red-pulse"
        style={{
          background: '#0f0a0a',
          border: '2px solid var(--sev-emergency)',
        }}
      >
        {/* Icon */}
        <div className="flex justify-center mb-5">
          <div
            className="w-20 h-20 rounded-full flex items-center justify-center"
            style={{
              background: 'rgba(239,68,68,0.12)',
              border: '2px solid rgba(239,68,68,0.35)',
            }}
          >
            <span style={{ fontSize: '2.6rem' }}>🚨</span>
          </div>
        </div>

        {/* Title */}
        <h2
          className="text-center text-2xl font-bold mb-2 tracking-wider"
          style={{ color: 'var(--sev-emergency)', fontFamily: 'Outfit', letterSpacing: '0.06em' }}
        >
          MEDICAL EMERGENCY
        </h2>

        {/* Message */}
        <p
          className="text-center text-sm mb-6"
          style={{ color: '#f0a0a0', fontFamily: 'IBM Plex Mono', lineHeight: '1.7' }}
        >
          {message || 'Your symptoms may indicate a serious medical emergency. Please seek immediate care.'}
        </p>

        {/* Emergency numbers */}
        <div className="grid grid-cols-3 gap-2 mb-6">
          {NUMBERS.map(({ label, num }) => (
            <div
              key={num}
              className="text-center p-3 rounded-xl"
              style={{
                background: 'rgba(239,68,68,0.08)',
                border: '1px solid rgba(239,68,68,0.18)',
              }}
            >
              <div className="text-xs mb-1" style={{ color: '#e0a0a0' }}>{label}</div>
              <div
                className="text-xl font-bold font-mono"
                style={{ color: 'var(--sev-emergency)' }}
              >
                {num}
              </div>
            </div>
          ))}
        </div>

        {/* Dismiss */}
        <button
          onClick={onDismiss}
          className="w-full py-2.5 rounded-xl text-sm font-mono transition-all"
          style={{
            background: 'transparent',
            border: '1px solid rgba(239,68,68,0.25)',
            color: 'rgba(240,160,160,0.65)',
            cursor: 'pointer',
          }}
          onMouseEnter={(e) => {
            e.target.style.borderColor = 'rgba(239,68,68,0.55)'
            e.target.style.color = '#f0a0a0'
          }}
          onMouseLeave={(e) => {
            e.target.style.borderColor = 'rgba(239,68,68,0.25)'
            e.target.style.color = 'rgba(240,160,160,0.65)'
          }}
        >
          I understand — close this alert
        </button>
      </div>
    </div>
  )
}
