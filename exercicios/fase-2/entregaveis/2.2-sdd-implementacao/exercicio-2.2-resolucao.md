# Exercício 2.2 — Implementação de Spec com Spec Driven Development
**Papel:** Desenvolvedor  
**Autor:** Guilherme Borniotto  
**Data:** 18/06/2026  

---

## 1. `tasks.md` — Decomposição Atômica do Plan

**Derivado de:** `specs/query-endpoint/plan.md`  
**Aprovação pendente:** Tech Lead (Gate 2 — Tasks → Implement)

---

### TASK-001 — HTTP Trigger: Setup e Validação de Input
**Estimativa:** P | **Dependências:** nenhuma

**Descrição:** Criar o Azure Function HTTP trigger (POST `/api/query`) com validação Zod. Rejeitar requests inválidos com HTTP 400 antes de qualquer chamada a serviços externos.

**Critérios de aceite:**
- [ ] POST `/api/query` com `{ "question": "texto" }` retorna HTTP 200 (stub)
- [ ] Ausência do campo `question` retorna HTTP 400 com `{ "error": "validation_error", "details": [...] }`
- [ ] `question` vazio (`""`) retorna HTTP 400
- [ ] `question` com mais de 1000 caracteres retorna HTTP 400
- [ ] `sessionId` (UUID) é opcional — ausente não gera erro
- [ ] Todos os requests logados com pino (método, path, status, latência) — nunca `console.log`
- [ ] Nenhuma chamada a Azure OpenAI ou Azure AI Search nesta task

---

### TASK-002 — Embedding Service: Conversão de Pergunta em Vetor
**Estimativa:** M | **Dependências:** TASK-001

**Descrição:** Implementar `EmbeddingService.embed(question)` usando Azure OpenAI (`text-embedding-ada-002`) com retry exponential backoff.

**Critérios de aceite:**
- [ ] Retorna `number[]` de 1536 floats
- [ ] Retry em erros 429 e 5xx: 1s → 2s → 4s (máx 3 tentativas)
- [ ] Erro não-recuperável lança `EmbeddingError` (custom error de `src/shared/errors.ts`)
- [ ] Endpoint lido de `AZURE_OPENAI_ENDPOINT` — nunca hardcoded
- [ ] Chamada logada: modelo, latência, tokens

---

### TASK-003 — Search Service: Busca Top-5 no Azure AI Search
**Estimativa:** M | **Dependências:** TASK-002

**Descrição:** Implementar `SearchService.search(embedding)` retornando top-5 chunks com metadata de vigência (ADR-0003).

**Critérios de aceite:**
- [ ] Retorna `Chunk[]` com: `content`, `source_document`, `section`, `is_current_version`, `score`
- [ ] Chunks com `is_current_version: false` marcados como `[OBSOLETO]` no campo `source_document`
- [ ] Retry em erros transitórios (mesmo padrão de TASK-002)
- [ ] Index name e endpoint lidos de variáveis de ambiente

---

### TASK-004 — Prompt Builder: Montagem com Context Budget (ADR-0002)
**Estimativa:** M | **Dependências:** TASK-003

**Descrição:** Montar prompt respeitando budget: ~4K tokens system + ~8K chunks + pergunta.

**Critérios de aceite:**
- [ ] `PromptBuilder.build(question, chunks)` retorna `{ system: string, user: string }`
- [ ] System prompt lido de `prompts/system-prompt.md` — nunca hardcoded
- [ ] Chunks ordenados: rank1, rank3, rank2 (mitigação lost-in-the-middle do cenário 1)
- [ ] Total de tokens não ultrapassa 13.000 — chunks de menor score são truncados se necessário
- [ ] Chunks de documentos obsoletos sinalizados no prompt

---

### TASK-005 — Completion Service: Chamada ao GPT-4o
**Estimativa:** M | **Dependências:** TASK-004

**Critérios de aceite:**
- [ ] Timeout configurável via `COMPLETION_TIMEOUT_MS` (default: 25.000ms)
- [ ] Retry em erros 429 e 5xx: 2s → 4s → 8s
- [ ] Temperatura: 0 (respostas determinísticas — guardrail de produto)
- [ ] Erro de timeout lança `CompletionTimeoutError`

---

### TASK-006 — Response Builder: Schema com `source_document`
**Estimativa:** P | **Dependências:** TASK-005

**Critérios de aceite:**
- [ ] Schema: `{ answer, source_document: string[], confidence: "high"|"low", session_id? }`
- [ ] `source_document` **sempre presente**, mesmo vazio (`[]`) — nunca omitido (guardrail de produto)
- [ ] Response validada com Zod antes de retornar ao cliente

---

### TASK-007 — Integração: Wire All Services no Handler
**Estimativa:** M | **Dependências:** TASK-001 a TASK-006

**Critérios de aceite:**
- [ ] Fluxo completo: validação → embedding → search → prompt → completion → response
- [ ] Erros de qualquer service retornam HTTP 500 com `{ "error": "internal_error" }` — nunca expõem stack trace
- [ ] Latência total logada por etapa (embedding, search, completion separados)

---

### TASK-008 — Testes de Integração
**Estimativa:** G | **Dependências:** TASK-007

