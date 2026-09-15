/** @vitest-environment jsdom */

import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { App } from './App'

type SavedInterval = {
  id: number
  media_path: string
  start_ms: number
  end_ms: number
  created_at: string
}

const savedInterval: SavedInterval = {
  id: 1,
  media_path: 'video.mp4',
  start_ms: 1200,
  end_ms: 3400,
  created_at: '2026-09-13T00:00:00.000Z',
}

function jsonResponse(value: unknown, status = 200): Response {
  return { ok: status >= 200 && status < 300, status, json: async () => value } as Response
}

async function renderWithLocalMedia(initialIntervals: SavedInterval[] = []) {
  const fetchMock = vi.fn(async (input: string | URL, init?: RequestInit) => {
    const path = String(input)
    if (path === '/spike/media') {
      return jsonResponse([{ media_path: 'video.mp4', url: '/spike/media/video.mp4' }])
    }
    if (path === '/spike/intervals' && init?.method === 'POST') {
      return jsonResponse(savedInterval, 201)
    }
    if (path === '/spike/intervals') return jsonResponse(initialIntervals)
    throw new Error(`Unexpected request: ${path}`)
  })
  vi.stubGlobal('fetch', fetchMock)

  render(<App />)
  const video = (await screen.findByLabelText('Reprodutor de video.mp4')) as HTMLVideoElement
  Object.defineProperty(video, 'duration', { configurable: true, value: 120 })
  fireEvent.loadedMetadata(video)
  await waitFor(() => {
    expect(document.body.textContent).toContain(
      initialIntervals.length > 0 ? 'Intervalo 001 — video.mp4' : 'Nenhum intervalo salvo.',
    )
  })
  return { video, fetchMock }
}

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

describe('marcação de intervalo', () => {
  it('captura tempos inteiros, envia um intervalo válido e exibe o registro salvo', async () => {
    const { video, fetchMock } = await renderWithLocalMedia()

    video.currentTime = 1.2
    fireEvent.click(screen.getByRole('button', { name: 'INICIAR LANCE' }))
    expect(document.body.textContent).toContain('Início: 00:01.200 (1200 ms)')

    video.currentTime = 3.4
    fireEvent.click(screen.getByRole('button', { name: 'ENCERRAR LANCE' }))

    await screen.findByText('Intervalo #1 salvo no SQLite, sem criar outro MP4.')
    expect(document.body.textContent).toContain('Fim: 00:03.400 (3400 ms)')
    expect(document.body.textContent).toContain('Intervalo 001 — video.mp4 · 00:01.200 → 00:03.400')
    const posts = fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')
    expect(posts).toHaveLength(1)
    expect(JSON.parse(posts[0][1]?.body as string)).toEqual({
      media_path: 'video.mp4',
      start_ms: 1200,
      end_ms: 3400,
    })
  })

  it.each([1200, 800])('recusa fim %i ms quando início é 1200 ms', async (endMs) => {
    const { video, fetchMock } = await renderWithLocalMedia()

    video.currentTime = 1.2
    fireEvent.click(screen.getByRole('button', { name: 'INICIAR LANCE' }))
    video.currentTime = endMs / 1000
    fireEvent.click(screen.getByRole('button', { name: 'ENCERRAR LANCE' }))

    expect(screen.getByRole('alert').textContent).toContain('O fim deve ser posterior ao início')
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')).toHaveLength(0)
  })

  it('mostra um intervalo recuperado pela API ao abrir a interface', async () => {
    await renderWithLocalMedia([savedInterval])

    await waitFor(() => {
      expect(document.body.textContent).toContain('Intervalo 001 — video.mp4 · 00:01.200 → 00:03.400')
    })
    expect(screen.getByRole('button', { name: 'REVER' }).hasAttribute('disabled')).toBe(false)
  })
})
