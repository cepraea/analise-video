# INC-001 — Integridade do MP4 original (RF-030/RNF-005)

- Data: 2026-09-13.
- Branch: `inc-001-architecture-spike`.
- Escopo verificado: MP4 real do spike, após marcação, persistência, reinício e revisão dos intervalos 001 e 002.

Arquivo: `.local/media/CEPRAEA x COSTA.mp4` (`854101055` bytes).

| Medição | SHA-256 |
| --- | --- |
| Antes dos testes, registrado em `docs/evidence/INC-001-save.md` | `ea6607f4d6a0095c1b413722fefa41aa50be57f2e1b6b9bed1fef7ed908c23c9` |
| Depois de todos os testes do INC-001, calculado novamente | `ea6607f4d6a0095c1b413722fefa41aa50be57f2e1b6b9bed1fef7ed908c23c9` |

Comandos executados após o teste crítico de persistência:

```bash
sha256sum '.local/media/CEPRAEA x COSTA.mp4'
printf '%s  %s\n' 'ea6607f4d6a0095c1b413722fefa41aa50be57f2e1b6b9bed1fef7ed908c23c9' '.local/media/CEPRAEA x COSTA.mp4' | sha256sum --check
```

O segundo comando retornou `.local/media/CEPRAEA x COSTA.mp4: OK` com código de saída `0`. `find .local/media -maxdepth 1 -type f` listou somente o MP4 original. Portanto, **hash antes = hash depois** para o arquivo testado; RF-030 e RNF-005 têm evidência observável no escopo INC-001. A validação dos mesmos requisitos nos incrementos futuros continua pendente.
