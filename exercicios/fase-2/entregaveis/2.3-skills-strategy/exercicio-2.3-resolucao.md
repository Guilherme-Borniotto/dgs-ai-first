# Exercício 2.3 — Definição de Estratégia de Skills do Projeto
**Papel:** Desenvolvedor  
**Autor:** Guilherme Borniotto  
**Data:** 18/06/2026  

---

## 1. Árvore de Skills — Foundation → Domain → Artifact

```
skills/
├── foundation/
│   ├── typescript-conventions.md    ← BASE: consumida por todas as outras skills
│   ├── error-handling.md
│   └── project-structure.md
│
├── domain/
│   ├── azure-functions-endpoint.md
│   ├── azure-ai-search-integration.md
│   ├── react-components.md
│   └── testing-patterns.md
│
└── artifact/
    ├── create-rag-endpoint.md
    ├── create-integration-test.md
    └── create-react-card.md
```

---

## 2. Catálogo de Skills

### FOUNDATION

| Skill | Frase-ativação | Quem cria | Quem consome | Frequência | Dependências |
|---|---|---|---|---|---|
| `typescript-conventions` | "Ao gerar qualquer arquivo `.ts` neste projeto" | Tech Lead | Dev, Copilot, Claude Code | Alta — toda geração de código | Nenhuma (é a base) |
| `error-handling` | "Ao implementar qualquer service com chamadas externas" | Tech Lead | Dev, Copilot | Alta — todos os services Azure | `typescript-conventions` |
| `project-structure` | "Ao criar um novo arquivo ou decidir onde colocá-lo" | Tech Lead | Dev, QA, PS, Copilot | Média — onboarding e novos módulos | Nenhuma |

### DOMAIN

| Skill | Frase-ativação | Quem cria | Quem consome | Frequência | Dependências |
|---|---|---|---|---|---|
| `azure-functions-endpoint` | "Ao criar ou modificar um Azure Function HTTP trigger" | Tech Lead | Dev, Copilot | Alta — 3+ endpoints no projeto | `typescript-conventions`, `error-handling` |
| `azure-ai-search-integration` | "Ao implementar chamada ao Azure AI Search" | Tech Lead + Dev Sênior | Dev, Copilot | Média — pipeline e query endpoint | `typescript-conventions`, `error-handling` |
| `react-components` | "Ao criar ou modificar componente React do painel web" | Dev Sênior | Dev, Copilot | Média — painel web tem escopo limitado | `typescript-conventions` |
| `testing-patterns` | "Ao escrever qualquer teste neste projeto" | QA | Dev, QA, Copilot | Alta — toda task tem testes | `typescript-conventions`, `project-structure` |

### ARTIFACT

| Skill | Frase-ativação | Quem cria | Quem consome | Frequência | Dependências |
|---|---|---|---|---|---|
| `create-rag-endpoint` | "Crie um endpoint RAG para [funcionalidade]" | Tech Lead + Dev Sênior | Dev Pleno, Copilot | Baixa — 1-2 endpoints RAG no projeto | `azure-functions-endpoint`, `azure-ai-search-integration`, `error-handling` |
| `create-integration-test` | "Crie testes de integração para [endpoint/service]" | QA + Dev Sênior | Dev, QA, Copilot | Alta — uma por endpoint | `testing-patterns`, `project-structure` |
| `create-react-card` | "Crie um card React para exibir [tipo de dado]" | Dev Sênior | Dev Pleno, Copilot | Baixa — 2-3 cards no painel web | `react-components`, `typescript-conventions` |

---

## 3. Sequência de Criação por Sprint

| Sprint | Skills a criar | Razão |
|---|---|---|
| Sprint 0 (antes do código) | `typescript-conventions`, `project-structure`, `error-handling` | Desbloqueiam todo o resto |
| Sprint 1 (TASK-001 a TASK-007) | `azure-functions-endpoint`, `azure-ai-search-integration`, `testing-patterns` | Necessárias para as primeiras implementações |
| Sprint 2 (artefatos) | `create-rag-endpoint`, `create-integration-test` | Quando o padrão estiver consolidado |
| Sprint 3 (painel web) | `react-components`, `create-react-card` | Escopo do painel web começa aqui |

---

## 4. SKILL.md — `typescript-conventions` (Foundation)

> Gerado com GitHub Copilot. Este é o arquivo `skills/foundation/typescript-conventions.md`.

---

### Contexto — Quando usar

Esta skill se aplica **sempre que qualquer arquivo TypeScript for criado ou modificado** neste projeto. É a skill raiz — leia-a antes de qualquer skill de nível Domain ou Artifact.

