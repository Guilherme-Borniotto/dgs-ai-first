# Exercício 1.3 – Pipeline de RAG: Análise e Resultados

**Papel:** Desenvolvedor  
**Código:** `rag/` na raiz do repositório  
**Ferramentas:** Claude (chat) + GitHub Copilot  
**Data:** 2026-06-05

---

## Ferramentas Utilizadas no Desenvolvimento

### GitHub Copilot

O GitHub Copilot foi utilizado como assistente de código durante o desenvolvimento do pipeline. O fluxo típico: escrever um comentário descrevendo a intenção → Copilot sugere a implementação → revisar e ajustar conforme necessário.

**Exemplo documentado — sugestão de função de verificação de re-ingestão:**

A partir do comentário:
```python
# função para verificar se um documento já foi ingerido antes de re-processar
```

O Copilot sugeriu automaticamente a assinatura:
```python
def is_already_ingested(source: str, client: chromadb.PersistentClient) -> bool
```

![Copilot sugerindo função is_already_ingested em ingest.py](../../assets/copilot-sugestao-ingest.png)

A sugestão foi avaliada e descartada para o PoC (a coleção é recriada a cada ingestão, tornando a verificação desnecessária nesta etapa). O Copilot foi mais útil nas partes de boilerplate — como a estrutura do loop de ingestão, o `col.add()` com todos os campos necessários, e o parsing dos metadados do breadcrumb.

### Claude (chat)

Utilizado para duas finalidades neste exercício:
1. **Apoio ao desenvolvimento** — discussão de estratégias de chunking e trade-offs entre abordagens.
2. **Avaliação das respostas** — os 6 prompts gerados pelo pipeline foram colados no Claude chat e as respostas avaliadas quanto à corretude, citação de fonte e respeito aos guardrails.

---

## Estratégia de Chunking Adotada

O chunking é feito **por tipo de documento**, não por número fixo de tokens.

**Por que não chunking fixo de N tokens?**
Chunking fixo corta seções semânticas ao meio. A tabela de multiplicadores regionais do PROC-042 tem ~150 tokens — se o limite for 512 tokens, ela vai ser agrupada com outros blocos não relacionados. A query "multiplicador para o Norte" vai recuperar um chunk que mistura fórmula + tabela + condições especiais, e a similaridade é diluída.

| Documento | Estratégia | Por quê |
|-----------|-----------|---------|
| POL-001 | Por subseção `###` | Cada subseção é uma regra independente — 3.1 (prazo geral) e 3.2 (exceções) são conceitos opostos que não devem estar no mesmo chunk |
| PROC-042 v1/v2 | Por bloco lógico `##`/`###` | A tabela de multiplicadores deve ser recuperada inteira — separar linha por linha destrói o contexto |
| SLA-2025 | Por bloco lógico | Tabela cortada no meio perde o SLA de resolução de um tier |
| FAQ | Por item `## Item N` | Cada Q&A é semânticamente independente — agrupar itens mistura tópicos díspares |

**Breadcrumb de contexto:** Cada chunk começa com `[Fonte: NOME | Versão: X | Data: DD/MM/AAAA | Seção: ...]`. Isso garante:
- Rastreabilidade mesmo quando o chunk é lido isoladamente pelo LLM.
- Que o LLM identifique qual versão originou a informação (crítico para resolver conflito PROC-042 v1 vs v2).
- Que o system prompt consiga aplicar a regra "use o mais recente".

**Resultado da ingestão (execução real — `python ingest.py`):**
```
FAQ-atendimento.md: 10 chunks
POL-001-politica-devolucao.md: 6 chunks
PROC-042-frete-especial-v1.md: 6 chunks
PROC-042-v2-frete-especial-revisado.md: 7 chunks
SLA-2024-tabela-sla-clientes.md: 6 chunks
Total: 35 chunks
```

---

## Resultados dos Testes (6 Perguntas do Gabarito)

> Scores reais obtidos rodando `python run_tests.py` com ChromaDB populado.
> Métrica: distância cosseno — **menor valor = mais similar**. Próximo de 0 = alta relevância.
> Os top 3 chunks de cada query são os enviados ao Claude via `prompt_builder.build()`.

---

### P1 — "Qual o prazo de devolução de mercadorias?"

**Top 5 chunks recuperados (scores reais):**

| Rank | Score | Fonte | Seção |
|------|-------|-------|-------|
| 1 | 0.7194 | POL-001-politica-devolucao | ### 3.3. Procedimento de devolução |
| 2 | 0.8388 | FAQ-atendimento | ## Item 3 – carga IMO |
| 3 | 0.8712 | POL-001-politica-devolucao | ### 3.5. Custos de devolução |
| 4 | 0.8907 | POL-001-politica-devolucao | ### 3.1. Prazo geral |
| 5 | 0.9431 | FAQ-atendimento | ## Item 22 – seguro de carga |

