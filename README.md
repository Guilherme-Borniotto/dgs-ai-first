# NovaTech Assistant - AI First Lab

Repositorio com os artefatos dos cenarios praticos do programa AI First, cobrindo as fases de entendimento, estruturacao e governanca do assistente da NovaTech.

**Autor:** Guilherme Borniotto  
**Atualizado em:** 09/07/2026

---

## Visao Geral

O conteudo esta organizado por fases:

1. **Fase 1 - Entendimento e Contexto**
2. **Fase 2 - Estruturacao do Trabalho**
3. **Fase 3 - Governanca e Validacao**

Cada fase possui enunciados e entregaveis em markdown, e quando aplicavel inclui codigo de apoio para os exercicios tecnicos.

---

## Estrutura do Repositorio

```text
assets/
    anexos/
        anexo-a-documentos-individuais/
        anexo-b-chunks-referencia-rag.md

exercicios/
    fase-1/
        entregaveis/
            exercicio-1.1-resolucao.md
            exercicio-1.2-resolucao.md
            exercicio-1.3-resolucao.md
            exercicio-fase-1-entendimento.md

    fase-2/
        entregaveis/
            2.1-mcp-servers/
            2.2-sdd-implementacao/
            2.3-skills-strategy/

    fase-3/
        cenario-3-exercicios-fase-governanca.md
        entregaveis/
            exercicio-3.1-resolucao.md
            exercicio-3.2-resolucao.md
            exercicio-fase-3-governanca.md
            src/
                functions/feedback/
                    handler.ts
                    validator.ts
                services/
                    response-validator.ts
                shared/
                    logger.ts

rag/
    ingest.py
    search.py
    prompt_builder.py
    run_tests.py
```

---

## Status por Fase

| Fase | Status | Principais Entregas |
|---|---|---|
| 1 - Entendimento | Concluida | Analise tecnica, engenharia de prompt e pipeline RAG |
| 2 - Estruturacao | Concluida | MCP mapping, SDD tasks, estrategia de skills |
| 3 - Governanca | Concluida | Structured output, guardrails deterministicos e revisao critica |

---

## Destaques da Fase 3 (Desenvolvedor)

- Implementacao de validacao de resposta estruturada com Zod.
- Aplicacao de guardrails deterministicos para bloquear respostas inseguras.
- Reescrita segura do modulo de feedback com:
    - validacao de input,
    - logging estruturado com pino,
    - tratamento de erro,
    - protecao de dado pessoal (hash de e-mail).

---

## Referencias Rapidas

- Enunciado da fase 3: `exercicios/fase-3/cenario-3-exercicios-fase-governanca.md`
- Consolidado da fase 3: `exercicios/fase-3/entregaveis/exercicio-fase-3-governanca.md`
- Codigo do harness (3.1): `exercicios/fase-3/entregaveis/src/services/response-validator.ts`
- Codigo de feedback (3.2): `exercicios/fase-3/entregaveis/src/functions/feedback/handler.ts`
