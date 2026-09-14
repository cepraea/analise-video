import { useEffect, useRef, useState } from 'react'

import { APP_NAME, APP_STATUS } from './appMeta'

type LocalMedia = {
  media_path: string
  url: string
}

type Marking = {
  mediaPath: string
  startMs: number
  endMs: number | null
  savedId: number | null
}

type SavedInterval = {
  id: number
  media_path: string
  start_ms: number
  end_ms: number
  created_at: string
}

function formatTime(seconds: number): string {
  if (!Number.isFinite(seconds)) return '00:00.0'
  const minutes = Math.floor(seconds / 60)
  const remaining = (seconds % 60).toFixed(1).padStart(4, '0')
  return `${String(minutes).padStart(2, '0')}:${remaining}`
}

function formatMilliseconds(milliseconds: number): string {
  const minutes = Math.floor(milliseconds / 60_000)
  const seconds = Math.floor((milliseconds % 60_000) / 1_000)
  const remainder = milliseconds % 1_000
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}.${String(remainder).padStart(3, '0')}`
}

export function App() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const reviewStoppingRef = useRef(false)
  const reviewReadyRef = useRef(false)
  const [media, setMedia] = useState<LocalMedia[]>([])
  const [selectedPath, setSelectedPath] = useState('')
  const [refreshKey, setRefreshKey] = useState(0)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')
  const [videoError, setVideoError] = useState('')
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(Number.NaN)
  const [playing, setPlaying] = useState(false)
  const [marking, setMarking] = useState<Marking | null>(null)
  const [markError, setMarkError] = useState('')
  const [saving, setSaving] = useState(false)
  const [intervals, setIntervals] = useState<SavedInterval[]>([])
  const [intervalsLoading, setIntervalsLoading] = useState(true)
  const [intervalsError, setIntervalsError] = useState('')
  const [reviewing, setReviewing] = useState<SavedInterval | null>(null)
  const [reviewStatus, setReviewStatus] = useState('')

  useEffect(() => {
    const controller = new AbortController()
    setLoading(true)
    setLoadError('')

    async function loadMedia() {
      try {
        const response = await fetch('/spike/media', { signal: controller.signal })
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        const available = (await response.json()) as LocalMedia[]
        setMedia(available)
        setSelectedPath((previous) =>
          available.some((item) => item.media_path === previous)
            ? previous
            : (available[0]?.media_path ?? ''),
        )
      } catch {
        if (!controller.signal.aborted) {
          setLoadError('Não foi possível listar os MP4s locais. Verifique o backend.')
        }
      } finally {
        if (!controller.signal.aborted) setLoading(false)
      }
    }

    void loadMedia()
    return () => controller.abort()
  }, [refreshKey])

  useEffect(() => {
    const controller = new AbortController()

    async function loadIntervals() {
      try {
        const response = await fetch('/spike/intervals', { signal: controller.signal })
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        setIntervals((await response.json()) as SavedInterval[])
      } catch {
        if (!controller.signal.aborted) {
          setIntervalsError('Não foi possível carregar os intervalos salvos.')
        }
      } finally {
        if (!controller.signal.aborted) setIntervalsLoading(false)
      }
    }

    void loadIntervals()
    return () => controller.abort()
  }, [])

  useEffect(() => {
    if (!reviewing || selectedPath !== reviewing.media_path || !Number.isFinite(duration)) return
    const video = videoRef.current
    if (!video) return

    const start = reviewing.start_ms / 1_000
    const end = reviewing.end_ms / 1_000
    if (start < 0 || start >= end || end > duration) {
      setReviewStatus('Os tempos salvos estão fora da duração deste MP4.')
      setReviewing(null)
      return
    }

    let cancelled = false
    const playFromStart = () => {
      if (cancelled) return
      void video.play().then(() => {
        if (!cancelled) {
          reviewReadyRef.current = true
          setReviewStatus(`Revendo intervalo ${String(reviewing.id).padStart(3, '0')}.`)
        }
      }).catch(() => {
        if (!cancelled) {
          reviewReadyRef.current = false
          setReviewStatus('Não foi possível reproduzir o intervalo salvo.')
          setReviewing(null)
        }
      })
    }

    if (Math.abs(video.currentTime - start) < 0.001 && !video.seeking) {
      playFromStart()
    } else {
      video.addEventListener('seeked', playFromStart, { once: true })
      video.currentTime = start
    }

    return () => {
      cancelled = true
      video.removeEventListener('seeked', playFromStart)
    }
  }, [reviewing, selectedPath, duration])

  const selectedMedia = media.find((item) => item.media_path === selectedPath)
  const activeMarking = marking?.mediaPath === selectedPath ? marking : null

  function selectMedia(path: string) {
    setSelectedPath(path)
    setCurrentTime(0)
    setDuration(Number.NaN)
    setPlaying(false)
    setVideoError('')
    setMarking(null)
    setMarkError('')
    setReviewing(null)
    reviewReadyRef.current = false
    setReviewStatus('')
  }

  function seekBy(seconds: number) {
    const video = videoRef.current
    if (!video || !Number.isFinite(video.duration)) return
    video.currentTime = Math.max(0, Math.min(video.currentTime + seconds, video.duration))
    setCurrentTime(video.currentTime)
  }

  async function togglePlayback() {
    const video = videoRef.current
    if (!video) return
    if (!video.paused) {
      video.pause()
      return
    }
    try {
      await video.play()
      setVideoError('')
    } catch {
      setVideoError('Não foi possível iniciar a reprodução deste MP4.')
    }
  }

  function captureCurrentMs(): number | null {
    const time = videoRef.current?.currentTime
    if (time === undefined || !Number.isFinite(time)) {
      setMarkError('O tempo do vídeo ainda não está disponível.')
      return null
    }
    return Math.round(time * 1_000)
  }

  function startMarking() {
    if (!selectedMedia || saving) return
    const startMs = captureCurrentMs()
    if (startMs === null) return
    setMarking({ mediaPath: selectedMedia.media_path, startMs, endMs: null, savedId: null })
    setMarkError('')
    setReviewing(null)
    reviewReadyRef.current = false
    setReviewStatus('')
  }

  async function endMarking() {
    if (!activeMarking || saving || activeMarking.savedId !== null) return
    const endMs = captureCurrentMs()
    if (endMs === null) return
    if (endMs <= activeMarking.startMs) {
      setMarking({ ...activeMarking, endMs: null, savedId: null })
      setMarkError('O fim deve ser posterior ao início. Avance o vídeo e tente novamente.')
      return
    }
    setMarking({ ...activeMarking, endMs, savedId: null })
    setMarkError('')
    setSaving(true)
    try {
      const response = await fetch('/spike/intervals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          media_path: activeMarking.mediaPath,
          start_ms: activeMarking.startMs,
          end_ms: endMs,
        }),
      })
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const saved = (await response.json()) as SavedInterval
      setMarking({ ...activeMarking, endMs, savedId: saved.id })
      setIntervals((previous) => [...previous, saved])
    } catch {
      setMarkError('Intervalo válido, mas não foi possível salvá-lo. Tente encerrar novamente.')
    } finally {
      setSaving(false)
    }
  }

  function reviewInterval(interval: SavedInterval) {
    if (!media.some((item) => item.media_path === interval.media_path)) {
      setReviewStatus('O MP4 deste intervalo não está disponível no diretório local.')
      return
    }
    videoRef.current?.pause()
    reviewStoppingRef.current = false
    reviewReadyRef.current = false
    if (selectedPath !== interval.media_path) selectMedia(interval.media_path)
    setReviewing({ ...interval })
    setReviewStatus('Buscando o início do intervalo…')
  }

  function updateVideoTime(video: HTMLVideoElement) {
    setCurrentTime(video.currentTime)
    if (reviewing && reviewReadyRef.current && !reviewStoppingRef.current && video.currentTime >= reviewing.end_ms / 1_000) {
      reviewStoppingRef.current = true
      reviewReadyRef.current = false
      video.pause()
      video.currentTime = reviewing.end_ms / 1_000
      setCurrentTime(video.currentTime)
      setReviewStatus(`Revisão do intervalo ${String(reviewing.id).padStart(3, '0')} concluída.`)
      setReviewing(null)
    }
  }

  return (
    <main style={{ maxWidth: 960, margin: '0 auto', padding: '1.5rem', fontFamily: 'sans-serif' }}>
      <h1>{APP_NAME}</h1>
      <p>{APP_STATUS}</p>
      <section aria-labelledby="local-video-heading">
        <h2 id="local-video-heading">Vídeo local</h2>
        <p>Selecione um MP4 em <code>.local/media</code> para testar a reprodução.</p>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <label htmlFor="media-select">Arquivo</label>
          <select
            id="media-select"
            value={selectedPath}
            onChange={(event) => selectMedia(event.target.value)}
            disabled={loading || saving || media.length === 0}
          >
            {media.length === 0 && <option value="">Nenhum MP4 disponível</option>}
            {media.map((item) => (
              <option key={item.media_path} value={item.media_path}>
                {item.media_path}
              </option>
            ))}
          </select>
          <button type="button" onClick={() => setRefreshKey((value) => value + 1)} disabled={saving}>
            Atualizar lista
          </button>
        </div>
        {loading && <p>Buscando vídeos locais…</p>}
        {loadError && <p role="alert">{loadError}</p>}
        {!loading && !loadError && media.length === 0 && (
          <p>Nenhum MP4 encontrado no diretório local.</p>
        )}
        {selectedMedia && (
          <>
            <video
              key={selectedMedia.media_path}
              ref={videoRef}
              src={selectedMedia.url}
              controls
              playsInline
              preload="metadata"
              aria-label={`Reprodutor de ${selectedMedia.media_path}`}
              style={{ display: 'block', width: '100%', maxHeight: '50vh', marginTop: '1rem', background: '#111' }}
              onLoadedMetadata={(event) => {
                setDuration(event.currentTarget.duration)
                setCurrentTime(event.currentTarget.currentTime)
                setVideoError('')
              }}
              onTimeUpdate={(event) => updateVideoTime(event.currentTarget)}
              onSeeked={(event) => updateVideoTime(event.currentTarget)}
              onPlay={() => setPlaying(true)}
              onPause={() => setPlaying(false)}
              onError={() => setVideoError('Não foi possível reproduzir este MP4.')}
            />
            {videoError && <p role="alert">{videoError}</p>}
            <p aria-live="off">
              Tempo corrente: <output data-testid="current-time">{formatTime(currentTime)}</output>
              {' / '}{Number.isFinite(duration) ? formatTime(duration) : 'carregando…'}
              {' · '}{playing ? 'Reproduzindo' : 'Pausado'}
            </p>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button type="button" onClick={() => void togglePlayback()} disabled={!Number.isFinite(duration)}>
                {playing ? 'Pausar' : 'Reproduzir'}
              </button>
              <button type="button" onClick={() => seekBy(-10)} disabled={!Number.isFinite(duration)}>
                Voltar 10 s
              </button>
              <button type="button" onClick={() => seekBy(10)} disabled={!Number.isFinite(duration)}>
                Avançar 10 s
              </button>
            </div>
            <section aria-labelledby="marking-heading">
              <h2 id="marking-heading">Marcação de lance</h2>
              <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                <button type="button" onClick={startMarking} disabled={!Number.isFinite(duration) || saving}>
                  INICIAR LANCE
                </button>
                <button type="button" onClick={() => void endMarking()} disabled={!activeMarking || saving || activeMarking.savedId !== null}>
                  ENCERRAR LANCE
                </button>
              </div>
              <p>
                Início: {activeMarking ? `${formatMilliseconds(activeMarking.startMs)} (${activeMarking.startMs} ms)` : 'não marcado'}
                <br />
                Fim: {activeMarking && activeMarking.endMs !== null
                  ? `${formatMilliseconds(activeMarking.endMs)} (${activeMarking.endMs} ms)`
                  : 'não marcado'}
              </p>
              {markError && <p role="alert">{markError}</p>}
              {saving && <p role="status">Salvando intervalo…</p>}
              {activeMarking && activeMarking.endMs !== null && !markError && (
                <p>
                  {activeMarking.savedId !== null
                    ? `Intervalo #${activeMarking.savedId} salvo no SQLite, sem criar outro MP4.`
                    : 'Intervalo válido, aguardando salvamento.'}
                </p>
              )}
            </section>
          </>
        )}
      </section>
      <section aria-labelledby="review-heading">
        <h2 id="review-heading">Revisão</h2>
        {intervalsLoading && <p>Carregando intervalos salvos…</p>}
        {intervalsError && <p role="alert">{intervalsError}</p>}
        {!intervalsLoading && intervals.length === 0 && !intervalsError && <p>Nenhum intervalo salvo.</p>}
        {intervals.length > 0 && (
          <ul>
            {intervals.map((interval) => (
              <li key={interval.id} style={{ marginBottom: '0.75rem' }}>
                Intervalo {String(interval.id).padStart(3, '0')} — {interval.media_path}
                {' · '}{formatMilliseconds(interval.start_ms)} → {formatMilliseconds(interval.end_ms)}
                {' '}
                <button
                  type="button"
                  onClick={() => reviewInterval(interval)}
                  disabled={!media.some((item) => item.media_path === interval.media_path)}
                >
                  REVER
                </button>
              </li>
            ))}
          </ul>
        )}
        {reviewStatus && <p role="status">{reviewStatus}</p>}
      </section>
    </main>
  )
}