**Resultado run_tests:** ✅ Fonte esperada recuperada (POL-001 presente)

**Top 3 enviados ao Claude:** seção 3.3 (procedimento), FAQ Item 3 (carga IMO), seção 3.5 (custos)

**Observação:** A seção 3.1 — que contém o prazo de 6 dias úteis, a resposta direta à pergunta — ficou em 4º lugar e não foi incluída no prompt. O modelo priorizou "procedimento de devolução" sobre "prazo geral" para a query "prazo de devolução".

**Resposta do Claude (real — colado de `p1_prompt.txt`):**

> O prazo para solicitação de devolução é de **6 dias úteis** a partir do recebimento da mercadoria.
>
> **Detalhes relevantes**
> Solicitações realizadas após esse prazo são consideradas não elegíveis para o processo de devolução padrão. Dentro do prazo, o fluxo segue as seguintes etapas após abertura do chamado:
> - Triagem pelo time de atendimento: até 6 horas úteis
> - Agendamento da coleta reversa (se aprovado): até 3 dias úteis
> - Processamento do reembolso ou crédito: até 7 dias úteis após recebimento da mercadoria no CD
>
> **Fonte**
> Conforme POL-001-politica-devolucao | Versão 2.8 | Data: 20/02/2024 | Seção 3.5 (prazo de elegibilidade) e Seção 3.3 (procedimento e prazos internos).
>
> **Ação recomendada**
> Verifique a data de recebimento da mercadoria antes de iniciar qualquer procedimento. Se o prazo de 6 dias úteis já tiver sido ultrapassado, não abra chamado de devolução padrão — transfira diretamente ao Comercial.

**Avaliação da resposta:** Resposta correta. O Claude citou a fonte com versão, data e seções específicas. A seção 3.1 não estava no top 3, mas o Claude extraiu o prazo de 6 dias da seção 3.3, que o mencionava como pré-condição do fluxo.

---

### P2 — "Posso devolver carga IMO? Qual o procedimento?"

**Top 5 chunks recuperados (scores reais):**

| Rank | Score | Fonte | Seção |
|------|-------|-------|-------|
| 1 | 0.6271 | FAQ-atendimento | ## Item 3 – devolução de carga IMO |
| 2 | 0.6854 | FAQ-atendimento | ## Item 22 – seguro de carga |
| 3 | 0.7542 | FAQ-atendimento | ## Item 38 – política para carga danificada |
| 4 | 0.8241 | PROC-042-frete-especial-v1 | ## 4. Condições especiais |
| 5 | 0.8681 | POL-001-politica-devolucao | ### 3.5. Custos de devolução |

**Resultado run_tests:** ✅ Fonte esperada recuperada (POL-001 presente na posição 5)

**Top 3 enviados ao Claude:** FAQ Item 3, FAQ Item 22 (seguro — irrelevante), FAQ Item 38

**Problema crítico identificado:** A seção 3.2 do POL-001 — que contém a proibição explícita para cargas IMO — **não apareceu nos top 5**. Os 3 chunks enviados ao Claude são todos do FAQ (fonte informal). O FAQ Item 22 (sobre seguro de carga) é completamente irrelevante para a query.

**Resposta do Claude (real — colado de `p2_prompt.txt`):**

> A devolução de carga IMO não é permitida pelo processo padrão, mas pode ser viabilizada mediante análise especializada pela equipe de Gestão de Riscos.
>
> **Detalhes relevantes**
> O procedimento indicado é orientar o cliente a entrar em contato pelo ramal 3800 (Gestão de Riscos). Não afirme ao cliente que a devolução é impossível — informe que o caso requer análise especializada. Atenção: não há documento formal de política que regulamente esse fluxo nos registros recuperados. A orientação acima é de origem informal.
>
> **Fonte**
> Segundo o FAQ interno (não validado formalmente) | Versão: Não controlada | Seção: Item 3 — devolução de carga IMO.
>
> **Ação recomendada**
> Transfira o cliente para o ramal 3800 (Gestão de Riscos). Recomenda-se confirmar a política formal consultando a POL-001 diretamente.

**Avaliação da resposta:** Falha crítica de retrieval confirmada. A POL-001 seção 3.2 proíbe explicitamente a devolução de cargas IMO via processo padrão, sem exceção de "análise especializada". Essa resposta enganosa é consequência direta do Problema 2 (FAQ domina o retrieval para queries sobre políticas formais).

