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

async function renderWithLocalMedia(
  initialIntervals: SavedInterval[] = [],
  postInterval: () => Promise<Response> = async () => jsonResponse(savedInterval, 201),
  mediaPaths: string[] = ['video.mp4'],
  mutations: {
    patch?: (path: string, init: RequestInit) => Promise<Response>
    delete?: (path: string, init: RequestInit) => Promise<Response>
  } = {},
) {
  const fetchMock = vi.fn(async (input: string | URL, init?: RequestInit) => {
    const path = String(input)
    if (path === '/spike/media') {
      return jsonResponse(mediaPaths.map((mediaPath) => ({
        media_path: mediaPath,
        url: `/spike/media/${mediaPath}`,
      })))
    }
    if (path === '/spike/intervals' && init?.method === 'POST') {
      return postInterval()
    }
    if (path.startsWith('/spike/intervals/') && init?.method === 'PATCH' && mutations.patch) {
      return mutations.patch(path, init)
    }
    if (path.startsWith('/spike/intervals/') && init?.method === 'DELETE' && mutations.delete) {
      return mutations.delete(path, init)
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

describe('correção e exclusão de intervalos salvos', () => {
  it('ajusta as duas bordas independentemente e mantém o ID após salvar', async () => {
    const updated = { ...savedInterval, start_ms: 1300, end_ms: 3500 }
    const { fetchMock } = await renderWithLocalMedia(
      [savedInterval], undefined, undefined,
      { patch: async () => jsonResponse(updated) },
    )

    expect(screen.getByRole('button', { name: 'REVER' })).toBeTruthy()
    expect(screen.getByRole('button', { name: 'EDITAR' })).toBeTruthy()
    expect(screen.getByRole('button', { name: 'EXCLUIR' })).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: 'EDITAR' }))
    expect(document.body.textContent).toContain('Tempos atuais: 00:01.200 → 00:03.400')
    fireEvent.click(screen.getByRole('button', { name: 'Início +0,1 s' }))
    fireEvent.click(screen.getByRole('button', { name: 'Fim +0,1 s' }))
    expect(document.body.textContent).toContain('Novos tempos: 00:01.300 → 00:03.500')
    fireEvent.click(screen.getByRole('button', { name: 'SALVAR ALTERAÇÕES' }))

    await screen.findByText('Intervalo 001 corrigido no mesmo ID.')
    expect(document.body.textContent).toContain('Intervalo 001 — video.mp4 · 00:01.300 → 00:03.500')
    const patches = fetchMock.mock.calls.filter(([, init]) => init?.method === 'PATCH')
    expect(patches).toHaveLength(1)
    expect(patches[0][0]).toBe('/spike/intervals/1')
    expect(JSON.parse(patches[0][1]?.body as string)).toEqual({ start_ms: 1300, end_ms: 3500 })
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')).toHaveLength(0)
  })

  it('recusa ajuste fora do MP4 e início igual ao fim sem PATCH', async () => {
    const { fetchMock } = await renderWithLocalMedia([savedInterval])
    fireEvent.click(screen.getByRole('button', { name: 'EDITAR' }))
    fireEvent.click(screen.getByRole('button', { name: 'Início −10 s' }))
    expect(screen.getByRole('alert').textContent).toContain('entre zero e a duração')
    fireEvent.click(screen.getByRole('button', { name: 'Início +1 s' }))
    fireEvent.click(screen.getByRole('button', { name: 'Início +1 s' }))
    fireEvent.click(screen.getByRole('button', { name: 'Início +0,1 s' }))
    fireEvent.click(screen.getByRole('button', { name: 'Início +0,1 s' }))
    fireEvent.click(screen.getByRole('button', { name: 'SALVAR ALTERAÇÕES' }))
    expect(screen.getByRole('alert').textContent).toContain('O início deve ser menor que o fim')
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'PATCH')).toHaveLength(0)
  })

  it('exige motivo e oculta o intervalo excluído sem criar MP4', async () => {
    const { fetchMock } = await renderWithLocalMedia(
      [savedInterval], undefined, undefined,
      { delete: async () => jsonResponse({ status: 'EXCLUÍDO' }) },
    )
    fireEvent.click(screen.getByRole('button', { name: 'EXCLUIR' }))
    fireEvent.click(screen.getByRole('button', { name: 'CONFIRMAR EXCLUSÃO' }))
    expect(screen.getByRole('alert').textContent).toContain('Informe o motivo')
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'DELETE')).toHaveLength(0)
    fireEvent.change(screen.getByLabelText('Motivo da exclusão'), { target: { value: '  Marcação inválida  ' } })
    fireEvent.click(screen.getByRole('button', { name: 'CONFIRMAR EXCLUSÃO' }))
    await screen.findByText('Intervalo 001 excluído logicamente.')
    expect(document.body.textContent).toContain('Nenhum intervalo salvo.')
    const deletes = fetchMock.mock.calls.filter(([, init]) => init?.method === 'DELETE')
    expect(deletes).toHaveLength(1)
    expect(JSON.parse(deletes[0][1]?.body as string)).toEqual({ reason: 'Marcação inválida' })
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')).toHaveLength(0)
  })
})

