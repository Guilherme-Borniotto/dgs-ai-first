# Tasks — Query Endpoint
**Módulo:** `query-endpoint`  
**Autor:** Guilherme Borniotto (Dev)  
**Gerado com apoio de:** GitHub Copilot  
**Aprovação:** Tech Lead  
**Data:** 18/06/2026  
**Status:** Aguardando aprovação do Tech Lead (Gate 2 — Tasks → Implement)

---

## Referências
- **Plan:** `specs/query-endpoint/plan.md`
- **Requirements:** `specs/query-endpoint/requirements.md`
- **ADR-0002:** Context budget (~4K system + ~8K chunks + pergunta)
- **ADR-0003:** Metadado de vigência para documentos contraditórios

---

## TASK-001 — HTTP Trigger: Setup e Validação de Input
**ID:** TASK-001  
**Estimativa:** P (Pequeno — ≤ 4h)  
**Dependências:** nenhuma (pode iniciar imediatamente)  

**Descrição:**  
Criar o Azure Function HTTP trigger (POST `/api/query`) com validação de input usando Zod. O handler deve rejeitar requests inválidos com HTTP 400 e retornar o schema de erro padronizado antes de qualquer chamada a serviços externos.

**Critérios de aceite:**
- [ ] POST `/api/query` com body `{ "question": "texto" }` retorna HTTP 200 (stub de resposta por ora)
- [ ] POST `/api/query` sem campo `question` retorna HTTP 400 com `{ "error": "validation_error", "details": [...] }`
- [ ] POST `/api/query` com `question` vazio (`""`) retorna HTTP 400
- [ ] POST `/api/query` com `question` com mais de 1000 caracteres retorna HTTP 400
- [ ] Campo `sessionId` (UUID) é opcional — ausente não gera erro
- [ ] Todos os requests são logados com pino: método, path, status, latência (nunca `console.log`)
- [ ] Nenhuma chamada a Azure OpenAI ou Azure AI Search nesta task (stub/placeholder apenas)

**Arquivos a criar:**
- `src/functions/query/handler.ts`
- `src/functions/query/validator.ts`

---

## TASK-002 — Embedding Service: Conversão de Pergunta em Vetor
**ID:** TASK-002  
**Estimativa:** M (Médio — 4h–1d)  
**Dependências:** TASK-001 (handler precisa existir para integrar o service)  

**Descrição:**  
Implementar o service que converte a pergunta do atendente em embedding usando Azure OpenAI (`text-embedding-ada-002`). Deve incluir retry com exponential backoff para erros transitórios.

**Critérios de aceite:**
- [ ] `EmbeddingService.embed(question: string): Promise<number[]>` retorna array de 1536 floats
- [ ] Retry automático em erros 429 (rate limit) e 5xx com backoff: 1s → 2s → 4s (máx 3 tentativas)
- [ ] Erro não-recuperável lança `EmbeddingError` (custom error definido em `src/shared/errors.ts`)
- [ ] Connection string lida de variável de ambiente `AZURE_OPENAI_ENDPOINT` — nunca hardcoded
- [ ] Chamada logada com pino: modelo, latência, número de tokens

**Arquivos a criar:**
- `src/services/embedding.ts`

---

## TASK-003 — Search Service: Busca top-5 no Azure AI Search
**ID:** TASK-003  
**Estimativa:** M (Médio — 4h–1d)  
**Dependências:** TASK-002 (precisa do embedding para buscar)  

**Descrição:**  
Implementar o service que recebe o embedding e retorna os top-5 chunks mais relevantes do Azure AI Search, incluindo o metadata de vigência (campo `is_current_version`) conforme ADR-0003.

**Critérios de aceite:**
- [ ] `SearchService.search(embedding: number[]): Promise<Chunk[]>` retorna array de até 5 chunks
- [ ] Cada `Chunk` contém: `content`, `source_document`, `section`, `is_current_version`, `score`
- [ ] Chunks com `is_current_version: false` são incluídos no resultado mas marcados com `[OBSOLETO]` no campo `source_document`
- [ ] Retry em erros transitórios (mesmo padrão de TASK-002)
- [ ] Index name lido de variável de ambiente `AZURE_SEARCH_INDEX_NAME`
- [ ] Search endpoint lido de variável de ambiente `AZURE_SEARCH_ENDPOINT`

**Arquivos a criar:**
- `src/services/search.ts`

---

## TASK-004 — Prompt Builder: Montagem do Prompt com Context Budget
**ID:** TASK-004  
**Estimativa:** M (Médio — 4h–1d)  
**Dependências:** TASK-003 (precisa dos chunks para montar o prompt)  

**Descrição:**  
Implementar o builder que monta o prompt final enviado ao GPT-4o, respeitando o context budget definido na ADR-0002: ~4K tokens para system prompt + ~8K tokens para chunks + pergunta.

**Critérios de aceite:**
- [ ] `PromptBuilder.build(question: string, chunks: Chunk[]): BuiltPrompt` retorna `{ system: string, user: string }`
- [ ] System prompt lido de `prompts/system-prompt.md` (nunca hardcoded)
- [ ] Chunks são ordenados por score (rank1, rank3, rank2 — padrão "lost-in-the-middle" mitigation do cenário 1)
- [ ] Total de tokens estimado não ultrapassa 13.000 (4K system + 8K chunks + 1K pergunta/histórico)
- [ ] Se soma de chunks ultrapassar 8K tokens, truncar chunks de menor score até caber
- [ ] Chunks de documentos obsoletos são sinalizados no prompt: "ATENÇÃO: este trecho vem da versão anterior de [documento]"

