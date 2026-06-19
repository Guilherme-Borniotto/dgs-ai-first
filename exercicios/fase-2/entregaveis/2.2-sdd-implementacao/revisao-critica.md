# Exercício 2.2 — Revisão Crítica do Código Gerado
**Autor:** Guilherme Borniotto  
**Data:** 18/06/2026  

---

## Código Revisado

Arquivos gerados com apoio do GitHub Copilot:
- `src/functions/query/handler.ts`
- `src/functions/query/validator.ts`

---

## Ponto 1 — `logger` importado de caminho relativo não garantido

**Localização:** `handler.ts`, linha 4  
```typescript
import { logger } from "../../shared/logger";
```

**Problema:**  
O arquivo `src/shared/logger.ts` não existe ainda (será criado em uma task separada). No estado atual do repositório, essa importação quebra a compilação. O Copilot assume que o módulo existe sem verificar o estado real do repositório.

**Ajuste proposto:**  
Criar um `logger` inline mínimo no handler para a TASK-001, e substituir pela importação de `src/shared/logger.ts` somente quando essa task estiver concluída. Alternativamente, criar o arquivo `src/shared/logger.ts` como dependência explícita da TASK-001.

```typescript
// Versão corrigida enquanto src/shared/logger.ts não existe:
import pino from "pino";
const logger = pino({ name: "query-handler" });
```

**Por que é crítico:** Uma importação quebrada impede qualquer execução ou teste da função, bloqueando o ciclo de feedback rápido da TASK-001.

---

## Ponto 2 — `authLevel: "function"` pode bloquear testes locais

**Localização:** `handler.ts`, linha 59  
```typescript
  authLevel: "function",
```

**Problema:**  
Com `authLevel: "function"`, o Azure Functions runtime exige um Function Key no header `x-functions-key` para qualquer request. Em ambiente de desenvolvimento local (via `func start`), isso não é necessário e adiciona fricção nos testes. Pior: nos testes de integração do Vitest, seria necessário mockar o header de autenticação.

**Ajuste proposto:**  
Usar `authLevel: "anonymous"` para TASK-001 (desenvolvimento) e mudar para `"function"` via configuração de ambiente antes do deploy:

```typescript
// Correto para desenvolvimento — configurado via environment antes de produção
authLevel: process.env.NODE_ENV === "production" ? "function" : "anonymous",
```

Ou, mais limpo: definir o auth level como variável de ambiente (`FUNCTION_AUTH_LEVEL`) lida em runtime, seguindo o padrão de `config.ts`.

**Por que é crítico:** Com `"function"` hardcoded, a TASK-008 (testes de integração) precisaria mockar autenticação do Azure — complexidade desnecessária que contradiz o critério "nenhuma chamada a serviços reais nos testes de integração".

---

## Pontos Adicionais de Qualidade (não críticos, mas relevantes para code review)

**P3 — Tipo de `body` no catch de JSON parse:**  
O Copilot gerou `catch { }` (catch sem variável) — válido em TypeScript 4.0+, mas o projeto usa `strict: true`. Alguns linters (ESLint com `@typescript-eslint`) preferem `catch (err: unknown)` explícito para garantir tipagem. Verificar configuração de ESLint do projeto.

**P4 — Stub response deveria ter `confidence: "low"` documentado:**  
O stub retorna `confidence: "low"` mas sem comentário explicando o motivo. Em uma code review real, um reviewer poderia questionar se isso é intencional ou bug. Adicionar comentário: `// Stub: confidence is always low until real pipeline (TASK-007) provides a score`.

---

## Resumo da Revisão

| # | Severidade | Arquivo | Descrição | Status |
|---|-----------|---------|-----------|--------|
| 1 | **Crítico** | `handler.ts:4` | Importação de `logger` inexistente quebra compilação | Ajustar antes de rodar |
| 2 | **Crítico** | `handler.ts:59` | `authLevel: "function"` bloqueia testes locais | Ajustar antes de TASK-008 |
| 3 | Baixo | `handler.ts:23` | `catch {}` sem tipo — verificar ESLint config | Verificar convenção do projeto |
| 4 | Baixo | `handler.ts:52` | Stub sem comentário explicativo | Adicionar comentário |

**Conclusão:** O código gerado pelo Copilot é funcionalmente correto na lógica de validação (Zod, tratamento de erros, schema de resposta), mas tem 2 problemas críticos que impediriam o merge em uma code review real: a importação quebrada e o auth level incorreto para desenvolvimento.
