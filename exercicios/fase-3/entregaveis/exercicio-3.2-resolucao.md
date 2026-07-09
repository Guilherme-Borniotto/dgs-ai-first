# Exercicio 3.2 - Revisao critica de codigo gerado por IA

**Papel:** Desenvolvedor  
**Autor:** Guilherme Borniotto  
**Data:** 09/07/2026

---

## 1. Minha revisao inicial (antes do Claude)

Codigo revisado (simulado no enunciado): modulo de feedback com Azure Function.

### Problemas encontrados e classificacao

| # | Problema | Classificacao |
|---|---|---|
| 1 | Uso de `as any` no body sem schema | Violacao AGENTS.md + bug potencial |
| 2 | `console.log` em vez de logger estruturado pino | Violacao AGENTS.md |
| 3 | `require` dinamico de `@azure/cosmos` dentro da funcao | Violacao AGENTS.md + risco de manutencao |
| 4 | Log contendo `attendantEmail` (dado pessoal) | Problema de seguranca / privacidade |
| 5 | Nao trata JSON invalido nem erros de validacao com HTTP 400 | Bug potencial |
| 6 | Nao trata ausencia de `COSMOS_CONNECTION_STRING` | Bug potencial |
| 7 | Nao trata erro de persistencia no Cosmos com retorno controlado | Bug potencial |

---

## 2. Segunda revisao (Claude)

Pontos reforcados na segunda revisao:
- Confirmou os 4 pontos minimos obrigatorios (any, console.log, require dinamico, PII no log).
- Sugeriu reduzir exposicao de PII persistindo hash de e-mail, nao valor bruto.
- Sugeriu schema Zod estrito para rejeitar campos extras nao esperados.
- Sugeriu logar apenas metadados operacionais (status, rating, queryId, hasComment).

---

## 3. Comparacao humano x Claude

| Tema | Minha revisao | Revisao Claude | Resultado |
|---|---|---|---|
| Validacao de entrada | Identificado | Identificado | Concordancia total |
| Logging (pino vs console) | Identificado | Identificado | Concordancia total |
| Import dinamico | Identificado | Identificado | Concordancia total |
| PII no log | Identificado | Identificado | Concordancia total |
| Privacidade na persistencia | Parcial | Mais profundo (hash) | Correcao adotada |
| Controle de erro operacional | Identificado | Identificado | Concordancia total |

Conclusao da comparacao:
- A revisao humana cobriu os problemas principais.
- A revisao Claude agregou melhoria de minimizacao de PII em armazenamento.
- As correcoes finais incorporam os dois pontos de vista.

---

## 4. Codigo reescrito (seguindo AGENTS.md)

Arquivos implementados:
- `src/functions/feedback/handler.ts`
- `src/functions/feedback/validator.ts`
- `src/shared/logger.ts`

### Ajustes aplicados

- Remocao de `as any`, com validacao Zod em `validator.ts`.
- Substituicao de `console.log` por logger pino (`src/shared/logger.ts`).
- Remocao de `require` dinamico; `CosmosClient` importado no topo.
- Remocao de PII do log; logs contem somente campos operacionais.
- `attendantEmail` e transformado em hash SHA-256 antes de persistir.
- Tratamento robusto para:
  - JSON invalido (`400 invalid_json`)
  - Erro de validacao (`400 validation_error`)
  - Cosmos nao configurado (`500 internal_error`)
  - Falha de persistencia (`500 internal_error`)

---

## 5. Resultado final

O modulo de feedback foi reescrito com:
- tipagem estrita,
- validacao deterministica de entrada,
- logging estruturado sem exposicao de dados pessoais,
- imports estaticos no topo,
- e tratamento de erro apropriado para producao.

Com isso, os requisitos do exercicio 3.2 e as regras resumidas do AGENTS.md foram atendidos.