**Arquivos a criar:**
- `src/services/prompt-builder.ts`

---

## TASK-005 — Completion Service: Chamada ao GPT-4o com Retry
**ID:** TASK-005  
**Estimativa:** M (Médio — 4h–1d)  
**Dependências:** TASK-004 (precisa do prompt montado)  

**Descrição:**  
Implementar o service que envia o prompt ao GPT-4o via Azure OpenAI e retorna a completion. Deve incluir retry com exponential backoff e timeout configurável.

**Critérios de aceite:**
- [ ] `CompletionService.complete(prompt: BuiltPrompt): Promise<string>` retorna texto da resposta
- [ ] Timeout configurável via variável de ambiente `COMPLETION_TIMEOUT_MS` (default: 25000ms)
- [ ] Retry em erros 429 e 5xx (máx 3 tentativas, backoff: 2s → 4s → 8s)
- [ ] Erro de timeout lança `CompletionTimeoutError`
- [ ] Temperatura: 0 (respostas determinísticas — guardrail de produto)
- [ ] Modelo: `gpt-4o` lido de `AZURE_OPENAI_DEPLOYMENT_NAME`

**Arquivos a criar:**
- `src/services/completion.ts`

---

## TASK-006 — Response Builder: Montagem da Resposta com `source_document`
**ID:** TASK-006  
**Estimativa:** P (Pequeno — ≤ 4h)  
**Dependências:** TASK-005 (precisa da completion para montar a resposta)  

**Descrição:**  
Implementar o builder que monta o JSON de resposta final da API, sempre incluindo o campo `source_document` com as fontes usadas.

**Critérios de aceite:**
- [ ] Resposta segue o schema: `{ answer: string, source_document: string[], confidence: "high"|"low", session_id?: string }`
- [ ] `source_document` sempre presente, mesmo vazio (`[]`) — nunca omitido
- [ ] Quando a completion inclui sinalização de baixa confiança, `confidence` = `"low"`
- [ ] Response validada com Zod antes de retornar ao cliente (nunca retornar schema inválido)

**Arquivos a criar:**
- `src/functions/query/response-builder.ts`

---

## TASK-007 — Integração: Wire All Services no Handler
**ID:** TASK-007  
**Estimativa:** M (Médio — 4h–1d)  
**Dependências:** TASK-001, TASK-002, TASK-003, TASK-004, TASK-005, TASK-006 (todas)  

**Descrição:**  
Integrar todos os services no handler do query endpoint, implementando o fluxo completo: validação → embedding → search → prompt → completion → response.

**Critérios de aceite:**
- [ ] Fluxo completo executa sem erro para pergunta válida com chunks disponíveis
- [ ] Erros de qualquer service são capturados e retornam HTTP 500 com `{ "error": "internal_error" }` — nunca expõem stack trace
- [ ] Latência total logada em pino (tempo de embedding + search + completion separados)
- [ ] `sessionId` propagado por todo o fluxo para correlação de logs

**Arquivos a modificar:**
- `src/functions/query/handler.ts` (adicionar integração dos services)

---

## TASK-008 — Testes de Integração do Query Endpoint
**ID:** TASK-008  
**Estimativa:** G (Grande — 1d–2d)  
**Dependências:** TASK-007 (integração completa)  

**Descrição:**  
Escrever testes de integração cobrindo os verification criteria do `requirements.md` (VC-01 a VC-04). Usar msw para mockar APIs externas (Azure OpenAI, Azure AI Search). Usar fixtures de `tests/fixtures/`.

**Critérios de aceite:**
- [ ] VC-01: Teste de latência (mock de services com delay controlado — 95% < 30s simulado)
- [ ] VC-02: Teste que `source_document` está presente em 100% das respostas (inclui respostas sem match)
- [ ] VC-03: Teste de query sobre carga perigosa + devolução retorna negativa explícita
- [ ] VC-04: Teste de query sem match retorna mensagem padrão "não encontrado"
- [ ] Coverage mínimo: 80% de linhas (threshold configurado no `vitest.config.ts`)

**Arquivos a criar:**
- `tests/integration/query-endpoint.test.ts`
- `tests/fixtures/chunks.ts` (chunks simulados)
- `tests/fixtures/queries.ts` (perguntas de teste)
- `tests/fixtures/expected-responses.ts` (respostas esperadas)

---

## Mapa de Dependências

```
TASK-001 (handler + validator)
    └── TASK-002 (embedding)
            └── TASK-003 (search)
                    └── TASK-004 (prompt builder)
                            └── TASK-005 (completion)
                                    └── TASK-006 (response builder)
                                            └── TASK-007 (integração)
                                                    └── TASK-008 (testes)
```

**Ordem de implementação sugerida:** 001 → 002 → 003 → 004 → 005 → 006 → 007 → 008

**TASK-001 está pronta para iniciar** (sem dependências). Ver implementação em `src/functions/query/`.
