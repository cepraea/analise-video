/** @vitest-environment jsdom */

import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { PhaseClassificationPanel } from './PhaseClassificationPanel'

const lance = {
  id: 'lance_1',
  game_id: 'game_1',
  temporal_references: [{
    id: 'time_1',
    lance_id: 'lance_1',
    video_source_id: 'source_1',
    media_path: 'jogo.mp4',
    start_ms: 1000,
    end_ms: 5000,
    created_at: '2026-09-28T00:00:00.000Z',
  }],
}

const minimumValues = [
  'Transição Ofensiva',
  'Ataque Posicionado',
  'Transição Defensiva',
  'Defesa Posicionada',
]

function jsonResponse(value: unknown, status = 200): Response {
  return { ok: status >= 200 && status < 300, status, json: async () => value } as Response
}

function savedClassification() {
  return {
    lance_id: lance.id,
    possession_team: 'Adversária',
    analyzed_team: 'CEPRAEA',
    phase_segments: [
      {
        id: 'phase_1',
        team_role: 'POSSESSION_TEAM',
        team_name: 'Adversária',
        phase: 'Transição Ofensiva',
        temporal_references: [{
          id: 'phase_time_1', video_source_id: 'source_1', start_ms: 1000, end_ms: 2500,
        }],
      },
      {
        id: 'phase_2',
        team_role: 'ANALYZED_TEAM',
        team_name: 'CEPRAEA',
        phase: 'Transição Defensiva',
        temporal_references: [{
          id: 'phase_time_2', video_source_id: 'source_1', start_ms: 1200, end_ms: 2800,
        }],
      },
    ],
  }
}

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

describe('classificação manual de posse e fase', () => {
  it('salva equipes independentes e segmentos sobrepostos', async () => {
    const fetchMock = vi.fn(async (input: string | URL, init?: RequestInit) => {
      const path = String(input)
      if (path === '/catalog/lances') return jsonResponse([lance])
      if (path === '/catalog/phase-values') {
        return jsonResponse({ minimum_values: minimumValues })
      }
      if (path.endsWith('/phase-classification') && init?.method === 'POST') {
        return jsonResponse(savedClassification(), 201)
      }
      if (path.endsWith('/phase-classification')) return jsonResponse({}, 404)
      throw new Error(`Unexpected request: ${path}`)
    })
    vi.stubGlobal('fetch', fetchMock)
    render(<PhaseClassificationPanel />)

    await screen.findByLabelText('Equipe analisada')
    fireEvent.change(screen.getByLabelText('Equipe com posse'), {
      target: { value: 'Adversária' },
    })
    fireEvent.change(screen.getByLabelText('Equipe analisada'), {
      target: { value: 'CEPRAEA' },
    })
    fireEvent.change(screen.getByLabelText('Fim (ms)'), {
      target: { value: '2500' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Adicionar segmento' }))

    const roles = screen.getAllByLabelText('Dimensão de equipe')
    const phases = screen.getAllByLabelText('Fase')
    const starts = screen.getAllByLabelText('Início (ms)')
    const ends = screen.getAllByLabelText('Fim (ms)')
    fireEvent.change(roles[1], { target: { value: 'ANALYZED_TEAM' } })
    fireEvent.change(phases[1], { target: { value: 'Transição Defensiva' } })
    fireEvent.change(starts[1], { target: { value: '1200' } })
    fireEvent.change(ends[1], { target: { value: '2800' } })
    fireEvent.click(screen.getByRole('button', { name: 'Salvar classificação manual' }))

    await screen.findByText('Classificação manual salva e vinculada ao lance canônico.')
    const posts = fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')
    expect(posts).toHaveLength(1)
    expect(JSON.parse(posts[0][1]?.body as string)).toEqual({
      possession_team: 'Adversária',
      analyzed_team: 'CEPRAEA',
      phase_segments: [
        {
          team_role: 'POSSESSION_TEAM',
          phase: 'Transição Ofensiva',
          temporal_references: [{
            video_source_id: 'source_1', start_ms: 1000, end_ms: 2500,
          }],
        },
        {
          team_role: 'ANALYZED_TEAM',
          phase: 'Transição Defensiva',
          temporal_references: [{
            video_source_id: 'source_1', start_ms: 1200, end_ms: 2800,
          }],
        },
      ],
    })
  })

  it('recupera a classificação existente em modo somente leitura', async () => {
    const existing = savedClassification()
    vi.stubGlobal('fetch', vi.fn(async (input: string | URL) => {
      const path = String(input)
      if (path === '/catalog/lances') return jsonResponse([lance])
      if (path === '/catalog/phase-values') {
        return jsonResponse({ minimum_values: minimumValues })
      }
      if (path.endsWith('/phase-classification')) return jsonResponse(existing)
      throw new Error(`Unexpected request: ${path}`)
    }))

    render(<PhaseClassificationPanel />)

    const saved = await screen.findByLabelText('Classificação salva')
    expect(saved.textContent).toContain('Equipe com posse: Adversária')
    expect(saved.textContent).toContain('Equipe analisada: CEPRAEA')
    expect(saved.textContent).toContain('Transição Ofensiva')
    expect(saved.textContent).toContain('Transição Defensiva')
    expect(screen.queryByRole('button', { name: 'Salvar classificação manual' })).toBeNull()
  })
})