---

### P3 — "Qual o SLA do cliente Gold para resolução de chamados?"

**Top 5 chunks recuperados (scores reais):**

| Rank | Score | Fonte | Seção |
|------|-------|-------|-------|
| 1 | 0.5241 | SLA-2024-tabela-sla-clientes | ## 5. Medição e reportes |
| 2 | 0.5978 | FAQ-atendimento | ## Item 41 – diferença SLA resposta vs. resolução |
| 3 | 0.7719 | FAQ-atendimento | ## Item 27 – tracking "em trânsito" há 5 dias |
| 4 | 0.8284 | SLA-2024-tabela-sla-clientes | ## 4. Penalidades por descumprimento |
| 5 | 0.8326 | FAQ-atendimento | ## Item 15 – tier Platinum não existe |

**Resultado run_tests:** ✅ Fonte esperada recuperada (SLA-2025 presente nas posições 1 e 4)

**Top 3 enviados ao Claude:** SLA seção 5 (medição), FAQ Item 41 (conceito de SLA), FAQ Item 27 (tracking — irrelevante)

**Problema crítico identificado:** A seção 2 do SLA-2025 — que contém a tabela com os valores reais (Gold: 3h resposta / 36h resolução) — **não apareceu nos top 5**. FAQ Item 27 sobre tracking está completamente fora de escopo.

**Resposta do Claude (real — colado de `p3_prompt.txt`):**

> O SLA de resolução para clientes Gold é de **36 horas úteis**, com SLA de resposta de **3 horas úteis**.
>
> **Detalhes relevantes**
> Para incidentes críticos de clientes Gold, o relógio de SLA não pausa fora do horário comercial. Para chamados gerais, o relógio pausa fora do período 08h–18h em dias úteis. O FAQ menciona que para incidentes críticos os prazos são menores — porém os valores específicos não constam nos trechos recuperados.
>
> **Fontes**
> Segundo o FAQ interno (não validado formalmente) | Seção: Item 41 — diferença entre SLA de resposta e resolução.
> Conforme SLA-2024-tabela-sla-clientes | Versão: 2025.1 | Seção 5 — medição e comportamento do relógio de SLA.
>
> **Ação recomendada**
> Confirme os valores na tabela completa SLA-2025 antes de comunicar prazos ao cliente, especialmente em casos de incidente crítico.

**Avaliação da resposta:** Os valores (3h/36h) estão corretos, mas o Claude chegou neles pelo FAQ Item 41 — que nunca foi recuperada a tabela SLA (seção 2). Resposta correta pela razão errada: FAQ informal com dados coincidentemente corretos.

---

### P4 — "Qual o SLA do cliente Platinum?" (teste de alucinação)

**Top 5 chunks recuperados (scores reais):**

| Rank | Score | Fonte | Seção |
|------|-------|-------|-------|
| 1 | 0.7468 | FAQ-atendimento | ## Item 15 – "Cliente diz que é Platinum. Existe esse tier?" |
| 2 | 0.8143 | SLA-2024-tabela-sla-clientes | ## 5. Medição e reportes |
| 3 | 0.8237 | SLA-2024-tabela-sla-clientes | bloco-0 (cabeçalho do documento) |
| 4 | 0.8551 | SLA-2024-tabela-sla-clientes | ## 1. Classificação de clientes |
| 5 | 0.9318 | SLA-2024-tabela-sla-clientes | ## 3. Definição de incidente crítico |

**Resultado run_tests:** ✅ Fonte esperada recuperada

**Top 3 enviados ao Claude:** FAQ Item 15 (Platinum não existe), SLA seção 5, SLA cabeçalho

**Avaliação:** Melhor resultado entre todas as queries. O FAQ Item 15 trata exatamente de "cliente diz que é Platinum" e ficou em 1º lugar.

**Resposta do Claude (real — colado de `p4_prompt.txt`):**

> Não existe o tier Platinum na ViaLog. Portanto, não há SLA definido para essa categoria.
>
> **Detalhes relevantes**
> Os tiers ativos na ViaLog são exclusivamente Gold, Silver e Standard. Caso o cliente afirme ser Platinum, as causas mais prováveis são: confusão com outra transportadora; referência a um programa de parceria que não virou contrato formal.
>
> **Fontes**
> Segundo o FAQ interno (não validado formalmente) | Seção: Item 15 — tier Platinum inexistente.
> Conforme SLA-2024-tabela-sla-clientes | Versão: 2025.1 | Data: 15/01/2025 — documento contratual que lista os tiers formais sem qualquer menção a Platinum.
>
> **Ação recomendada**
> Solicite ao cliente o número do contrato e consulte o cadastro para identificar o tier correto. Se houver divergência, escale para o setor Comercial.

