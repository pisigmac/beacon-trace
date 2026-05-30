import { useEffect, useRef, useState, useCallback } from 'react'

const WS_URL = (import.meta as any).env.VITE_WS_URL || 'ws://localhost:8000/ws'

interface WSEvent {
  type: string
  data: any
}

export function useWebSocket() {
  const [lastEvent, setLastEvent] = useState<WSEvent | null>(null)
  const [connected, setConnected] = useState(false)
  const ws = useRef<WebSocket | null>(null)
  const reconnectTimeout = useRef<ReturnType<typeof setTimeout> | null>(null)

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) return

    const socket = new WebSocket(WS_URL)

    socket.onopen = () => {
      setConnected(true)
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current)
        reconnectTimeout.current = null
      }
    }

    socket.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data)
        setLastEvent(parsed)
      } catch {
        // Ignore non-JSON messages
      }
    }

    socket.onclose = () => {
      setConnected(false)
      ws.current = null
      reconnectTimeout.current = setTimeout(connect, 3000)
    }

    socket.onerror = () => {
      socket.close()
    }

    ws.current = socket
  }, [])

  useEffect(() => {
    connect()
    return () => {
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current)
      ws.current?.close()
    }
  }, [connect])

  return { connected, lastEvent }
}