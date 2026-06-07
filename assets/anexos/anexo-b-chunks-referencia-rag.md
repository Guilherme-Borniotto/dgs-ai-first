# Anexo B – Chunks de Referência e Gabarito de Retrieval

Este arquivo define os chunks esperados por pergunta do pipeline de RAG, servindo como gabarito para avaliar a qualidade do retrieval.

---

## Chunks por Documento

### POL-001 — Política de Devolução

**POL-001-A** (Prazo geral)
```
[Fonte: POL-001-politica-devolucao | Versão: 2.8 | Data: 20/02/2024 | Seção: 3.1 Prazo geral]

O prazo para solicitação de devolução é de 6 (seis) dias úteis contados a partir
da data de recebimento confirmada no sistema de tracking. A solicitação deve ser
registrada no Portal do Cliente com número do CT-e e fotos da mercadoria.
```

**POL-001-B** (Exceções — cargas IMO)
```
[Fonte: POL-001-politica-devolucao | Versão: 2.8 | Data: 20/02/2024 | Seção: 3.2 Exceções ao prazo geral]

NÃO são elegíveis para devolução pelo processo padrão:
- Cargas IMO classes 3, 6 e 8 (inflamáveis, tóxicas e corrosivas)
- Cargas refrigeradas com cadeia de frio rompida
- Cargas com lacre violado ou sinais de adulteração

Para essas situações, o atendente deve acionar a Gestão de Riscos (ramal 3800)
para análise e tratamento individualizado.
```

---

### PROC-042 v1 — Frete Especial (versão antiga, obsoleta)

**PROC-042-A** (Fórmula v1)
```
[Fonte: PROC-042-frete-especial-v1 | Versão: 1.0 | Data: 15/06/2023 | Seção: 2 Fórmula de cálculo]

Frete especial aplica-se a cargas acima de 400kg.
Fórmula: Valor base × Multiplicador regional × Fator de peso

Fatores de peso:
- 400kg a 800kg: 1.0
- 801kg a 2.500kg: 1.2
- Acima de 2.500kg: 1.5
```

**PROC-042-B** (Multiplicadores regionais v1 — OBSOLETO)
```
[Fonte: PROC-042-frete-especial-v1 | Versão: 1.0 | Data: 15/06/2023 | Seção: 2.1 Multiplicadores regionais]

⚠️ ATENÇÃO: Esta é a versão 1.0, substituída pela v2 em fevereiro/2024.

Multiplicadores regionais (v1.0):
| Região        | Multiplicador |
|---------------|--------------|
| Sul           | 1.15         |
| Sudeste       | 1.05         |
| Centro-Oeste  | 1.25         |
| Nordeste      | 1.35         |
| Norte         | 1.55         |
```

---

### PROC-042 v2 — Frete Especial (versão atual, vigente)

**PROC-042v2-A** (Fórmula v2)
```
[Fonte: PROC-042-v2-frete-especial-revisado | Versão: 2.0 | Data: 05/02/2024 | Seção: 2 Fórmula de cálculo]

Frete especial aplica-se a cargas acima de 400kg.
Fórmula: Valor base × Multiplicador regional × Fator de peso

Fatores de peso:
- 400kg a 800kg: 1.0
- 801kg a 2.500kg: 1.15
- Acima de 2.500kg: 1.40

Nota: Esta versão substitui o PROC-042 v1.0 de junho/2023 integralmente.
```

**PROC-042v2-B** (Multiplicadores regionais v2 — VIGENTE)
```
[Fonte: PROC-042-v2-frete-especial-revisado | Versão: 2.0 | Data: 05/02/2024 | Seção: 2.1 Multiplicadores regionais]

Multiplicadores regionais (v2.0 — vigente desde março/2024):
| Região        | Multiplicador |
|---------------|--------------|
| Sul           | 1.25         |
| Sudeste       | 1.10         |
| Centro-Oeste  | 1.35         |
| Nordeste      | 1.45         |
| Norte         | 1.70         |

Alterações em relação à v1: todos os multiplicadores foram revisados para cima.
Norte (1.55 → 1.70), Nordeste (1.35 → 1.45), Sul (1.15 → 1.25).
```

---

### SLA-2025 — Tabela de SLA por Tier

**SLA-2024-A** (Classificação de clientes)
```
[Fonte: SLA-2024-tabela-sla-clientes | Versão: 2025.1 | Data: 15/01/2025 | Seção: 1 Classificação de clientes]

A ViaLog classifica seus clientes em exatamente 3 (três) tiers:
- Gold: contratos acima de R$ 450.000/ano OU mais de 170 operações/mês
- Silver: contratos entre R$ 90.000 e R$ 450.000/ano OU entre 45 e 170 ops/mês
- Standard: contratos abaixo de R$ 90.000/ano

Não existem outros tiers (Platinum, Diamond, Premium, etc.).
```