**Avaliação da resposta:** Melhor resultado entre todos os testes. O Claude bloqueou corretamente a alucinação, não inventou SLA para Platinum.

---

### P5 — "Quanto custa o frete especial para 700kg com destino a Belém?" (conflito v1 vs v2)

**Top 5 chunks recuperados (scores reais):**

| Rank | Score | Fonte | Seção |
|------|-------|-------|-------|
| 1 | 0.8187 | PROC-042-frete-especial-v1 | ## 1. Objetivo |
| 2 | 0.8514 | PROC-042-v2-frete-especial-revisado | ## 1. Objetivo |
| 3 | 0.8528 | PROC-042-frete-especial-v1 | ## 4. Condições especiais |
| 4 | 0.8711 | PROC-042-frete-especial-v1 | ## 3. Prazo de entrega para frete especial |
| 5 | 0.8963 | FAQ-atendimento | ## Item 38 – política para carga danificada |

**Resultado run_tests:** ✅ Fonte esperada recuperada (PROC-042-v2 presente na posição 2)

**Top 3 enviados ao Claude:** PROC-042-v1/objetivo, PROC-042-v2/objetivo, PROC-042-v1/condições especiais

**Problema duplo identificado:** A seção com a tabela de multiplicadores regionais (onde está Norte = 1.70) **não apareceu nos top 5**. As seções de "Objetivo" de ambas as versões foram mais próximas semanticamente da query do que a tabela de valores.

**Resposta do Claude (real — colado de `p5_prompt.txt`):**

> Não é possível calcular o valor do frete especial para 700 kg com destino a Belém, pois a fórmula e os multiplicadores regionais vigentes não constam nos trechos recuperados.
>
> **Detalhes relevantes**
> Há contradição por sobreposição de versões na base documental:
>
> | Documento | Versão | Data |
> |-----------|--------|------|
> | PROC-042-frete-especial-v1 | 1.0 | 15/06/2023 |
> | PROC-042-v2-frete-especial-revisado | 2.0 | 05/02/2024 |
>
> Conforme a regra de documentos contraditórios, o documento vigente é o PROC-042 v2.0 (fevereiro/2024). Os parâmetros da versão 1.0 estão desatualizados e não devem ser utilizados para chamados abertos após 01/03/2024.
>
> **Fontes**
> Conforme PROC-042-v2-frete-especial-revisado | Versão 2.0 | Seção 1 — documento vigente.
> Conforme PROC-042-frete-especial-v1 | Versão 1.0 | Seção 4 — referência a PROC-043 para cargas IMO.
>
> **Ação recomendada**
> Acesse o documento completo PROC-042 v2.0 para obter a fórmula e os multiplicadores regionais atualizados. Caso não tenha acesso, encaminhe ao setor de Operações com as informações: peso (700 kg), destino (Belém/PA) e natureza da carga.

**Avaliação da resposta:** O Claude aplicou corretamente o guardrail de "nunca invente valores" — reconheceu que os multiplicadores não estavam nos chunks e recusou inventar. A tabela de multiplicadores (Norte = 1.70 na v2) ficou fora dos top 5 no retrieval (Problema 3).

---

### P6 — "Qual o valor do frete para 350kg com destino a Recife?" (sem cobertura documental)

**Top 5 chunks recuperados (scores reais):**

| Rank | Score | Fonte | Seção |
|------|-------|-------|-------|
| 1 | 0.9412 | FAQ-atendimento | ## Item 27 – tracking "em trânsito" |
| 2 | 0.9428 | FAQ-atendimento | ## Item 38 – política para carga danificada |
| 3 | 0.9489 | PROC-042-frete-especial-v1 | ## 1. Objetivo |
| 4 | 0.9516 | SLA-2024-tabela-sla-clientes | ## 1. Classificação de clientes |
| 5 | 0.9782 | PROC-042-frete-especial-v1 | ## 4. Condições especiais |

**Resultado run_tests:** ✅ OK — min_score = 0.9412 > threshold 0.5 → sem cobertura real detectada

**Avaliação:** Funcionou corretamente. Todos os scores acima de 0.94 confirmam que nenhum chunk tem proximidade semântica real com "frete padrão para 350kg". A carga de 350kg está abaixo do threshold do frete especial (400kg), e não existe documentação formal para frete padrão nos documentos do pipeline.

**Resposta do Claude (real — colado de `p6_prompt.txt`):**

