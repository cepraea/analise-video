import { useEffect, useRef, useState } from 'react'

import { APP_NAME, APP_STATUS } from './appMeta'

const PLAYBACK_RATES = [
  { value: 0.25, label: '0,25x' },
  { value: 0.5, label: '0,5x' },
  { value: 1, label: '1x' },
  { value: 1.5, label: '1,5x' },
  { value: 2, label: '2x' },
]

type LocalMedia = {
  media_path: string
  url: string
}

type Marking = {
  mediaPath: string
  startMs: number
  endMs: number | null
}

type SavedInterval = {
  id: number
  media_path: string
  start_ms: number
  end_ms: number
  created_at: string
}

type ReviewTarget = Pick<SavedInterval, 'media_path' | 'start_ms' | 'end_ms'> & {
  id: number | null
}

type EditDraft = Pick<SavedInterval, 'id' | 'media_path' | 'start_ms' | 'end_ms'>

const EDIT_STEPS = [10_000, 1_000, 100]

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
  const savingRef = useRef(false)
  const [media, setMedia] = useState<LocalMedia[]>([])
  const [selectedPath, setSelectedPath] = useState('')
  const [refreshKey, setRefreshKey] = useState(0)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')
  const [videoError, setVideoError] = useState('')
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(Number.NaN)
  const [playing, setPlaying] = useState(false)
  const [playbackRate, setPlaybackRate] = useState(1)
  const [marking, setMarking] = useState<Marking | null>(null)
  const [markError, setMarkError] = useState('')
  const [lastSavedId, setLastSavedId] = useState<number | null>(null)
  const [saving, setSaving] = useState(false)
  const [intervals, setIntervals] = useState<SavedInterval[]>([])
  const [selectedIntervalId, setSelectedIntervalId] = useState<number | null>(null)
  const [intervalsLoading, setIntervalsLoading] = useState(true)
  const [intervalsError, setIntervalsError] = useState('')
  const [reviewing, setReviewing] = useState<ReviewTarget | null>(null)
  const [reviewStatus, setReviewStatus] = useState('')
  const [editing, setEditing] = useState<EditDraft | null>(null)
  const [editError, setEditError] = useState('')
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const [deletionReason, setDeletionReason] = useState('')
  const [mutationBusy, setMutationBusy] = useState(false)
  const [mutationStatus, setMutationStatus] = useState('')

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
      setReviewStatus('Os tempos da revisão estão fora da duração deste MP4.')
      setReviewing(null)
      return
    }

    let cancelled = false
    const playFromStart = () => {
      if (cancelled) return
      void video.play().then(() => {
        if (!cancelled) {
          reviewReadyRef.current = true
          setReviewStatus(reviewing.id === null
            ? 'Revendo prévia do lance.'
            : `Revendo intervalo ${String(reviewing.id).padStart(3, '0')}.`)
        }
      }).catch(() => {
        if (!cancelled) {
          reviewReadyRef.current = false
          setReviewStatus('Não foi possível reproduzir este intervalo.')
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

  useEffect(() => {
    function handleKeyboard(event: KeyboardEvent) {
      if (event.defaultPrevented || event.isComposing) return
      if (editing || deletingId !== null) {
        if (event.key === 'Escape' && !savingRef.current) {
          event.preventDefault()
          setEditing(null)
          setDeletingId(null)
          setEditError('')
        }
        return
      }
      if (event.target instanceof Element && event.target.closest('input, textarea, select, [contenteditable]')) return
      if (event.composedPath().some((target) => target instanceof HTMLMediaElement)) return

      if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
        if (event.altKey || event.metaKey || (event.ctrlKey && event.shiftKey)) return
        const stepMs = event.ctrlKey ? 10_000 : event.shiftKey ? 100 : 1_000
        if (seekByMs(event.key === 'ArrowLeft' ? -stepMs : stepMs)) event.preventDefault()
        return
      }

      if (event.ctrlKey || event.altKey || event.metaKey || event.shiftKey || event.repeat) return

      if (event.key === 'Escape') {
        if (savingRef.current || document.fullscreenElement) return
        if (reviewing) {
          event.preventDefault()
          stopReview()
        } else if (activeMarking) {
          event.preventDefault()
          discardMarking()
        } else if (selectedIntervalId !== null) {
          event.preventDefault()
          setSelectedIntervalId(null)
          setReviewStatus('')
        }
        return
      }

      const focusedButton = event.target instanceof Element &&
        event.target.closest('button, a, [role="button"], [role="link"]')
      if (event.key === ' ' || event.key === 'Spacebar') {
        if (focusedButton || !Number.isFinite(videoRef.current?.duration)) return
        event.preventDefault()
        void togglePlayback()
        return
      }
      if (event.key === 'Enter') {
        if (focusedButton || !activeMarking || activeMarking.endMs === null || reviewing || savingRef.current) return
        event.preventDefault()
        void confirmAndSave()
        return
      }

      const command = event.key.toLowerCase()
      if (command === 'i') {
        if (!selectedMedia || activeMarking || reviewing || savingRef.current || !Number.isFinite(videoRef.current?.duration)) return
        event.preventDefault()
        startMarking()
      } else if (command === 'o') {
        if (!activeMarking || activeMarking.endMs !== null || savingRef.current) return
        event.preventDefault()
        endMarking()
      } else if (command === 'r') {
        if (reviewing || savingRef.current) return
        if (activeMarking) {
          if (activeMarking.endMs === null) return
          event.preventDefault()
          reviewDraft()
        } else {
          const selected = intervals.find((interval) => interval.id === selectedIntervalId)
          event.preventDefault()
          if (selected) reviewInterval(selected)
          else setReviewStatus('Selecione um intervalo salvo para rever com R.')
        }
      }
    }

    window.addEventListener('keydown', handleKeyboard, true)
    return () => window.removeEventListener('keydown', handleKeyboard, true)
  }, [reviewing, activeMarking, intervals, selectedIntervalId, selectedMedia, editing, deletingId])

  function selectMedia(path: string) {
    setSelectedPath(path)
    setCurrentTime(0)
    setDuration(Number.NaN)
    setPlaying(false)
    setVideoError('')
    setMarking(null)
    setMarkError('')
    setLastSavedId(null)
    setReviewing(null)
    reviewReadyRef.current = false
    setReviewStatus('')
    setEditing(null)
    setDeletingId(null)
    setEditError('')
  }

  function seekByMs(deltaMs: number): boolean {
    const video = videoRef.current
    if (!video || !Number.isFinite(video.duration) || !Number.isFinite(video.currentTime)) return false
    const targetMs = Math.round(video.currentTime * 1_000) + deltaMs
    const targetSeconds = Math.max(0, Math.min(targetMs / 1_000, video.duration))
    video.currentTime = targetSeconds
    setCurrentTime(targetSeconds)
    return true
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
    if (!selectedMedia || marking || reviewing || savingRef.current) return
    const startMs = captureCurrentMs()
    if (startMs === null) return
    setMarking({ mediaPath: selectedMedia.media_path, startMs, endMs: null })
    setMarkError('')
    setLastSavedId(null)
    setReviewing(null)
    reviewReadyRef.current = false
    setReviewStatus('')
  }

  function endMarking() {
    if (!activeMarking || activeMarking.endMs !== null || savingRef.current) return
    const endMs = captureCurrentMs()
    if (endMs === null) return
    if (endMs <= activeMarking.startMs) {
      setMarkError('O fim deve ser posterior ao início. Avance o vídeo e tente novamente.')
      return
    }
    setMarking({ ...activeMarking, endMs })
    setMarkError('')
  }

  async function confirmAndSave() {
    if (!activeMarking || activeMarking.endMs === null || savingRef.current || reviewing) return
    const interval = activeMarking
    savingRef.current = true
    setSaving(true)
    setMarkError('')
    try {
      const response = await fetch('/spike/intervals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          media_path: interval.mediaPath,
          start_ms: interval.startMs,
          end_ms: interval.endMs,
        }),
      })
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const saved = (await response.json()) as SavedInterval
      setMarking(null)
      setLastSavedId(saved.id)
      setSelectedIntervalId(saved.id)
      setIntervals((previous) => [...previous, saved])
    } catch {
      setMarkError('Não foi possível salvar a prévia. Confirme novamente para tentar outra vez.')
    } finally {
      savingRef.current = false
      setSaving(false)
    }
  }

  function discardMarking() {
    if (!activeMarking || savingRef.current || reviewing) return
    setMarking(null)
    setMarkError('')
    setLastSavedId(null)
    setReviewStatus('')
  }

  function reviewDraft() {
    if (!activeMarking || activeMarking.endMs === null || savingRef.current) return
    reviewInterval({
      id: null,
      media_path: activeMarking.mediaPath,
      start_ms: activeMarking.startMs,
      end_ms: activeMarking.endMs,
    })
  }

  function stopReview() {
    if (!reviewing) return
    videoRef.current?.pause()
    reviewStoppingRef.current = true
    reviewReadyRef.current = false
    setReviewing(null)
    setReviewStatus(reviewing.id === null
      ? 'Revisão da prévia interrompida.'
      : 'Revisão do intervalo interrompida.')
  }

  function reviewInterval(interval: ReviewTarget) {
    if (!media.some((item) => item.media_path === interval.media_path)) {
      setReviewStatus('O MP4 deste intervalo não está disponível no diretório local.')
      return
    }
    videoRef.current?.pause()
    reviewStoppingRef.current = false
    reviewReadyRef.current = false
    if (interval.id !== null) setSelectedIntervalId(interval.id)
    if (selectedPath !== interval.media_path) selectMedia(interval.media_path)
    setReviewing({ ...interval })
    setReviewStatus('Buscando o início do intervalo…')
  }

  function beginEditing(interval: SavedInterval) {
    if (activeMarking || reviewing || savingRef.current) return
    if (!media.some((item) => item.media_path === interval.media_path)) {
      setMutationStatus('O MP4 deste intervalo não está disponível para validar a edição.')
      return
    }
    if (selectedPath !== interval.media_path) selectMedia(interval.media_path)
    setSelectedIntervalId(interval.id)
    setEditing({
      id: interval.id,
      media_path: interval.media_path,
      start_ms: interval.start_ms,
      end_ms: interval.end_ms,
    })
    setDeletingId(null)
    setEditError('')
    setMutationStatus('')
  }

  function adjustEditBoundary(edge: 'start_ms' | 'end_ms', deltaMs: number) {
    if (!editing || savingRef.current) return
    const limitMs = Number.isFinite(duration) && selectedPath === editing.media_path
      ? Math.round(duration * 1_000) : null
    const nextMs = editing[edge] + deltaMs
    if (nextMs < 0 || (limitMs !== null && nextMs > limitMs)) {
      setEditError('O ajuste deve ficar entre zero e a duração do MP4.')
      return
    }
    setEditing({ ...editing, [edge]: nextMs })
    setEditError('')
  }

  async function saveEdit() {
    if (!editing || savingRef.current) return
    const draft = editing
    const limitMs = Number.isFinite(duration) && selectedPath === draft.media_path
      ? Math.round(duration * 1_000) : null
    if (limitMs === null) {
      setEditError('Aguarde a duração do MP4 para validar a edição.')
      return
    }
    if (draft.start_ms < 0 || draft.end_ms > limitMs || draft.start_ms >= draft.end_ms) {
      setEditError('O início deve ser menor que o fim e ambos devem estar dentro do MP4.')
      return
    }
    savingRef.current = true
    setMutationBusy(true)
    setEditError('')
    try {
      const response = await fetch(`/spike/intervals/${draft.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ start_ms: draft.start_ms, end_ms: draft.end_ms }),
      })
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const updated = (await response.json()) as SavedInterval
      setIntervals((previous) => previous.map((item) => item.id === updated.id ? updated : item))
      setEditing(null)
      setMutationStatus(`Intervalo ${String(updated.id).padStart(3, '0')} corrigido no mesmo ID.`)
    } catch {
      setEditError('Não foi possível salvar a correção. Os valores editados foram preservados.')
    } finally {
      savingRef.current = false
      setMutationBusy(false)
    }
  }

  async function confirmDeletion() {
    if (deletingId === null || savingRef.current) return
    const reason = deletionReason.trim()
    if (!reason) {
      setEditError('Informe o motivo da exclusão.')
      return
    }
    const intervalId = deletingId
    savingRef.current = true
    setMutationBusy(true)
    setEditError('')
    try {
      const response = await fetch(`/spike/intervals/${intervalId}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason }),
      })
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      setIntervals((previous) => previous.filter((item) => item.id !== intervalId))
      if (selectedIntervalId === intervalId) setSelectedIntervalId(null)
      setDeletingId(null)
      setDeletionReason('')
      setMutationStatus(`Intervalo ${String(intervalId).padStart(3, '0')} excluído logicamente.`)
    } catch {
      setEditError('Não foi possível excluir o intervalo. Tente novamente.')
    } finally {
      savingRef.current = false
      setMutationBusy(false)
    }
  }

  function updateVideoTime(video: HTMLVideoElement) {
    setCurrentTime(video.currentTime)
    if (reviewing && reviewReadyRef.current && !reviewStoppingRef.current && video.currentTime >= reviewing.end_ms / 1_000) {
      reviewStoppingRef.current = true
      reviewReadyRef.current = false
      video.pause()
      video.currentTime = reviewing.end_ms / 1_000
      setCurrentTime(video.currentTime)
      setReviewStatus(reviewing.id === null
        ? 'Revisão da prévia concluída.'
        : `Revisão do intervalo ${String(reviewing.id).padStart(3, '0')} concluída.`)
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
            disabled={loading || saving || mutationBusy || Boolean(editing) || deletingId !== null || media.length === 0}
          >
            {media.length === 0 && <option value="">Nenhum MP4 disponível</option>}
            {media.map((item) => (
              <option key={item.media_path} value={item.media_path}>
                {item.media_path}
              </option>
            ))}
          </select>
          <button type="button" onClick={() => setRefreshKey((value) => value + 1)} disabled={saving || mutationBusy || Boolean(editing) || deletingId !== null}>
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
                event.currentTarget.playbackRate = playbackRate
                setDuration(event.currentTarget.duration)
                setCurrentTime(event.currentTarget.currentTime)
                setVideoError('')
              }}
              onTimeUpdate={(event) => updateVideoTime(event.currentTarget)}
              onSeeked={(event) => updateVideoTime(event.currentTarget)}
              onPlay={() => setPlaying(true)}
              onPause={() => setPlaying(false)}
              onRateChange={(event) => {
                const rate = event.currentTarget.playbackRate
                if (PLAYBACK_RATES.some((option) => option.value === rate)) setPlaybackRate(rate)
                else event.currentTarget.playbackRate = playbackRate
              }}
              onError={() => setVideoError('Não foi possível reproduzir este MP4.')}
            />
            {videoError && <p role="alert">{videoError}</p>}
            <p aria-live="off">
              Tempo corrente: <output data-testid="current-time">{formatTime(currentTime)}</output>
              {' / '}{Number.isFinite(duration) ? formatTime(duration) : 'carregando…'}
              {' · '}{playing ? 'Reproduzindo' : 'Pausado'}
            </p>
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
              <button type="button" onClick={() => void togglePlayback()} disabled={!Number.isFinite(duration)}>
                {playing ? 'Pausar' : 'Reproduzir'}
              </button>
              <button type="button" onClick={() => seekByMs(-10_000)} disabled={!Number.isFinite(duration)}>
                Voltar 10 s
              </button>
              <button type="button" onClick={() => seekByMs(10_000)} disabled={!Number.isFinite(duration)}>
                Avançar 10 s
              </button>
              <label htmlFor="playback-rate">Velocidade</label>
              <select
                id="playback-rate"
                value={playbackRate}
                onChange={(event) => {
                  const rate = Number(event.target.value)
                  setPlaybackRate(rate)
                  if (videoRef.current) videoRef.current.playbackRate = rate
                }}
                disabled={!Number.isFinite(duration)}
              >
                {PLAYBACK_RATES.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </div>
            <div tabIndex={0} role="group" aria-label="Área de atalhos do player" style={{ outlineOffset: '4px' }}>
              <p>Busca: ←/→ ±1 s · Shift + ←/→ ±0,1 s · Ctrl + ←/→ ±10 s.</p>
              <p>Operação: Espaço reproduz/pausa · I marca início · O marca fim · R revê · Enter confirma e salva · Esc sai ou descarta.</p>
              <p>Use Tab para focar esta área e operar sem mouse. Em botões, Espaço e Enter ativam o próprio botão; campos e controles nativos do vídeo usam suas teclas normalmente.</p>
            </div>
            <section aria-labelledby="marking-heading">
              <h2 id="marking-heading">Marcação de lance</h2>
              <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                <button type="button" onClick={startMarking} disabled={!Number.isFinite(duration) || Boolean(activeMarking) || reviewing !== null || saving || Boolean(editing) || deletingId !== null || mutationBusy}>
                  INICIAR LANCE
                </button>
                <button type="button" onClick={endMarking} disabled={!activeMarking || activeMarking.endMs !== null || saving}>
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
              {activeMarking && activeMarking.endMs !== null && (
                <>
                  <p>Prévia válida: {formatMilliseconds(activeMarking.startMs)} → {formatMilliseconds(activeMarking.endMs)}. Revise, descarte ou confirme para salvar.</p>
                  <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                    <button
                      type="button"
                      onClick={reviewing?.id === null ? stopReview : reviewDraft}
                      disabled={saving}
                    >
                      {reviewing?.id === null ? 'SAIR DA REVISÃO' : 'REVER'}
                    </button>
                    <button type="button" onClick={discardMarking} disabled={saving || reviewing !== null}>
                      DESCARTAR
                    </button>
                    <button type="button" onClick={() => void confirmAndSave()} disabled={saving || reviewing !== null}>
                      CONFIRMAR E SALVAR
                    </button>
                  </div>
                </>
              )}
              {activeMarking && activeMarking.endMs === null && (
                <button type="button" onClick={discardMarking} disabled={saving || reviewing !== null}>DESCARTAR</button>
              )}
              {lastSavedId !== null && <p>Intervalo #{lastSavedId} salvo no SQLite, sem criar outro MP4.</p>}
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
          <>
            <p>Use Tab até o intervalo desejado para selecioná-lo; depois pressione R para rever.</p>
            <ul>
            {intervals.map((interval) => (
              <li key={interval.id} style={{ marginBottom: '0.75rem' }}>
                Intervalo {String(interval.id).padStart(3, '0')} — {interval.media_path}
                {' · '}{formatMilliseconds(interval.start_ms)} → {formatMilliseconds(interval.end_ms)}
                {' '}
                <button
                  type="button"
                  aria-pressed={selectedIntervalId === interval.id}
                  onFocus={() => setSelectedIntervalId(interval.id)}
                  onClick={() => setSelectedIntervalId(interval.id)}
                  disabled={Boolean(activeMarking) || saving || reviewing !== null || mutationBusy || Boolean(editing) || deletingId !== null}
                >
                  {selectedIntervalId === interval.id ? 'SELECIONADO PARA R' : 'SELECIONAR PARA R'}
                </button>
                {' '}
                <button
                  type="button"
                  onFocus={() => setSelectedIntervalId(interval.id)}
                  onClick={() => reviewInterval(interval)}
                  disabled={Boolean(activeMarking) || saving || mutationBusy || Boolean(editing) || deletingId !== null || !media.some((item) => item.media_path === interval.media_path)}
                >
                  REVER
                </button>
                {' '}
                <button
                  type="button"
                  onFocus={() => setSelectedIntervalId(interval.id)}
                  onClick={() => beginEditing(interval)}
                  disabled={Boolean(activeMarking) || saving || mutationBusy || reviewing !== null || Boolean(editing) || deletingId !== null || !media.some((item) => item.media_path === interval.media_path)}
                >
                  EDITAR
                </button>
                {' '}
                <button
                  type="button"
                  onFocus={() => setSelectedIntervalId(interval.id)}
                  onClick={() => {
                    setEditing(null)
                    setDeletingId(interval.id)
                    setDeletionReason('')
                    setEditError('')
                    setMutationStatus('')
                  }}
                  disabled={Boolean(activeMarking) || saving || mutationBusy || reviewing !== null || Boolean(editing)}
                >
                  EXCLUIR
                </button>
              </li>
            ))}
            </ul>
          </>
        )}
        {editing && (() => {
          const original = intervals.find((interval) => interval.id === editing.id)
          return (
            <section aria-labelledby="edit-heading">
              <h3 id="edit-heading">EDITAR intervalo {String(editing.id).padStart(3, '0')}</h3>
              <p>Tempos atuais: {original && `${formatMilliseconds(original.start_ms)} → ${formatMilliseconds(original.end_ms)}`}</p>
              <p>Novos tempos: {formatMilliseconds(editing.start_ms)} → {formatMilliseconds(editing.end_ms)}</p>
              {(['start_ms', 'end_ms'] as const).map((edge) => (
                <div key={edge}>
                  <p>{edge === 'start_ms' ? 'Início' : 'Fim'}: {formatMilliseconds(editing[edge])}</p>
                  {EDIT_STEPS.map((stepMs) => [(-stepMs), stepMs].map((deltaMs) => (
                    <button
                      key={`${edge}-${deltaMs}`}
                      type="button"
                      onClick={() => adjustEditBoundary(edge, deltaMs)}
                      disabled={mutationBusy || !Number.isFinite(duration)}
                      aria-label={`${edge === 'start_ms' ? 'Início' : 'Fim'} ${deltaMs < 0 ? '−' : '+'}${String(Math.abs(deltaMs) / 1_000).replace('.', ',')} s`}
                    >
                      {deltaMs < 0 ? '−' : '+'}{String(Math.abs(deltaMs) / 1_000).replace('.', ',')} s
                    </button>
                  )))}
                </div>
              ))}
              <button type="button" onClick={() => void saveEdit()} disabled={mutationBusy || !Number.isFinite(duration)}>SALVAR ALTERAÇÕES</button>
              {' '}
              <button type="button" onClick={() => { setEditing(null); setEditError('') }} disabled={mutationBusy}>CANCELAR EDIÇÃO</button>
            </section>
          )
        })()}
        {deletingId !== null && (
          <section aria-labelledby="delete-heading">
            <h3 id="delete-heading">EXCLUIR intervalo {String(deletingId).padStart(3, '0')}</h3>
            <label htmlFor="deletion-reason">Motivo da exclusão</label>{' '}
            <input id="deletion-reason" value={deletionReason} onChange={(event) => setDeletionReason(event.target.value)} />
            {' '}
            <button type="button" onClick={() => void confirmDeletion()} disabled={mutationBusy}>CONFIRMAR EXCLUSÃO</button>
            {' '}
            <button type="button" onClick={() => { setDeletingId(null); setEditError('') }} disabled={mutationBusy}>CANCELAR EXCLUSÃO</button>
          </section>
        )}
        {editError && <p role="alert">{editError}</p>}
        {mutationStatus && <p role="status">{mutationStatus}</p>}
        {reviewStatus && <p role="status">{reviewStatus}</p>}
      </section>
    </main>
  )
}
