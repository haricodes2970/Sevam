/**
 * SeverityBadge
 * Coloured pill showing LOW / MEDIUM / HIGH / EMERGENCY.
 */

const CONFIG = {
  LOW:       { color: '#22c55e', bg: 'rgba(34,197,94,0.10)',  border: 'rgba(34,197,94,0.22)',   icon: '●', label: 'Low'       },
  MEDIUM:    { color: '#f59e0b', bg: 'rgba(245,158,11,0.10)', border: 'rgba(245,158,11,0.22)',  icon: '◆', label: 'Medium'    },
  HIGH:      { color: '#f97316', bg: 'rgba(249,115,22,0.10)', border: 'rgba(249,115,22,0.22)',  icon: '▲', label: 'High'      },
  EMERGENCY: { color: '#ef4444', bg: 'rgba(239,68,68,0.12)',  border: 'rgba(239,68,68,0.25)',   icon: '⚠', label: 'Emergency' },
}

export default function SeverityBadge({ severity }) {
  const cfg = CONFIG[(severity || '').toUpperCase()] || CONFIG.LOW
  return (
    <span
      className="sev-badge"
      style={{ color: cfg.color, background: cfg.bg, border: `1px solid ${cfg.border}` }}
    >
      <span style={{ fontSize: '0.6rem' }}>{cfg.icon}</span>
      <span>{cfg.label}</span>
    </span>
  )
}