describe('marcação de intervalo', () => {
  it('mostra a prévia sem POST e salva somente após confirmação', async () => {
    const { video, fetchMock } = await renderWithLocalMedia()

    video.currentTime = 1.2
    fireEvent.click(screen.getByRole('button', { name: 'INICIAR LANCE' }))
    expect(document.body.textContent).toContain('Início: 00:01.200 (1200 ms)')

    video.currentTime = 3.4
    fireEvent.click(screen.getByRole('button', { name: 'ENCERRAR LANCE' }))

    expect(document.body.textContent).toContain('Fim: 00:03.400 (3400 ms)')
    expect(document.body.textContent).toContain('Prévia válida: 00:01.200 → 00:03.400')
    expect(screen.getByRole('button', { name: 'REVER' })).toBeTruthy()
    expect(screen.getByRole('button', { name: 'DESCARTAR' })).toBeTruthy()
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')).toHaveLength(0)

    fireEvent.click(screen.getByRole('button', { name: 'CONFIRMAR E SALVAR' }))

    await screen.findByText('Intervalo #1 salvo no SQLite, sem criar outro MP4.')
    expect(document.body.textContent).toContain('Intervalo 001 — video.mp4 · 00:01.200 → 00:03.400')
    expect(document.body.textContent).toContain('Início: não marcado')
    const posts = fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')
    expect(posts).toHaveLength(1)
    expect(JSON.parse(posts[0][1]?.body as string)).toEqual({
      media_path: 'video.mp4',
      start_ms: 1200,
      end_ms: 3400,
    })
  })

  it('descarta uma prévia sem criar registro', async () => {
    const { video, fetchMock } = await renderWithLocalMedia()

    video.currentTime = 1.2
    fireEvent.click(screen.getByRole('button', { name: 'INICIAR LANCE' }))
    video.currentTime = 3.4
    fireEvent.click(screen.getByRole('button', { name: 'ENCERRAR LANCE' }))
    fireEvent.click(screen.getByRole('button', { name: 'DESCARTAR' }))

    expect(document.body.textContent).toContain('Início: não marcado')
    expect(document.body.textContent).toContain('Fim: não marcado')
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')).toHaveLength(0)
  })

  it('bloqueia troca e atualização de MP4 até confirmar ou descartar a marcação', async () => {
    const { video, fetchMock } = await renderWithLocalMedia([], undefined, ['video.mp4', 'outro.mp4'])
    Object.defineProperty(video, 'play', { configurable: true, value: vi.fn().mockResolvedValue(undefined) })
    Object.defineProperty(video, 'pause', { configurable: true, value: vi.fn() })
    const mediaSelect = screen.getByLabelText('Arquivo') as HTMLSelectElement
    const refreshButton = screen.getByRole('button', { name: 'Atualizar lista' })

    video.currentTime = 1.2
    fireEvent.click(screen.getByRole('button', { name: 'INICIAR LANCE' }))
    video.currentTime = 3.4
    fireEvent.click(screen.getByRole('button', { name: 'ENCERRAR LANCE' }))

    expect(mediaSelect.disabled).toBe(true)
    expect((refreshButton as HTMLButtonElement).disabled).toBe(true)
    fireEvent.change(mediaSelect, { target: { value: 'outro.mp4' } })
    expect(mediaSelect.value).toBe('video.mp4')
    expect(document.body.textContent).toContain('Prévia válida: 00:01.200 → 00:03.400')

    fireEvent.click(screen.getByRole('button', { name: 'REVER' }))
    fireEvent.seeked(video)
    await screen.findByText('Revendo prévia do lance.')
    expect(mediaSelect.disabled).toBe(true)
    expect((refreshButton as HTMLButtonElement).disabled).toBe(true)

    fireEvent.click(screen.getByRole('button', { name: 'SAIR DA REVISÃO' }))
    fireEvent.click(screen.getByRole('button', { name: 'DESCARTAR' }))
    expect(mediaSelect.disabled).toBe(false)
    expect((refreshButton as HTMLButtonElement).disabled).toBe(false)
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')).toHaveLength(0)
  })

  it('revê a prévia sem salvar e preserva os tempos ao terminar', async () => {
    const { video, fetchMock } = await renderWithLocalMedia()
    Object.defineProperty(video, 'play', { configurable: true, value: vi.fn().mockResolvedValue(undefined) })
    Object.defineProperty(video, 'pause', { configurable: true, value: vi.fn() })

    video.currentTime = 1.2
    fireEvent.click(screen.getByRole('button', { name: 'INICIAR LANCE' }))
    video.currentTime = 3.4
    fireEvent.click(screen.getByRole('button', { name: 'ENCERRAR LANCE' }))
    fireEvent.click(screen.getByRole('button', { name: 'REVER' }))
    expect(video.currentTime).toBe(1.2)
    fireEvent.seeked(video)
    await screen.findByText('Revendo prévia do lance.')

    video.currentTime = 3.4
    fireEvent.timeUpdate(video)

    await screen.findByText('Revisão da prévia concluída.')
    expect(document.body.textContent).toContain('Prévia válida: 00:01.200 → 00:03.400')
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')).toHaveLength(0)
  })

  it('permite sair da revisão e confirmar a mesma prévia', async () => {
    const { video, fetchMock } = await renderWithLocalMedia()
    Object.defineProperty(video, 'play', { configurable: true, value: vi.fn().mockResolvedValue(undefined) })
    Object.defineProperty(video, 'pause', { configurable: true, value: vi.fn() })

    video.currentTime = 1.2
    fireEvent.click(screen.getByRole('button', { name: 'INICIAR LANCE' }))
    video.currentTime = 3.4
    fireEvent.click(screen.getByRole('button', { name: 'ENCERRAR LANCE' }))
    fireEvent.click(screen.getByRole('button', { name: 'REVER' }))
    fireEvent.seeked(video)
    await screen.findByText('Revendo prévia do lance.')
    fireEvent.click(screen.getByRole('button', { name: 'SAIR DA REVISÃO' }))

    expect(document.body.textContent).toContain('Prévia válida: 00:01.200 → 00:03.400')
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')).toHaveLength(0)
    fireEvent.click(screen.getByRole('button', { name: 'CONFIRMAR E SALVAR' }))
    await screen.findByText('Intervalo #1 salvo no SQLite, sem criar outro MP4.')
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')).toHaveLength(1)
  })

  it('usa o primeiro Esc para sair da revisão e o segundo para descartar a prévia', async () => {
    const { video, fetchMock } = await renderWithLocalMedia()
    Object.defineProperty(video, 'play', { configurable: true, value: vi.fn().mockResolvedValue(undefined) })
    Object.defineProperty(video, 'pause', { configurable: true, value: vi.fn() })

    video.currentTime = 1.2
    fireEvent.click(screen.getByRole('button', { name: 'INICIAR LANCE' }))
    video.currentTime = 3.4
    fireEvent.click(screen.getByRole('button', { name: 'ENCERRAR LANCE' }))
    fireEvent.click(screen.getByRole('button', { name: 'REVER' }))
    fireEvent.seeked(video)
    await screen.findByText('Revendo prévia do lance.')

    fireEvent.keyDown(window, { key: 'Escape' })
    expect(document.body.textContent).toContain('Prévia válida: 00:01.200 → 00:03.400')
    expect(screen.getByRole('button', { name: 'REVER' })).toBeTruthy()
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')).toHaveLength(0)

    fireEvent.keyDown(window, { key: 'Escape' })
    expect(document.body.textContent).toContain('Início: não marcado')
    expect(document.body.textContent).toContain('Fim: não marcado')
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')).toHaveLength(0)
  })

  it('preserva a prévia quando o salvamento falha', async () => {
    const { video, fetchMock } = await renderWithLocalMedia([], async () => jsonResponse({}, 500))

    video.currentTime = 1.2
    fireEvent.click(screen.getByRole('button', { name: 'INICIAR LANCE' }))
    video.currentTime = 3.4
    fireEvent.click(screen.getByRole('button', { name: 'ENCERRAR LANCE' }))
    fireEvent.click(screen.getByRole('button', { name: 'CONFIRMAR E SALVAR' }))

    await screen.findByRole('alert')
    expect(document.body.textContent).toContain('Prévia válida: 00:01.200 → 00:03.400')
    expect(screen.getByRole('button', { name: 'CONFIRMAR E SALVAR' }).hasAttribute('disabled')).toBe(false)
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')).toHaveLength(1)
  })

  it('impede confirmação duplicada enquanto o POST está pendente', async () => {
    let finishPost: (response: Response) => void = () => { throw new Error('POST não iniciado') }
    const pendingPost = new Promise<Response>((resolve) => { finishPost = resolve })
    const { video, fetchMock } = await renderWithLocalMedia([], () => pendingPost)

    video.currentTime = 1.2
    fireEvent.click(screen.getByRole('button', { name: 'INICIAR LANCE' }))
    video.currentTime = 3.4
    fireEvent.click(screen.getByRole('button', { name: 'ENCERRAR LANCE' }))
    const confirm = screen.getByRole('button', { name: 'CONFIRMAR E SALVAR' })
    fireEvent.click(confirm)
    fireEvent.click(confirm)

    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')).toHaveLength(1)
    finishPost(jsonResponse(savedInterval, 201))
    await screen.findByText('Intervalo #1 salvo no SQLite, sem criar outro MP4.')
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

describe('navegação temporal por teclado', () => {
  it('aplica passos de 10 s, 1 s e 0,1 s e captura milissegundos inteiros', async () => {
    const { video } = await renderWithLocalMedia()
    video.currentTime = 75.32

    fireEvent.keyDown(window, { key: 'ArrowLeft', ctrlKey: true })
    expect(video.currentTime).toBeCloseTo(65.32, 3)
    fireEvent.keyDown(window, { key: 'ArrowRight', ctrlKey: true })
    expect(video.currentTime).toBeCloseTo(75.32, 3)

    fireEvent.keyDown(window, { key: 'ArrowLeft' })
    expect(video.currentTime).toBeCloseTo(74.32, 3)
    fireEvent.keyDown(window, { key: 'ArrowRight' })
    expect(video.currentTime).toBeCloseTo(75.32, 3)

    fireEvent.keyDown(window, { key: 'ArrowLeft', shiftKey: true })
    expect(video.currentTime).toBeCloseTo(75.22, 3)
    fireEvent.keyDown(window, { key: 'ArrowRight', shiftKey: true })
    expect(video.currentTime).toBeCloseTo(75.32, 3)

    fireEvent.keyDown(window, { key: 'ArrowRight', shiftKey: true })
    fireEvent.click(screen.getByRole('button', { name: 'INICIAR LANCE' }))
    fireEvent.keyDown(window, { key: 'ArrowRight' })
    fireEvent.click(screen.getByRole('button', { name: 'ENCERRAR LANCE' }))
    expect(document.body.textContent).toContain('Início: 01:15.420 (75420 ms)')
    expect(document.body.textContent).toContain('Fim: 01:16.420 (76420 ms)')
  })

  it('limita as setas e os botões ao início e à duração do MP4', async () => {
    const { video } = await renderWithLocalMedia()

    video.currentTime = 0.05
    fireEvent.keyDown(window, { key: 'ArrowLeft', ctrlKey: true })
    expect(video.currentTime).toBe(0)
    fireEvent.click(screen.getByRole('button', { name: 'Voltar 10 s' }))
    expect(video.currentTime).toBe(0)

    video.currentTime = 119.95
    fireEvent.keyDown(window, { key: 'ArrowRight', ctrlKey: true })
    expect(video.currentTime).toBe(120)
    fireEvent.keyDown(window, { key: 'ArrowRight', shiftKey: true })
    expect(video.currentTime).toBe(120)
    fireEvent.click(screen.getByRole('button', { name: 'Avançar 10 s' }))
    expect(video.currentTime).toBe(120)
  })

  it('ignora modificadores não previstos e teclas em controles editáveis', async () => {
    const { video } = await renderWithLocalMedia()
    video.currentTime = 50

    fireEvent.keyDown(window, { key: 'ArrowRight', ctrlKey: true, shiftKey: true })
    fireEvent.keyDown(window, { key: 'ArrowLeft', altKey: true })
    fireEvent.keyDown(window, { key: 'ArrowRight', metaKey: true })
    fireEvent.keyDown(window, { key: 'ArrowLeft', ctrlKey: true, altKey: true })
    fireEvent.keyDown(screen.getByLabelText('Arquivo'), { key: 'ArrowRight' })

    expect(video.currentTime).toBe(50)
  })
})

describe('velocidade de reprodução', () => {
  it('começa em 1x e aplica cada velocidade oferecida ao vídeo', async () => {
    const { video } = await renderWithLocalMedia()
    const selector = screen.getByLabelText('Velocidade') as HTMLSelectElement

    expect(selector.value).toBe('1')
    expect(video.playbackRate).toBe(1)
    expect(Array.from(selector.options, (option) => option.textContent)).toEqual([
      '0,25x', '0,5x', '1x', '1,5x', '2x',
    ])

    for (const rate of [0.25, 0.5, 1, 1.5, 2]) {
      fireEvent.change(selector, { target: { value: String(rate) } })
      expect(selector.value).toBe(String(rate))
      expect(video.playbackRate).toBe(rate)
    }
  })

  it('mantém a velocidade escolhida ao abrir outro MP4', async () => {
    await renderWithLocalMedia([], undefined, ['video.mp4', 'outro.mp4'])
    const selector = screen.getByLabelText('Velocidade') as HTMLSelectElement
    fireEvent.change(selector, { target: { value: '1.5' } })
    fireEvent.change(screen.getByLabelText('Arquivo'), { target: { value: 'outro.mp4' } })

    const otherVideo = (await screen.findByLabelText('Reprodutor de outro.mp4')) as HTMLVideoElement
    Object.defineProperty(otherVideo, 'duration', { configurable: true, value: 120 })
    fireEvent.loadedMetadata(otherVideo)

    expect(selector.value).toBe('1.5')
    expect(otherVideo.playbackRate).toBe(1.5)
  })
})

describe('atalhos de operação', () => {
  it('usa Espaço para reproduzir/pausar sem duplicar controles focados', async () => {
    const { video } = await renderWithLocalMedia()
    let paused = true
    const play = vi.fn(async () => { paused = false })
    const pause = vi.fn(() => { paused = true })
    Object.defineProperty(video, 'paused', { configurable: true, get: () => paused })
    Object.defineProperty(video, 'play', { configurable: true, value: play })
    Object.defineProperty(video, 'pause', { configurable: true, value: pause })

    fireEvent.keyDown(window, { key: ' ' })
    await waitFor(() => expect(play).toHaveBeenCalledTimes(1))
    fireEvent.keyDown(window, { key: ' ' })
    expect(pause).toHaveBeenCalledTimes(1)

    fireEvent.keyDown(screen.getByRole('button', { name: 'Voltar 10 s' }), { key: ' ' })
    fireEvent.keyDown(video, { key: ' ' })
    expect(play).toHaveBeenCalledTimes(1)
    expect(pause).toHaveBeenCalledTimes(1)
  })

  it('marca com I/O e faz um único POST com Enter', async () => {
    const { video, fetchMock } = await renderWithLocalMedia()

    video.currentTime = 1.2
    fireEvent.keyDown(window, { key: 'i' })
    expect(document.body.textContent).toContain('Início: 00:01.200 (1200 ms)')
    video.currentTime = 3.4
    fireEvent.keyDown(window, { key: 'o' })
    expect(document.body.textContent).toContain('Prévia válida: 00:01.200 → 00:03.400')
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')).toHaveLength(0)

    fireEvent.keyDown(window, { key: 'Enter' })
    fireEvent.keyDown(window, { key: 'Enter' })
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')).toHaveLength(1)
    await screen.findByText('Intervalo #1 salvo no SQLite, sem criar outro MP4.')
  })

  it('só revê com R o intervalo salvo selecionado por foco', async () => {
    const secondInterval = { ...savedInterval, id: 2, start_ms: 5000, end_ms: 7000 }
    const { video } = await renderWithLocalMedia([savedInterval, secondInterval])
    Object.defineProperty(video, 'play', { configurable: true, value: vi.fn().mockResolvedValue(undefined) })
    Object.defineProperty(video, 'pause', { configurable: true, value: vi.fn() })

    fireEvent.keyDown(window, { key: 'r' })
    expect(document.body.textContent).toContain('Selecione um intervalo salvo para rever com R.')
    expect(video.currentTime).toBe(0)

    const selectors = screen.getAllByRole('button', { name: 'SELECIONAR PARA R' })
    fireEvent.focus(selectors[1])
    expect(selectors[1].getAttribute('aria-pressed')).toBe('true')
    fireEvent.keyDown(selectors[1], { key: 'r' })
    expect(video.currentTime).toBe(5)
    fireEvent.seeked(video)
    await screen.findByText('Revendo intervalo 002.')

    fireEvent.keyDown(window, { key: 'Escape' })
    expect(document.body.textContent).toContain('Revisão do intervalo interrompida.')
  })

  it('prioriza a prévia em R mesmo com um salvo selecionado', async () => {
    const { video, fetchMock } = await renderWithLocalMedia([savedInterval])
    Object.defineProperty(video, 'play', { configurable: true, value: vi.fn().mockResolvedValue(undefined) })
    Object.defineProperty(video, 'pause', { configurable: true, value: vi.fn() })
    fireEvent.focus(screen.getByRole('button', { name: 'SELECIONAR PARA R' }))

    video.currentTime = 10
    fireEvent.keyDown(window, { key: 'i' })
    video.currentTime = 20
    fireEvent.keyDown(window, { key: 'o' })
    fireEvent.keyDown(window, { key: 'r' })

    expect(video.currentTime).toBe(10)
    fireEvent.seeked(video)
    await screen.findByText('Revendo prévia do lance.')
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')).toHaveLength(0)
  })

  it('preserva edição de campos e ativação nativa de botões', async () => {
    const { video, fetchMock } = await renderWithLocalMedia()
    const input = document.createElement('input')
    document.body.append(input)
    try {
      video.currentTime = 1.2
      fireEvent.keyDown(input, { key: 'i' })
      fireEvent.keyDown(video, { key: 'i' })
      fireEvent.keyDown(window, { key: 'i', ctrlKey: true })
      expect(document.body.textContent).toContain('Início: não marcado')

      fireEvent.keyDown(window, { key: 'i' })
      video.currentTime = 3.4
      fireEvent.keyDown(window, { key: 'o' })
      const confirm = screen.getByRole('button', { name: 'CONFIRMAR E SALVAR' })
      fireEvent.keyDown(confirm, { key: 'Enter' })
      expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')).toHaveLength(0)
      fireEvent.click(confirm)
      await screen.findByText('Intervalo #1 salvo no SQLite, sem criar outro MP4.')
      expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')).toHaveLength(1)
    } finally {
      input.remove()
    }
  })
})
