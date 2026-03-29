import { useEffect, useRef, useState } from 'react'
import Controls from './components/Controls'
import GuidePanel from './components/GuidePanel'
import Header from './components/Header'
import HistoryPanel from './components/HistoryPanel'
import { useLocalStorage } from './hooks/useLocalStorage'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
const WS_BASE = (import.meta.env.VITE_WS_BASE || 'ws://localhost:8000') + '/ws/translate'

function speak(text, lang) {
  if (!('speechSynthesis' in window) || !text) return
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = lang === 'hi' ? 'hi-IN' : 'en-IN'
  window.speechSynthesis.cancel()
  window.speechSynthesis.speak(utterance)
}

export default function App() {
  const videoRef = useRef(null)
  const canvasRef = useRef(document.createElement('canvas'))
  const wsRef = useRef(null)
  const streamRef = useRef(null)

  const [darkMode, setDarkMode] = useLocalStorage('visonsign-dark', true)
  const [language, setLanguage] = useState('en')
  const [speakerOn, setSpeakerOn] = useState(true)
  const [translation, setTranslation] = useState('Waiting for gesture...')
  const [confidence, setConfidence] = useState(0)
  const [history, setHistory] = useLocalStorage('visonsign-history', [])
  const [uploadResult, setUploadResult] = useState('')

  useEffect(() => {
    document.body.className = darkMode ? 'theme-dark' : 'theme-light'
  }, [darkMode])

  useEffect(() => {
    const connect = () => {
      wsRef.current = new WebSocket(WS_BASE)
      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.text) {
          setTranslation(data.text)
          const conf = Math.round((data.confidence || 0) * 100)
          setConfidence(conf)
          setHistory((prev) => [{ text: data.text, confidence: conf }, ...prev].slice(0, 30))
          if (speakerOn) speak(data.text, language)
        }
      }
    }

    connect()
    return () => wsRef.current?.close()
  }, [language, speakerOn, setHistory])

  useEffect(() => {
    const startCamera = async () => {
      streamRef.current = await navigator.mediaDevices.getUserMedia({ video: true, audio: false })
      if (videoRef.current) {
        videoRef.current.srcObject = streamRef.current
      }
    }

    startCamera().catch(() => setTranslation('Camera access denied.'))
    return () => streamRef.current?.getTracks().forEach((t) => t.stop())
  }, [])

  useEffect(() => {
    const timer = setInterval(() => {
      if (!videoRef.current || wsRef.current?.readyState !== WebSocket.OPEN) return
      const canvas = canvasRef.current
      canvas.width = 320
      canvas.height = 240
      const ctx = canvas.getContext('2d')
      ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height)
      const frame = canvas.toDataURL('image/jpeg', 0.6).split(',')[1]
      wsRef.current.send(JSON.stringify({ frame, language }))
    }, 120)

    return () => clearInterval(timer)
  }, [language])

  const handleUpload = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)
    formData.append('language', language)

    const response = await fetch(`${API_BASE}/translate/video`, {
      method: 'POST',
      body: formData,
    })
    const data = await response.json()
    setUploadResult(data.transcript || 'No gesture detected in video')
  }

  return (
    <div className="app-shell">
      <Header darkMode={darkMode} onToggleDark={() => setDarkMode((v) => !v)} />

      <main className="grid">
        <section className="glass card live-panel">
          <h2>Live Interpreter</h2>
          <video ref={videoRef} autoPlay playsInline muted className="video" />
          <div className="output">
            <p className="text">{translation}</p>
            <p className="confidence">Confidence: {confidence}%</p>
          </div>
        </section>

        <section className="side-stack">
          <Controls
            language={language}
            setLanguage={setLanguage}
            speakerOn={speakerOn}
            setSpeakerOn={setSpeakerOn}
          />
          <div className="glass card upload">
            <h3>Offline Video Translation</h3>
            <input type="file" accept="video/*" onChange={handleUpload} />
            <p>{uploadResult}</p>
          </div>
          <GuidePanel />
        </section>

        <HistoryPanel history={history} clearHistory={() => setHistory([])} />
      </main>
    </div>
  )
}