> Não encontrei essa informação na documentação disponível. O cálculo de frete para 350 kg com destino a Recife não está coberto pelos documentos recuperados nesta consulta.
>
> **Detalhes relevantes**
> O único documento sobre cálculo de frete recuperado — PROC-042 — aplica-se exclusivamente a cargas com peso acima de 400 kg. Uma carga de 350 kg está fora do escopo desse procedimento e segue tabela de frete padrão, cujos parâmetros não constam nos registros disponíveis.
>
> **Fonte**
> Conforme PROC-042-frete-especial-v1 | Versão 1.0 | Seção 1 — escopo restrito a cargas acima de 400 kg.
>
> **Ação recomendada**
> Consulte a tabela de frete padrão com o setor Comercial ou Operações, informando: peso (350 kg) e destino (Recife/PE).

**Avaliação da resposta:** Funcionamento correto do threshold. O Claude respondeu "não encontrei" sem inventar valores, e ainda explicou o motivo (350kg fora do escopo do frete especial).

---

## Resumo da Execução

```
Retrieval correto (nível de fonte): 6/6
  ✅ P1  ✅ P2  ✅ P3  ✅ P4  ✅ P5  ✅ P6
```

**Ressalva importante:** o teste verifica se o documento-fonte correto apareceu nos top 5 — não se a seção específica com a resposta foi incluída no prompt enviado ao Claude. A análise de qualidade real está nas seções de problemas abaixo.

---

## Problemas Identificados e Propostas de Correção

### Problema 1 — Seções erradas recuperadas nos top 3 (P1, P2, P3, P5)

**Observação real da execução:** O modelo `all-MiniLM-L6-v2` não diferencia bem seções do mesmo documento quando as queries são sobre um conceito amplo. Para P2, os 3 chunks enviados ao Claude são todos FAQ — a seção 3.2 do POL-001 (proibição explícita de cargas IMO) não foi recuperada. Para P3, a tabela de SLAs (seção 2) não apareceu; a seção de medição (seção 5) foi mais próxima semanticamente. Para P5, a tabela de multiplicadores regionais não apareceu em nenhum dos 5 resultados.

**Proposta de correção:**
- Implementar **hybrid retrieval**: combinar busca vetorial (semântica) com BM25 (palavra-chave exata). Bibliotecas como `rank_bm25` permitem isso sem infraestrutura adicional. BM25 garantiria que "Belém" e "Norte" no PROC-042 fossem recuperados, mesmo sem proximidade semântica.
- Aumentar `n` no retrieval de 5 para 10, aplicar threshold de score (ex: descartar scores > 0.90), e selecionar os top 3 do resultado filtrado.

### Problema 2 — FAQ domina o retrieval para queries sobre políticas formais (P2)

**Observação real da execução:** Para P2, os 3 primeiros resultados foram FAQ Items (scores 0.63, 0.69, 0.75). A seção formal do POL-001 ficou em 5º lugar. O FAQ Item 22 (sobre seguro de carga) é irrelevante para a query e consumiu uma das 3 vagas do prompt.

**Proposta de correção:**
- Adicionar campo `confiabilidade` nos metadados do chunk: `"formal"` (POL, PROC, SLA) vs. `"informal"` (FAQ).
- Aplicar **re-ranking pós-retrieval**: chunks formais com score ≤ 0.85 sobem na fila em relação a chunks informais com score semelhante. Garante que documentos normativos tenham preferência.
- Em `prompt_builder.py`, marcar visualmente chunks informais com aviso `[FONTE INFORMAL]`, reforçando a REGRA 5 do system prompt.

### Problema 3 — Tabela de multiplicadores não recuperada para query de frete (P5)

**Observação real da execução:** Para P5 ("Quanto custa o frete especial para 700kg para Belém?"), a tabela de multiplicadores regionais não apareceu nos top 5. As seções de "Objetivo" dos dois PROCs foram mais próximas semanticamente. Claude receberia apenas a introdução do procedimento, sem os valores concretos para calcular o frete.

**Proposta de correção:**
- Adicionar **sumário semântico** a cada chunk no momento da ingestão: uma frase descrevendo o conteúdo específico do chunk (ex: "Esta seção contém os multiplicadores regionais de frete: Sul 1.25, Sudeste 1.10, Norte 1.70, Nordeste 1.45, Centro-Oeste 1.35"). Embedar o sumário melhora a recuperação por queries de intenção.
- Alternativa mais simples: duplicar as linhas da tabela de multiplicadores como metadados de texto nos chunks adjacentes, aumentando a densidade de termos relevantes.
