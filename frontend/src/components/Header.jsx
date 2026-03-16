import { useState, useEffect } from 'react'
import { healthCheck } from '../api/medicAPI'

/**
 * Header
 * Contains: animated heartbeat logo, status dot, disclaimer badge.
 */
export default function Header() {
  const [status, setStatus] = useState('checking') // 'online' | 'offline' | 'checking'

  useEffect(() => {
    healthCheck()
      .then(() => setStatus('online'))
      .catch(() => setStatus('offline'))
  }, [])

  const dotColor =
    status === 'online'   ? 'var(--sev-low)'       :
    status === 'offline'  ? 'var(--sev-emergency)'  :
    'var(--sev-medium)'

  const statusLabel =
    status === 'online'  ? 'API Online'     :
    status === 'offline' ? 'API Offline'    :
    'Connecting…'

  return (
    <header style={{ background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border)' }}>
      <div className="max-w-4xl mx-auto px-5 py-3.5 flex items-center justify-between gap-4">

        {/* Logo */}
        <div className="flex items-center gap-3">
          {/* Heartbeat SVG */}
          <div className="w-8 h-8 flex items-center justify-center">
            <svg
              width="34"
              height="22"
              viewBox="0 0 34 22"
              fill="none"
              className="anim-heartbeat"
            >
              <polyline
                points="1,11 5,11 7,3 11,19 13,9 15,13 19,13 21,7 23,11 27,11 33,11"
                stroke="var(--accent)"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>

          {/* Name */}
          <div>
            <h1
              className="text-lg font-semibold leading-none tracking-tight"
              style={{ fontFamily: 'Outfit' }}
            >
              Symp<span style={{ color: 'var(--accent)' }}>Decoder</span>
            </h1>
            <p
              className="text-xs mt-0.5"
              style={{ color: 'var(--text-muted)', fontFamily: 'IBM Plex Mono' }}
            >
              RAG · Medical AI
            </p>
          </div>
        </div>

        {/* Right */}
        <div className="flex items-center gap-3 flex-wrap justify-end">

          {/* Status dot */}
          <div className="flex items-center gap-1.5">
            <span
              className={`w-2 h-2 rounded-full inline-block ${status === 'checking' ? 'anim-status-blink' : ''}`}
              style={{ background: dotColor }}
            />
            <span
              className="text-xs font-mono hidden sm:inline"
              style={{ color: 'var(--text-muted)' }}
            >
              {statusLabel}
            </span>
          </div>

          {/* Disclaimer badge */}
          <div
            className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-md"
            style={{
              background: 'rgba(249,115,22,0.08)',
              border:     '1px solid rgba(249,115,22,0.18)',
            }}
          >
            <span
              style={{
                color: 'var(--sev-high)',
                fontSize: '0.62rem',
                fontWeight: 600,
                letterSpacing: '0.05em',
                textTransform: 'uppercase',
              }}
            >
              ⚠ Not a substitute for medical advice
            </span>
          </div>
        </div>
      </div>

      {/* Accent rule */}
      <div className="header-rule" />
    </header>
  )
}
