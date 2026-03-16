import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'

const SUGGESTED_PROMPTS = [
  'I have a headache and feel nauseous',
  'My throat hurts when I swallow',
  'I have chest pain after eating',
  "I've had a fever for 2 days",
  'I feel dizzy when I stand up',
  'My lower back is very painful',
]

/**
 * ChatWindow
 * Handles: message list, typing indicator, auto-scroll,
 * suggested-prompts empty state, and the chat input bar.
 */
export default function ChatWindow({ messages, sessionId, isLoading, onSend }) {
  const [input, setInput] = useState('')
  const bottomRef  = useRef(null)
  const inputRef   = useRef(null)
  const textareaRef = useRef(null)

  /* Auto-scroll to bottom on new messages */
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  /* Auto-resize textarea */
  const resizeTextarea = () => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 120)}px`
  }

  const handleChange = (e) => {
    setInput(e.target.value)
    resizeTextarea()
  }

  const handleSend = () => {
    const text = input.trim()
    if (!text || isLoading) return
    onSend(text)
    setInput('')
    // Reset textarea height
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
    inputRef.current?.focus()
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const isEmpty = messages.length === 0

  return (
    <div className="flex flex-col h-full overflow-hidden">

      {/* ── Message list ───────────────────────────────── */}
      <div
        className="flex-1 overflow-y-auto px-4 md:px-8 py-6"
        style={{ scrollbarWidth: 'thin' }}
      >
        {/* Empty state — suggested prompts */}
        {isEmpty && (
          <div className="flex flex-col items-center justify-center h-full anim-fade-in">
            <div
              className="w-16 h-16 rounded-2xl flex items-center justify-center mb-4"
              style={{
                background: 'var(--accent-dim)',
                border:     '1px solid rgba(0,217,166,0.18)',
              }}
            >
              <span style={{ fontSize: '2rem' }}>🩺</span>
            </div>

            <h2
              className="text-xl font-semibold mb-1.5"
              style={{ color: 'var(--text-primary)' }}
            >
              How can I help you today?
            </h2>
            <p
              className="text-sm mb-8 text-center max-w-sm"
              style={{ color: 'var(--text-secondary)', lineHeight: '1.6' }}
            >
              Describe your symptoms and I'll provide grounded information
              from trusted medical knowledge.
            </p>

            {/* Prompt grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-lg">
              {SUGGESTED_PROMPTS.map((p) => (
                <button
                  key={p}
                  className="prompt-card"
                  onClick={() => onSend(p)}
                >
                  <span style={{ color: 'var(--accent)', marginRight: 7 }}>›</span>
                  {p}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Messages */}
        {!isEmpty && messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} sessionId={sessionId} />
        ))}

        {/* Typing indicator */}
        {isLoading && <TypingIndicator />}

        {/* Scroll anchor */}
        <div ref={bottomRef} />
      </div>

      {/* ── Disclaimer bar ──────────────────────────────── */}
      <div
        className="px-6 py-1.5 text-center"
        style={{ borderTop: '1px solid var(--border)', background: 'var(--bg-secondary)' }}
      >
        <p
          className="text-xs font-mono"
          style={{ color: 'var(--text-muted)' }}
        >
          ⚕ Informational only — always consult a qualified healthcare professional
        </p>
      </div>

      {/* ── Input area ──────────────────────────────────── */}
      <div
        className="px-4 md:px-8 py-4"
        style={{ background: 'var(--bg-secondary)', borderTop: '1px solid var(--border)' }}
      >
        <div className="max-w-4xl mx-auto flex gap-3 items-end">
          <textarea
            ref={(el) => { textareaRef.current = el; inputRef.current = el }}
            value={input}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder="Describe your symptoms…"
            rows={1}
            disabled={isLoading}
            className="flex-1 chat-input rounded-xl px-4 py-3 resize-none"
            style={{ minHeight: '48px', maxHeight: '120px' }}
          />

          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="btn-send w-12 h-12 rounded-xl flex items-center justify-center text-lg"
            title="Send message (Enter)"
          >
            {isLoading ? (
              <span
                className="w-4 h-4 border-2 rounded-full"
                style={{
                  borderColor:    'transparent',
                  borderTopColor: 'var(--text-muted)',
                  animation:      'spin 0.7s linear infinite',
                  display:        'inline-block',
                }}
              />
            ) : (
              '↑'
            )}
          </button>
        </div>

        <p
          className="text-center mt-1.5 text-xs font-mono"
          style={{ color: 'var(--text-muted)' }}
        >
          Enter to send · Shift+Enter for new line
        </p>
      </div>

      {/* Inline spin keyframe (no extra file needed) */}
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}