**Critérios de aceite:**
- [ ] VC-01: Latência simulada < 30s (mocks com delay controlado)
- [ ] VC-02: `source_document` presente em 100% das respostas
- [ ] VC-03: Query sobre carga perigosa + devolução retorna negativa explícita
- [ ] VC-04: Query sem match retorna mensagem padrão "não encontrado"
- [ ] Coverage mínimo: 80% de linhas

**Ordem:** TASK-001 → 002 → 003 → 004 → 005 → 006 → 007 → 008

---

## 2. Implementação da TASK-001

### `src/functions/query/validator.ts`

```typescript
import { z } from "zod";

export const QueryRequestSchema = z.object({
  question: z
    .string()
    .min(1, "question cannot be empty")
    .max(1000, "question exceeds maximum length of 1000 characters")
    .trim(),
  sessionId: z
    .string()
    .uuid("sessionId must be a valid UUID")
    .optional(),
});

export const QueryResponseSchema = z.object({
  answer: z.string(),
  source_document: z.array(z.string()),
  confidence: z.enum(["high", "low"]),
  session_id: z.string().uuid().optional(),
});

export type QueryRequest = z.infer<typeof QueryRequestSchema>;
export type QueryResponse = z.infer<typeof QueryResponseSchema>;

export function validateRequest(body: unknown): QueryRequest {
  return QueryRequestSchema.parse(body);
}

export function validateResponse(response: unknown): QueryResponse {
  return QueryResponseSchema.parse(response);
}
```

---

### `src/functions/query/handler.ts`

```typescript
import { app, HttpRequest, HttpResponseInit, InvocationContext } from "@azure/functions";
import { ZodError } from "zod";
import { validateRequest, validateResponse, QueryResponse } from "./validator";
import { logger } from "@shared/logger";

// TASK-001: HTTP trigger setup com validação de input.
// Services (embedding, search, completion) wired em TASK-007.
export async function queryHandler(
  request: HttpRequest,
  context: InvocationContext
): Promise<HttpResponseInit> {
  const start = Date.now();
  const log = logger.child({ functionName: "query", invocationId: context.invocationId });

  let body: unknown;

  try {
    body = await request.json();
  } catch {
    log.warn({ status: 400 }, "Failed to parse request body as JSON");
    return {
      status: 400,
      jsonBody: { error: "invalid_json", message: "Request body must be valid JSON" },
    };
  }

  let question: string;
  let sessionId: string | undefined;

  try {
    const validated = validateRequest(body);
    question = validated.question;
    sessionId = validated.sessionId;
  } catch (err) {
    if (err instanceof ZodError) {
      log.warn({ status: 400, issues: err.issues }, "Input validation failed");
      return {
        status: 400,
        jsonBody: {
          error: "validation_error",
          details: err.issues.map((i) => ({ field: i.path.join("."), message: i.message })),
        },
      };
    }
    throw err;
  }

  log.info({ sessionId, questionLength: question.length }, "Query request received");

  // Stub — pipeline real wired em TASK-007
  const stubResponse: QueryResponse = {
    answer: "[STUB] Pipeline not yet implemented — see TASK-007",
    source_document: [],
    confidence: "low",
    ...(sessionId && { session_id: sessionId }),
  };

  const validated = validateResponse(stubResponse);
  const latencyMs = Date.now() - start;

  log.info({ status: 200, latencyMs, sessionId }, "Query response sent");

  return { status: 200, jsonBody: validated };
}

app.http("query", {
  methods: ["POST"],
  authLevel: "function",
  route: "query",
  handler: queryHandler,
});
```

---

## 3. Revisão Crítica do Código Gerado

### Problema 1 — `logger` importado de módulo inexistente (Crítico)

**Localização:** `handler.ts`, linha de import  
```typescript
import { logger } from "@shared/logger"; // src/shared/logger.ts ainda não existe
```

**Problema:** `src/shared/logger.ts` não existe neste estágio — o import quebra a compilação imediatamente. O Copilot assume que o módulo existe sem verificar o estado real do repositório.

**Ajuste:** Criar `src/shared/logger.ts` como pré-requisito da TASK-001, ou usar instância inline de pino até a task do shared logger:
```typescript
import pino from "pino";
const logger = pino({ name: "query-handler" });
```

---

### Problema 2 — `authLevel: "function"` bloqueia testes locais (Crítico)

**Localização:** `handler.ts`, registro da função  
```typescript
authLevel: "function", // exige x-functions-key em todo request
```

**Problema:** Em desenvolvimento local e nos testes de integração (TASK-008), isso força o mock do header de autenticação do Azure — complexidade desnecessária que contradiz o critério "nenhuma chamada a serviços reais nos testes".

**Ajuste:**
```typescript
authLevel: process.env.NODE_ENV === "production" ? "function" : "anonymous",
```

---

### Conclusão da revisão

| # | Severidade | Descrição | Ação |
|---|---|---|---|
| 1 | Crítico | Import de `logger` inexistente quebra compilação | Criar `src/shared/logger.ts` antes de rodar |
| 2 | Crítico | `authLevel: "function"` bloqueia testes locais | Usar env-based auth level |

O código é funcionalmente correto na lógica de validação Zod e no tratamento de erros HTTP, mas os 2 problemas acima impediriam o merge em uma code review real.
