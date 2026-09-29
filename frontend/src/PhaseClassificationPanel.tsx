import { useEffect, useMemo, useState } from 'react'

import './phase-classification.css'

type TemporalReference = {
  id: string
  video_source_id: string
  media_path: string
  start_ms: number
  end_ms: number
}

type CanonicalLance = {
  id: string
  game_id: string
  temporal_references: TemporalReference[]
}

type SegmentDraft = {
  localId: number
  team_role: 'POSSESSION_TEAM' | 'ANALYZED_TEAM'
  phase: string
  video_source_id: string
  start_ms: number
  end_ms: number
}

type SavedSegment = {
  id: string
  team_role: SegmentDraft['team_role']
  team_name: string
  phase: string
  temporal_references: Array<Pick<
    TemporalReference,
    'id' | 'video_source_id' | 'start_ms' | 'end_ms'
  >>
}

type SavedClassification = {
  lance_id: string
  possession_team: string
  analyzed_team: string
  phase_segments: SavedSegment[]
}

const ROLE_LABELS = {
  POSSESSION_TEAM: 'Equipe com posse',
  ANALYZED_TEAM: 'Equipe analisada',
}

function formatMilliseconds(milliseconds: number): string {
  const minutes = Math.floor(milliseconds / 60_000)
  const seconds = Math.floor((milliseconds % 60_000) / 1_000)
  const remainder = milliseconds % 1_000
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}.${String(remainder).padStart(3, '0')}`
}

function segmentFrom(reference: TemporalReference, localId: number): SegmentDraft {
  return {
    localId,
    team_role: 'POSSESSION_TEAM',
    phase: 'Transição Ofensiva',
    video_source_id: reference.video_source_id,
    start_ms: reference.start_ms,
    end_ms: reference.end_ms,
  }
}

async function errorMessage(response: Response, fallback: string): Promise<string> {
  try {
    const body = await response.json() as { detail?: string }
    return body.detail ?? fallback
  } catch {
    return fallback
  }
}

export function PhaseClassificationPanel() {
  const [lances, setLances] = useState<CanonicalLance[]>([])
  const [phaseValues, setPhaseValues] = useState<string[]>([])
  const [selectedLanceId, setSelectedLanceId] = useState('')
  const [possessionTeam, setPossessionTeam] = useState('')
  const [analyzedTeam, setAnalyzedTeam] = useState('')
  const [segments, setSegments] = useState<SegmentDraft[]>([])
  const [saved, setSaved] = useState<SavedClassification | null>(null)
  const [loading, setLoading] = useState(true)
  const [loadingClassification, setLoadingClassification] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [status, setStatus] = useState('')

  const selectedLance = useMemo(
    () => lances.find((lance) => lance.id === selectedLanceId),
    [lances, selectedLanceId],
  )

  useEffect(() => {
    const controller = new AbortController()
    async function loadCatalog() {
      setLoading(true)
      setError('')
      try {
        const [lancesResponse, phasesResponse] = await Promise.all([
          fetch('/catalog/lances', { signal: controller.signal }),
          fetch('/catalog/phase-values', { signal: controller.signal }),
        ])
        if (!lancesResponse.ok || !phasesResponse.ok) throw new Error('catalog')
        const availableLances = await lancesResponse.json() as CanonicalLance[]
        const phases = await phasesResponse.json() as { minimum_values: string[] }
        setLances(availableLances)
        setPhaseValues(phases.minimum_values)
        setSelectedLanceId((current) =>
          availableLances.some((lance) => lance.id === current)
            ? current
            : (availableLances[0]?.id ?? ''),
        )
      } catch {
        if (!controller.signal.aborted) {
          setError('Não foi possível carregar os lances canônicos e as fases.')
        }
      } finally {
        if (!controller.signal.aborted) setLoading(false)
      }
    }
    void loadCatalog()
    return () => controller.abort()
  }, [])

  useEffect(() => {
    if (!selectedLance) {
      setSaved(null)
      setSegments([])
      return
    }
    const lance = selectedLance
    const controller = new AbortController()
    const reference = lance.temporal_references[0]
    setPossessionTeam('')
    setAnalyzedTeam('')
    setSegments(reference ? [segmentFrom(reference, 1)] : [])
    setSaved(null)
    setStatus('')
    setError('')
    setLoadingClassification(true)

    async function loadClassification() {
      try {
        const response = await fetch(
          `/catalog/lances/${lance.id}/phase-classification`,
          { signal: controller.signal },
        )
        if (response.status === 404) return
        if (!response.ok) throw new Error('classification')
        setSaved(await response.json() as SavedClassification)
      } catch {
        if (!controller.signal.aborted) {
          setError('Não foi possível consultar a classificação deste lance.')
        }
      } finally {
        if (!controller.signal.aborted) setLoadingClassification(false)
      }
    }
    void loadClassification()
    return () => controller.abort()
  }, [selectedLance])

  function updateSegment(localId: number, change: Partial<SegmentDraft>) {
    setSegments((current) => current.map((segment) =>
      segment.localId === localId ? { ...segment, ...change } : segment,
    ))
  }

  function changeSource(localId: number, sourceId: string) {
    const reference = selectedLance?.temporal_references.find(
      (item) => item.video_source_id === sourceId,
    )
    if (!reference) return
    updateSegment(localId, {
      video_source_id: sourceId,
      start_ms: reference.start_ms,
      end_ms: reference.end_ms,
    })
  }

  function addSegment() {
    const reference = selectedLance?.temporal_references[0]
    if (!reference) return
    setSegments((current) => {
      const nextId = Math.max(0, ...current.map((segment) => segment.localId)) + 1
      return [...current, segmentFrom(reference, nextId)]
    })
  }

  function validate(): string | null {
    if (!possessionTeam.trim() || !analyzedTeam.trim()) {
      return 'Informe a equipe com posse e a equipe analisada.'
    }
    if (segments.length === 0) return 'Adicione ao menos um segmento de fase.'
    for (const segment of segments) {
      if (!segment.phase.trim()) return 'Todos os segmentos precisam de uma fase.'
      const isEnclosed = selectedLance?.temporal_references.some(
        (reference) => reference.video_source_id === segment.video_source_id &&
          segment.start_ms >= reference.start_ms && segment.end_ms <= reference.end_ms,
      )
      if (!isEnclosed || segment.start_ms >= segment.end_ms) {
        return 'Os tempos de cada segmento devem estar dentro dos limites do lance.'
      }
    }
    return null
  }

  async function saveClassification() {
    if (!selectedLance || saving || saved) return
    const validationError = validate()
    if (validationError) {
      setError(validationError)
      return
    }
    setSaving(true)
    setError('')
    setStatus('')
    try {
      const response = await fetch(
        `/catalog/lances/${selectedLance.id}/phase-classification`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            possession_team: possessionTeam.trim(),
            analyzed_team: analyzedTeam.trim(),
            phase_segments: segments.map(({ localId: _localId, ...segment }) => ({
              team_role: segment.team_role,
              phase: segment.phase.trim(),
              temporal_references: [{
                video_source_id: segment.video_source_id,
                start_ms: segment.start_ms,
                end_ms: segment.end_ms,
              }],
            })),
          }),
        },
      )
      if (!response.ok) {
        setError(await errorMessage(response, 'Não foi possível salvar a classificação.'))
        return
      }
      const classification = await response.json() as SavedClassification
      setSaved(classification)
      setStatus('Classificação manual salva e vinculada ao lance canônico.')
    } catch {
      setError('Não foi possível salvar a classificação. Verifique o backend.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="phase-panel" aria-labelledby="phase-classification-heading">
      <header className="phase-panel__header">
        <div>
          <p className="phase-panel__eyebrow">INC-003 · catálogo canônico</p>
          <h2 id="phase-classification-heading">Classificação manual de posse e fase</h2>
        </div>
        <p className="phase-panel__principle">A interface registra; não classifica automaticamente.</p>
      </header>

      {loading && <p role="status">Carregando lances canônicos…</p>}
      {!loading && lances.length === 0 && !error && (
        <p>Nenhum lance canônico disponível. Cadastre o lance pela API do catálogo.</p>
      )}
      {lances.length > 0 && (
        <>
          <div className="phase-panel__field phase-panel__lance-picker">
            <label htmlFor="canonical-lance">Lance canônico</label>
            <select
              id="canonical-lance"
              value={selectedLanceId}
              onChange={(event) => setSelectedLanceId(event.target.value)}
              disabled={saving}
            >
              {lances.map((lance) => (
                <option key={lance.id} value={lance.id}>
                  {lance.id} · {lance.temporal_references[0]?.media_path ?? 'sem fonte'}
                </option>
              ))}
            </select>
          </div>

          {loadingClassification && <p role="status">Consultando classificação…</p>}
          {saved && (
            <div className="phase-panel__saved" aria-label="Classificação salva">
              <p><strong>Equipe com posse:</strong> {saved.possession_team}</p>
              <p><strong>Equipe analisada:</strong> {saved.analyzed_team}</p>
              <ol>
                {saved.phase_segments.map((segment) => (
                  <li key={segment.id}>
                    <strong>{ROLE_LABELS[segment.team_role]} · {segment.team_name}</strong>
                    <span>{segment.phase}</span>
                    {segment.temporal_references.map((reference) => (
                      <small key={reference.id}>
                        {formatMilliseconds(reference.start_ms)} → {formatMilliseconds(reference.end_ms)}
                      </small>
                    ))}
                  </li>
                ))}
              </ol>
            </div>
          )}

          {!saved && !loadingClassification && selectedLance && (
            <form onSubmit={(event) => { event.preventDefault(); void saveClassification() }}>
              <fieldset className="phase-panel__teams">
                <legend>Contexto do lance</legend>
                <div className="phase-panel__field">
                  <label htmlFor="possession-team">Equipe com posse</label>
                  <input
                    id="possession-team"
                    value={possessionTeam}
                    onChange={(event) => setPossessionTeam(event.target.value)}
                    autoComplete="off"
                  />
                </div>
                <div className="phase-panel__field">
                  <label htmlFor="analyzed-team">Equipe analisada</label>
                  <input
                    id="analyzed-team"
                    value={analyzedTeam}
                    onChange={(event) => setAnalyzedTeam(event.target.value)}
                    autoComplete="off"
                  />
                </div>
              </fieldset>

              <div className="phase-panel__segments-heading">
                <div>
                  <h3>Segmentos de fase</h3>
                  <p>As duas equipes possuem linhas temporais independentes e podem se sobrepor.</p>
                </div>
                <button type="button" onClick={addSegment}>Adicionar segmento</button>
              </div>

              <datalist id="minimum-phase-values">
                {phaseValues.map((phase) => <option key={phase} value={phase} />)}
              </datalist>

              <ol className="phase-panel__segments">
                {segments.map((segment, index) => (
                  <li key={segment.localId} className="phase-segment">
                    <div className="phase-segment__index" aria-hidden="true">{index + 1}</div>
                    <div className="phase-segment__fields">
                      <div className="phase-panel__field">
                        <label htmlFor={`team-role-${segment.localId}`}>Dimensão de equipe</label>
                        <select
                          id={`team-role-${segment.localId}`}
                          value={segment.team_role}
                          onChange={(event) => updateSegment(segment.localId, {
                            team_role: event.target.value as SegmentDraft['team_role'],
                          })}
                        >
                          <option value="POSSESSION_TEAM">Equipe com posse</option>
                          <option value="ANALYZED_TEAM">Equipe analisada</option>
                        </select>
                      </div>
                      <div className="phase-panel__field">
                        <label htmlFor={`phase-${segment.localId}`}>Fase</label>
                        <input
                          id={`phase-${segment.localId}`}
                          list="minimum-phase-values"
                          value={segment.phase}
                          onChange={(event) => updateSegment(segment.localId, { phase: event.target.value })}
                        />
                      </div>
                      <div className="phase-panel__field phase-panel__source">
                        <label htmlFor={`source-${segment.localId}`}>Fonte</label>
                        <select
                          id={`source-${segment.localId}`}
                          value={segment.video_source_id}
                          onChange={(event) => changeSource(segment.localId, event.target.value)}
                        >
                          {selectedLance.temporal_references.map((reference) => (
                            <option key={reference.id} value={reference.video_source_id}>
                              {reference.media_path}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="phase-panel__time-grid">
                        <div className="phase-panel__field">
                          <label htmlFor={`start-${segment.localId}`}>Início (ms)</label>
                          <input
                            id={`start-${segment.localId}`}
                            type="number"
                            min="0"
                            value={segment.start_ms}
                            onChange={(event) => updateSegment(segment.localId, {
                              start_ms: Number(event.target.value),
                            })}
                          />
                        </div>
                        <div className="phase-panel__field">
                          <label htmlFor={`end-${segment.localId}`}>Fim (ms)</label>
                          <input
                            id={`end-${segment.localId}`}
                            type="number"
                            min="0"
                            value={segment.end_ms}
                            onChange={(event) => updateSegment(segment.localId, {
                              end_ms: Number(event.target.value),
                            })}
                          />
                        </div>
                      </div>
                    </div>
                    <button
                      className="phase-segment__remove"
                      type="button"
                      onClick={() => setSegments((current) => current.filter(
                        (item) => item.localId !== segment.localId,
                      ))}
                      aria-label={`Remover segmento ${index + 1}`}
                    >
                      Remover
                    </button>
                  </li>
                ))}
              </ol>

              <button className="phase-panel__save" type="submit" disabled={saving}>
                {saving ? 'Salvando classificação…' : 'Salvar classificação manual'}
              </button>
            </form>
          )}
        </>
      )}
      {error && <p className="phase-panel__message phase-panel__message--error" role="alert">{error}</p>}
      {status && <p className="phase-panel__message" role="status">{status}</p>}
    </section>
  )
}
