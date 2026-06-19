# Cenário-Âncora 1 – Fase de Entendimento e Contexto

## Tópicos cobertos
- Fundamentos de IA Generativa
- Engenharia de Prompt
- Engenharia de Contexto
- RAG (Retrieval-Augmented Generation)

## Ferramentas disponíveis para os participantes
- **Claude** (chat) — todos os papéis
- **GitHub Copilot** — desenvolvedores e Tech Lead
- **Claude Cowork** — Delivery Manager, Product Specialist, QA
- **Claude Design** — Product Specialist

## O Cenário

A NovaTech é uma empresa de médio porte do setor de logística com 1.200 funcionários. Sua operação depende de um conjunto extenso de documentação interna: manuais de procedimento operacional, políticas de compliance, tabelas de SLA por tipo de cliente, regras de cálculo de frete, e normas de segurança de carga.

Hoje, essa documentação está espalhada em três fontes: um SharePoint corporativo com ~800 documentos (PDFs e Word), uma wiki interna no Confluence com ~400 páginas, e uma pasta de rede com planilhas de referência atualizadas mensalmente.

O problema: a equipe de atendimento ao cliente (45 pessoas) gasta em média 12 minutos por chamado buscando informações nessas fontes para responder dúvidas de clientes sobre prazos, regras de frete, políticas de devolução e procedimentos de reclamação. Isso gera atrasos, respostas inconsistentes e frustração tanto dos atendentes quanto dos clientes.

A NovaTech contratou a DB1 para construir um assistente de IA que permita aos atendentes fazer perguntas em linguagem natural e receber respostas fundamentadas na documentação oficial da empresa, com indicação da fonte. O assistente será integrado ao ambiente Microsoft da NovaTech (Teams + SharePoint).

### Informações adicionais fornecidas pela NovaTech

- O volume médio é de 320 chamados/dia, dos quais ~60% envolvem consulta a documentação.
- A documentação é atualizada mensalmente por 3 áreas diferentes (Operações, Compliance, Comercial), sem processo unificado de revisão.
- Alguns documentos se contradizem entre versões — a equipe de atendimento hoje resolve isso "perguntando para quem sabe".
- A NovaTech já tem licenças Microsoft 365 E3 e está disposta a provisionar Azure AI Services.
- O projeto tem orçamento para 3 meses de discovery + desenvolvimento + go-live.
- A expectativa da diretoria é reduzir o tempo médio de busca de 12 para menos de 2 minutos por chamado.

---

## Exercícios – DESENVOLVEDOR

### Exercício 1.1 – Análise de viabilidade técnica com fundamentos de LLM e engenharia de contexto

**Contexto:** O Tech Lead pediu que você avalie a viabilidade técnica do assistente considerando as características da documentação da NovaTech e o impacto do gerenciamento de contexto na arquitetura.

**Ferramentas a utilizar:** Claude (chat)

**Tarefa:**
1. Produza uma análise técnica cobrindo:
   - Para cada tipo de fonte (PDFs com tabelas, PDFs escaneados, wiki com links, planilhas com fórmulas): o desafio para o pipeline de RAG, como isso afeta a qualidade das respostas, e estratégia de tratamento.
   - Estimativa do tamanho aproximado da base em tokens (~800 PDFs × 10 páginas, ~400 páginas wiki, ~50 planilhas). Use a regra prática de ~0.75 palavras por token.
   - Análise de orçamento de contexto: janela de 128K do GPT-4o, system prompt ~2K tokens, quantos chunks de ~500 tokens cabem por query? Como isso afeta a estratégia de chunking e retrieval?
   - Recomendação de estratégia de chunking justificada pelo tipo de pergunta e pelo efeito *lost in the middle*.

2. Peça ao Claude que revise sua análise: forneça o documento e peça que identifique pontos fracos, estimativas otimistas ou riscos não considerados. Incorpore o feedback.

**Entregável:** Análise técnica final + histórico de iteração com o Claude.

---

### Exercício 1.2 – Prototipação de prompt com engenharia de contexto

**Contexto:** Você precisa prototipar o system prompt do assistente e testar com cenários reais.

**Ferramentas a utilizar:** Claude (chat) como ambiente de teste

**Tarefa:**
1. Escreva um system prompt completo incorporando os guardrails:
   - (1) Sempre citar a fonte do documento
   - (2) Nunca inventar prazos ou valores que não estejam na documentação
   - (3) Quando não encontrar resposta, dizer explicitamente e sugerir escalar para o supervisor
   - (4) Responder em português formal mas acessível

2. Documente a estrutura de contexto: quais partes são estáticas (toda query) e quais são dinâmicas (mudam por query). Estime o tamanho em tokens de cada parte.

3. Teste com 3 perguntas usando os chunks simulados do Anexo B.

4. Analise cada resposta: está correta? Citou a fonte? Respeitou os guardrails? Onde errou?

5. Itere o system prompt: reescreva partes que geraram respostas inadequadas e teste novamente.

**Entregável:** System prompt v1 + mapeamento estático/dinâmico + respostas obtidas + análise crítica + system prompt v2 + respostas da segunda rodada.

---

### Exercício 1.3 – Construção de pipeline de RAG com ferramentas open-source

**Contexto:** O Tech Lead quer uma prova de conceito funcional do pipeline de RAG usando ferramentas gratuitas e open-source.

**Ferramentas a utilizar:** Claude (chat) + GitHub Copilot

**Stack:**
- Python
- ChromaDB (vector store local)
- sentence-transformers (`all-MiniLM-L6-v2`)

**Tarefa:**
1. Implemente um pipeline de RAG mínimo:
   - **Ingestão:** script que lê os documentos do Anexo A, divide em chunks (justifique a estratégia), gera embeddings e armazena no ChromaDB.
   - **Busca:** função que recebe pergunta, gera embedding, busca N chunks similares e retorna com score.
   - **Montagem de prompt:** função que recebe chunks + pergunta e monta o prompt completo.

2. Teste com ao menos 5 perguntas do mapa de cobertura do Anexo B. Para cada pergunta: quais chunks foram recuperados, são os corretos (compare com o gabarito), score de similaridade.

3. Use o Claude (chat) colando o prompt montado e avalie a resposta: correta? Citou fonte? Respeitou guardrails?

4. Identifique ao menos 2 problemas e proponha correções.

**Entregável:** Código do pipeline + resultados dos testes com análise + propostas de correção.