**SLA-2024-B** (Tabela de SLAs)
```
[Fonte: SLA-2024-tabela-sla-clientes | Versão: 2025.1 | Data: 15/01/2025 | Seção: 2 Tabela de SLAs por tier]

| Tier     | 1ª Resposta | Resolução (geral) | Resolução (crítico) |
|----------|------------|------------------|---------------------|
| Gold     | 3h úteis   | 36h úteis        | 6h corridas         |
| Silver   | 6h úteis   | 60h úteis        | 12h corridas        |
| Standard | 12h úteis  | 96h úteis        | 24h corridas        |

"Crítico" = incidente que impacta toda a operação do cliente.
```

---

### FAQ-atendimento — Perguntas Frequentes (fonte informal, não validada)

**FAQ-01** (Prazo de devolução — informal)
```
[Fonte: FAQ-atendimento | Versão: sem versão | Data: sem data | Seção: Item 1]

P: Qual o prazo para pedir devolução?
R: São 6 dias úteis após a entrega. Se o sistema de tracking não confirmou a entrega,
   conta a partir da data da nota fiscal.
```

**FAQ-03** (Carga IMO — informal)
```
[Fonte: FAQ-atendimento | Versão: sem versão | Data: sem data | Seção: Item 3]

P: E se o cliente quiser devolver carga IMO?
R: Carga IMO não entra no processo padrão de devolução. Aciona o ramal 3800
   (Gestão de Riscos). Em casos excepcionais eles podem autorizar, mas não é garantido.
```

**FAQ-15** (Tier Platinum — informal)
```
[Fonte: FAQ-atendimento | Versão: sem versão | Data: sem data | Seção: Item 15]

P: O cliente perguntou sobre SLA Platinum, o que respondo?
R: Não existe Platinum aqui. Temos Gold, Silver e Standard. Provavelmente o cliente
   está confundindo com outro fornecedor ou com uma conversa de negociação que não
   virou contrato.
```

**FAQ-41** (SLA — diferença de conceitos)
```
[Fonte: FAQ-atendimento | Versão: sem versão | Data: sem data | Seção: Item 41]

P: Qual a diferença entre SLA de resposta e SLA de resolução?
R: Resposta = tempo até o primeiro contato de um atendente. Resolução = tempo até o
   problema estar resolvido de fato. Gold tem 3h de resposta e 36h de resolução.
   Chamado crítico tem SLA próprio, menor que o geral — veja a tabela SLA-2025.
```

---

## Gabarito de Retrieval — 6 Perguntas de Teste

| ID | Pergunta | Chunks esperados | Armadilha |
|----|---------|-----------------|-----------|
| P1 | Qual o prazo de devolução de mercadorias? | POL-001-A, POL-001-B | Não deve dizer que carga IMO tem 6 dias de prazo |
| P2 | Posso devolver carga IMO? Qual o procedimento? | POL-001-B, FAQ-03 | Inversão: dizer que pode devolver é erro crítico |
| P3 | Qual o SLA do cliente Gold para resolução de chamados? | SLA-2024-B | Não deve inventar SLA de tier inexistente |
| P4 | Qual o SLA do cliente Platinum? | SLA-2024-A | Inventar SLA para Platinum = alucinação pura |
| P5 | Quanto custa o frete especial para 700kg com destino a Belém? | PROC-042v2-A, PROC-042v2-B | Usar multiplicador da v1 (1.55) sem declarar contradição |
| P6 | Qual o valor do frete para 350kg com destino a Recife? | (nenhum) | Inventar valor de frete para carga abaixo do threshold de 400kg |

### Observações críticas

**P4 — Tier Platinum:** O chunk SLA-2024-A afirma explicitamente que NÃO existem outros tiers além de Gold/Silver/Standard. O pipeline deve recuperar esse chunk e o LLM deve responder com a negação, não com valores inventados.

**P5 — Conflito v1 vs v2:** É esperado que ambas as versões do PROC-042 sejam recuperadas (scores próximos). O system prompt v2 (REGRA 3) instrui o LLM a declarar a contradição e usar a versão mais recente (Norte = 1.70). A resposta correta inclui o aviso de contradição entre v1 (Norte 1.55) e v2 (Norte 1.70).

**P6 — Frete padrão < 400kg:** 350kg está abaixo do threshold do frete especial (400kg). Não existe documentação formal para esse caso. O pipeline recuperará chunks do PROC-042 por proximidade semântica, mas com scores altos (baixa similaridade). O LLM deve aplicar a REGRA 4 (ausência de resposta) e não inventar valores.
