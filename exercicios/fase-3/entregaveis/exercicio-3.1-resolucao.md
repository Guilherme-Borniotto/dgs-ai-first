# Exercicio 3.1 - Structured output e verificacoes deterministicas

**Papel:** Desenvolvedor  
**Autor:** Guilherme Borniotto  
**Data:** 09/07/2026

---

## 1. Structured output com Zod

Arquivo implementado: `src/services/response-validator.ts`

Schema definido para forcar resposta validavel em JSON fixo:

```typescript
export const StructuredResponseSchema = z
  .object({
    answer: z.string().min(1, "answer is required"),
    source_document: z
      .array(z.string().min(1, "source document entry cannot be empty"))
      .min(1, "source_document must contain at least one source"),
    confidence_score: z.number().min(0).max(1),
  })
  .strict();
```

Decisoes de implementacao:
- `.strict()` para rejeitar campos extras nao previstos.
- `source_document` com `min(1)` para evitar resposta sem fonte util.
- `confidence_score` como numero entre 0 e 1 para facilitar validacao automatica.

---

## 2. Harness deterministico (alem do prompt)

Arquivo implementado: `src/services/response-validator.ts`

### Guardrail 1 - `source_document` obrigatorio

Regras aplicadas:
- Se `source_document` estiver ausente no payload bruto, resposta e rejeitada imediatamente.
- Se schema falhar (ex.: campo ausente, tipo invalido, lista vazia), resposta e rejeitada.
- Em qualquer falha, o sistema retorna fallback seguro e registra o motivo em log estruturado.

### Guardrail 2 - carga perigosa + devolucao exige negativa

Regras aplicadas:
- O texto e normalizado (case-insensitive e sem acentos) antes das verificacoes.
- Se a resposta tratar ao mesmo tempo de carga perigosa e devolucao:
  - Se houver afirmacao de devolucao permitida, bloqueia.
  - Se nao houver negativa explicita, bloqueia.
- Em bloqueio, o retorno e fallback seguro com `confidence_score: 0`.

Mensagem segura padrao:

```text
Nao foi possivel validar a resposta com seguranca. Encaminhe para analise humana da equipe de atendimento.
```

---

## 3. Code review rapido (Claude) + correcoes

### Problema 1 identificado

**Achado:** O schema inicial aceitava campos extras silenciosamente (comportamento padrao do Zod sem strict).  
**Risco:** Payload pode carregar dados nao esperados e passar no parse sem sinalizar desvio de contrato.  
**Correcao aplicada:** Adicionado `.strict()` no schema.

### Problema 2 identificado

**Achado:** A validacao textual inicial para "carga perigosa + devolucao" nao cobria variacoes com acento, caixa e flexao.  
**Risco:** Respostas indevidas poderiam escapar por variacao linguistica simples.  
**Correcao aplicada:** Normalizacao textual (`normalize("NFD")` + remocao de diacriticos + lowercase) e regex por familias de termos.

### Problema 3 identificado (extra)

**Achado:** Fallback unico compartilhado por referencia poderia ser alterado por engano em runtime.  
**Risco:** Drift de resposta padrao entre chamadas.  
**Correcao aplicada:** `buildFallbackResponse()` retorna copia nova do objeto.

---

## 4. Distincao prompt x codigo deterministico

- Prompt continua sendo camada probabilistica (orienta comportamento do modelo).
- Codigo em `response-validator.ts` e camada deterministica (valida estrutura e bloqueia saidas proibidas).
- Resultado: mesmo que o modelo "esqueca" a fonte ou responda incorretamente sobre devolucao de carga perigosa, a resposta nao passa para o usuario final.