**Frase-ativação para agentes:**
> "Quando gerar qualquer arquivo `.ts` ou `.tsx` neste projeto, siga as convenções desta skill antes de qualquer outra."

---

### Regras Prescritivas

1. **TypeScript Strict Mode é obrigatório** — `tsconfig.json` tem `"strict": true`: sem `noImplicitAny`, sem `strictNullChecks` violados, toda função com retorno tipado retorna em todos os caminhos.

2. **Imports são sempre absolutos via aliases** configurados no `tsconfig.json`. Caminhos relativos são permitidos apenas dentro do mesmo diretório.

3. **Tipos de domínio vivem em `src/shared/types.ts`** — nunca defina `QueryRequest`, `Chunk`, `CustomerTier` inline em handlers ou services.

4. **Variáveis de ambiente nunca com `process.env` direto** — toda variável é lida e validada em `src/shared/config.ts` com Zod. Outros módulos importam de `config.ts`.

5. **`console.log` é proibido** — use sempre pino importado de `src/shared/logger.ts`.

6. **Exports nomeados, nunca default exports** — `export default` é proibido. Use `export const` ou `export function`.

7. **Nomenclatura:** arquivos `kebab-case.ts`, classes `PascalCase`, funções e variáveis `camelCase`, constantes de módulo `SCREAMING_SNAKE_CASE`, tipos e interfaces `PascalCase` com sufixo descritivo.

---

### Exemplos

#### Imports — DO ✅
```typescript
import { logger } from "@shared/logger";
import { QueryRequest, Chunk } from "@shared/types";
import { config } from "@shared/config";
import { validateRequest } from "./validator"; // relativo ok — mesmo diretório
```

#### Imports — DON'T ❌
```typescript
import { logger } from "../../../shared/logger"; // caminho relativo profundo
const endpoint = process.env.AZURE_OPENAI_ENDPOINT!; // process.env direto
```

---

#### Variáveis de ambiente — DO ✅
```typescript
// src/shared/config.ts
import { z } from "zod";

const envSchema = z.object({
  AZURE_OPENAI_ENDPOINT: z.string().url(),
  AZURE_OPENAI_DEPLOYMENT_NAME: z.string().min(1),
  COMPLETION_TIMEOUT_MS: z.coerce.number().default(25000),
});

export const config = envSchema.parse(process.env);
```

```typescript
// consumer
import { config } from "@shared/config";
const client = new AzureOpenAI({ endpoint: config.AZURE_OPENAI_ENDPOINT });
```

#### Variáveis de ambiente — DON'T ❌
```typescript
const endpoint = process.env.AZURE_OPENAI_ENDPOINT!; // non-null assertion esconde runtime error
```

---

#### Logging — DO ✅
```typescript
import { logger } from "@shared/logger";
const log = logger.child({ service: "embedding" });

log.info({ model: "text-embedding-ada-002", latencyMs: 120 }, "Embedding generated");
log.error({ err, questionLength: question.length }, "Embedding failed");
```

#### Logging — DON'T ❌
```typescript
console.log("Embedding generated", { latencyMs: 120 }); // proibido
logger.info(`Embedding generated in ${latencyMs}ms`);   // perde estrutura JSON
```

---

#### Exports — DO ✅
```typescript
export const MAX_QUESTION_LENGTH = 1000;
export function validateRequest(body: unknown): QueryRequest { ... }
export type { QueryRequest, QueryResponse };
```

#### Exports — DON'T ❌
```typescript
export default function handler() { ... }      // default export proibido
export default { validateRequest, MAX_QUESTION_LENGTH }; // objeto anônimo perde identidade
```

---

### Anti-padrões Comuns de IA

| Anti-padrão | Por que é errado | Correto |
|---|---|---|
| `console.log(...)` | Não estruturado, sem correlação, sem nível | `log.info({ ... }, "mensagem")` |
| `process.env.VAR!` | Non-null assertion esconde undefined silencioso | Validar via `config.ts` com Zod |
| `export default function` | Perde nome no stack trace, impossibilita tree-shaking | `export function nomeExplicito` |
| Import relativo profundo `../../shared/...` | Quebra em refatoração | Import absoluto via alias |
| `const x: any = ...` | Perde tipagem, viola strict mode | Tipar corretamente ou usar `unknown` + type guard |
| Tipo de domínio inline no handler | Duplicação e divergência | Definir em `src/shared/types.ts` |

---

### Referências

- `tsconfig.json` — strict mode e path aliases
- `src/shared/config.ts` — validação de variáveis de ambiente
- `src/shared/logger.ts` — instância de pino
- `src/shared/types.ts` — tipos de domínio
- **Skills que dependem desta:** todas as skills Domain e Artifact
