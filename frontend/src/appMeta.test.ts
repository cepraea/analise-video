import { describe, expect, it } from 'vitest'

import { APP_NAME, APP_STATUS } from './appMeta'

describe('bootstrap metadata', () => {
  it('identifies the application and current increment', () => {
    expect(APP_NAME).toBe('CEPRAEA — Análise de Vídeo')
    expect(APP_STATUS).toContain('INC-000')
  })
})
