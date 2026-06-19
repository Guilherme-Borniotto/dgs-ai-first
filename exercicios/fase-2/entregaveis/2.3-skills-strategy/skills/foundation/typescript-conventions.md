# SKILL: typescript-conventions
**Nível:** Foundation  
**Autor:** Guilherme Borniotto (Dev) — gerado com GitHub Copilot  
**Data:** 18/06/2026  
**Projeto:** NovaTech Assistant  

---

## Contexto — Quando usar esta skill

Esta skill se aplica **sempre que qualquer arquivo TypeScript for criado ou modificado** neste projeto. Ela é a base de todas as outras skills — leia-a antes de ler qualquer skill de nível Domain ou Artifact.

**Frase-ativação para agentes:**
> "Quando gerar qualquer arquivo `.ts` ou `.tsx` neste projeto, siga as convenções desta skill antes de qualquer outra."

**Dependências:** nenhuma — esta é a skill raiz.

---

## Regras Prescritivas

### 1. TypeScript Strict Mode é obrigatório
O `tsconfig.json` tem `"strict": true`. Isso implica:
- `noImplicitAny`: todo parâmetro e variável deve ter tipo explícito ou inferível
- `strictNullChecks`: `null` e `undefined` nunca são atribuídos implicitamente
- `noImplicitReturns`: toda função com retorno tipado deve retornar em todos os caminhos

### 2. Imports são sempre absolutos (caminho de módulo, nunca caminho relativo profundo)
Use aliases configurados no `tsconfig.json`. Caminhos relativos são permitidos apenas dentro do mesmo diretório.

### 3. Tipos de domínio vivem em `src/shared/types.ts`
Nunca defina tipos de domínio (ex: `QueryRequest`, `Chunk`, `CustomerTier`) inline em arquivos de função ou service. Importe de `src/shared/types.ts`.

### 4. Variáveis de ambiente nunca são acessadas diretamente com `process.env`
Toda variável de ambiente é lida e validada em `src/shared/config.ts`. Outros módulos importam de `config.ts`, nunca de `process.env` diretamente.

### 5. `console.log` é proibido — use sempre o logger pino
Importe o logger de `src/shared/logger.ts`. Nunca use `console.log`, `console.error`, `console.warn`.

### 6. Exports nomeados, nunca default exports
`export default` é proibido. Use `export const` ou `export function` sempre.

### 7. Nomenclatura
- **Arquivos:** `kebab-case.ts` (ex: `prompt-builder.ts`, `response-validator.ts`)
- **Classes:** `PascalCase`
- **Funções e variáveis:** `camelCase`
- **Constantes de módulo:** `SCREAMING_SNAKE_CASE`
- **Tipos e interfaces:** `PascalCase` com sufixo descritivo (ex: `QueryRequest`, `SearchResult`, `EmbeddingError`)

---

## Exemplos

### Imports — DO ✅

```typescript
// Absoluto — configurado via tsconfig paths
import { logger } from "@shared/logger";
import { QueryRequest, Chunk } from "@shared/types";
import { config } from "@shared/config";

// Relativo apenas dentro do mesmo diretório
import { validateRequest } from "./validator";
```

### Imports — DON'T ❌

```typescript
// Caminho relativo profundo — frágil e difícil de refatorar
import { logger } from "../../../shared/logger";

// Import de process.env direto — viola regra 4
const endpoint = process.env.AZURE_OPENAI_ENDPOINT!;
```

---

### Variáveis de ambiente — DO ✅

```typescript
// src/shared/config.ts
import { z } from "zod";

const envSchema = z.object({
  AZURE_OPENAI_ENDPOINT: z.string().url(),
  AZURE_OPENAI_DEPLOYMENT_NAME: z.string().min(1),
  AZURE_SEARCH_ENDPOINT: z.string().url(),
  AZURE_SEARCH_INDEX_NAME: z.string().min(1),
  COMPLETION_TIMEOUT_MS: z.coerce.number().default(25000),
});

export const config = envSchema.parse(process.env);
```

```typescript
// src/services/completion.ts — consome config, nunca process.env
import { config } from "@shared/config";

const client = new AzureOpenAI({ endpoint: config.AZURE_OPENAI_ENDPOINT });
```

### Variáveis de ambiente — DON'T ❌

```typescript
// Acesso direto — não validado, pode ser undefined silenciosamente
const endpoint = process.env.AZURE_OPENAI_ENDPOINT!;

// Non-null assertion (!) disfarça falta de validação
const apiKey = process.env.API_KEY!;
```

---

### Logging — DO ✅

```typescript
import { logger } from "@shared/logger";

const log = logger.child({ service: "embedding" });

log.info({ model: "text-embedding-ada-002", latencyMs: 120 }, "Embedding generated");
log.error({ err, questionLength: question.length }, "Embedding failed");
```

### Logging — DON'T ❌

```typescript
// Nunca — viola regra 5
console.log("Embedding generated", { latencyMs: 120 });
console.error("Failed:", err);

// Nunca — perde estrutura (não é JSON, não tem correlação)
logger.info(`Embedding generated in ${latencyMs}ms`);
```

---

### Exports — DO ✅

```typescript
// Named exports sempre
export const MAX_QUESTION_LENGTH = 1000;
export function validateRequest(body: unknown): QueryRequest { ... }
export type { QueryRequest, QueryResponse };
```

### Exports — DON'T ❌

```typescript
// Default export — proibido
export default function handler() { ... }

// Export de objeto anônimo — perde identidade no import
export default { validateRequest, MAX_QUESTION_LENGTH };
```

---

### Tipos — DO ✅

```typescript
// src/shared/types.ts — fonte única de verdade para tipos de domínio
export type CustomerTier = "Gold" | "Silver" | "Standard";

export interface Chunk {
  content: string;
  source_document: string;
  section: string;
  is_current_version: boolean;
  score: number;
}

export interface QueryResponse {
  answer: string;
  source_document: string[];
  confidence: "high" | "low";
  session_id?: string;
}
```

### Tipos — DON'T ❌

```typescript
// Tipo inline em handler — não reutilizável, duplicado em outros arquivos
async function handler(req: { body: { question: string; sessionId?: string } }) { ... }

// `any` explícito — viola strict mode
function parseBody(raw: any): any { ... }
```

---

## Anti-padrões Comuns de IA

Os seguintes padrões são gerados frequentemente por LLMs e **não são aceitos** neste projeto:

| Anti-padrão | Por que é errado | Correto |
|---|---|---|
| `console.log(...)` | Viola regra de logging — não é estruturado, não tem correlação | `log.info({ ... }, "mensagem")` |
| `process.env.VAR!` | Non-null assertion esconde runtime error se var não está definida | Validar via `config.ts` com Zod |
| `export default function` | Impossível fazer tree-shaking, perde nome no stack trace | `export function nomeExplicito` |
| `import X from "../../shared/..."` | Caminho relativo profundo quebra com refatoração | Import absoluto via alias |
| `const x: any = ...` | Perde tipagem, viola strict mode | Tipar corretamente ou usar `unknown` + type guard |
| Tipo de domínio inline | Duplicação, divergência entre arquivos | Definir em `src/shared/types.ts` |

---

## Referências

- `tsconfig.json` — configuração de strict mode e path aliases
- `src/shared/config.ts` — validação de variáveis de ambiente
- `src/shared/logger.ts` — instância de pino
- `src/shared/types.ts` — tipos de domínio
- `src/shared/errors.ts` — custom errors do projeto
- **Skills que dependem desta:** todas as skills Domain e Artifact
