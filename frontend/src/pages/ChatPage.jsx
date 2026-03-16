import { useState } from 'react'
import Header from '../components/Header'
import ChatWindow from '../components/ChatWindow'
import EmergencyAlert from '../components/EmergencyAlert'
import { sendMessage } from '../api/medicAPI'

/**
 * ChatPage
 * Top-level page. Owns all conversation state:
 *   messages, sessionId, isLoading, showEmergency.
 */
export default function ChatPage() {
  const [messages,       setMessages]       = useState([])
  const [sessionId,      setSessionId]      = useState(null)
  const [isLoading,      setIsLoading]      = useState(false)
  const [showEmergency,  setShowEmergency]  = useState(false)
  const [emergencyMsg,   setEmergencyMsg]   = useState('')

  /**
   * Send a message through the full pipeline.
   * Adds the user message immediately, then awaits the bot response.
   */
  const handleSend = async (text) => {
    // Optimistic user message
    const userMsg = {
      id:        Date.now(),
      role:      'user',
      content:   text,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMsg])
    setIsLoading(true)

    try {
      const data = await sendMessage(text, sessionId)

      // Persist session ID from first response
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id)
      }

      // Trigger emergency overlay
      if (data.is_emergency) {
        setEmergencyMsg(data.response)
        setShowEmergency(true)
      }

      const botMsg = {
        id:           Date.now() + 1,
        role:         'bot',
        content:      data.response  || '',
        sources:      data.sources   || [],
        severity:     data.severity  || 'LOW',
        is_emergency: data.is_emergency || false,
        timestamp:    new Date(),
      }
      setMessages((prev) => [...prev, botMsg])

    } catch (err) {
      // Network / server error fallback
      const errMsg = {
        id:           Date.now() + 1,
        role:         'bot',
        content:      `⚠ Could not reach the medical knowledge system.\n\nPlease make sure the backend is running:\n\n  python run_api.py\n\nThen refresh this page.`,
        sources:      [],
        severity:     'LOW',
        is_emergency: false,
        timestamp:    new Date(),
      }
      setMessages((prev) => [...prev, errMsg])
      console.error('[SympDecoder] API error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div
      className="flex flex-col h-screen bg-grid"
      style={{ background: 'var(--bg-primary)' }}
    >
      <Header />

      <main className="flex-1 overflow-hidden w-full max-w-4xl mx-auto flex flex-col">
        <ChatWindow
          messages={messages}
          sessionId={sessionId}
          isLoading={isLoading}
          onSend={handleSend}
        />
      </main>

      {showEmergency && (
        <EmergencyAlert
          message={emergencyMsg}
          onDismiss={() => setShowEmergency(false)}
        />
      )}
    </div>
  )
}
