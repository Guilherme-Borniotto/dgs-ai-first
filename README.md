# dgs-ai-first

Prova de conceito de um pipeline RAG (Retrieval-Augmented Generation) para o assistente de atendimento interno da ViaLog — empresa de logística fictícia usada como cenário de treinamento no programa DB1 AI-First.

O problema central: atendentes gastam em média 12 minutos por chamado buscando regras espalhadas em múltiplas fontes, com documentos que às vezes se contradizem. O objetivo do pipeline é responder perguntas sobre devolução, frete, SLA e procedimentos sempre com base documental e indicação de fonte — sem inventar informação.

---

## Estrutura do projeto

```
assets/
  anexos/
    anexo-a-documentos-individuais/    <- 5 documentos fonte (input do pipeline)
    anexo-b-chunks-referencia-rag.md   <- gabarito de retrieval (mapa pergunta → chunks esperados)
rag/                                   <- pipeline RAG implementado
  ingest.py
  search.py
  prompt_builder.py
  run_tests.py
  requirements.txt
  chroma_db/                           <- vector store gerado automaticamente (ignorado pelo git)
  prompts_para_claude/                 <- prompts prontos para colar no Claude chat (gerado pelo run_tests.py)
exercicios/
  fase-1/
    exercicio-fase-1-entendimento.md   <- enunciado dos exercícios
    entregaveis/                       <- resoluções e análises
```

---

## Base documental

Cinco documentos simulados da ViaLog em `assets/anexos/anexo-a-documentos-individuais/`:

| Arquivo | Tipo | Detalhe |
|---------|------|---------|
| `POL-001-politica-devolucao.md` | Normativo | Cargas IMO (classes 3, 6 e 8) **não** seguem o processo padrão de devolução |
| `PROC-042-frete-especial-v1.md` | Procedimento | Versão **obsoleta** — multiplicadores diferentes da v2 (Norte: 1.55) |
| `PROC-042-v2-frete-especial-revisado.md` | Procedimento | Versão **atual** — coexiste com v1 sem hierarquia formal (Norte: 1.70) |
| `SLA-2024-tabela-sla-clientes.md` | Contratual | Apenas 3 tiers: Gold, Silver, Standard. **Não existe Platinum** |
| `FAQ-atendimento.md` | Informal | Documento colaborativo, não validado por Compliance |

---

## Stack

- **Python 3.11**
- **ChromaDB** — vector store local (distância cosseno)
- **sentence-transformers** (`all-MiniLM-L6-v2`) — embeddings open-source
- **Claude** (chat manual) — geração de resposta final

Sem LangChain. O pipeline é código manual para tornar cada etapa explícita.

---

## Como rodar

### Pré-requisito

```bash
cd rag
pip install -r requirements.txt
```

### Passo 1 — Ingerir os documentos

Lê os 5 arquivos `.md`, aplica chunking por tipo de documento, gera embeddings e persiste no ChromaDB.

```bash
python ingest.py
```

Saída esperada (com os documentos atuais):
```
FAQ-atendimento.md: 10 chunks
POL-001-politica-devolucao.md: 6 chunks
PROC-042-frete-especial-v1.md: 6 chunks
PROC-042-v2-frete-especial-revisado.md: 7 chunks
SLA-2024-tabela-sla-clientes.md: 6 chunks
Total: 35 chunks
Ingestão concluída.
```
Rodar novamente apenas quando os documentos fonte forem atualizados.

### Passo 2 — Executar os testes de retrieval

Roda as 6 perguntas de teste, compara os chunks recuperados com o gabarito do Anexo B e salva os prompts prontos em `prompts_para_claude/`.

```bash
python run_tests.py
```

### Passo 3 — Busca avulsa (opcional)

Para testar qualquer pergunta diretamente:

```bash
python search.py "Qual o prazo de devolução?"
```

Retorna os 5 chunks mais similares com score de similaridade e indicação de versão (atual/obsoleta).

### Passo 4 — Geração de resposta no Claude

Os arquivos `prompts_para_claude/p1_prompt.txt` a `p6_prompt.txt` contêm o prompt completo (system prompt + chunks recuperados + pergunta) para cada teste.

O pipeline não chama a API do Claude por escolha deliberada — o enunciado pede geração via **Claude chat manual**, sem API. Esses arquivos são a ponte entre o pipeline e o LLM:

1. Abra [claude.ai](https://claude.ai) e inicie uma conversa nova
2. Abra um dos arquivos `.txt` em `prompts_para_claude/`
3. Copie o conteúdo completo e cole no Claude
4. Avalie a resposta: citou a fonte? Respeitou os guardrails? Inventou algo?

---

## Estratégia de chunking

O chunking é feito por **tipo de documento**, não por número fixo de tokens:

| Documento | Estratégia | Motivo |
|-----------|-----------|--------|
| POL-001 | Por subseção `###` | Cada subseção é uma regra independente; misturar 3.1 com 3.2 confunde prazo geral com exceção de carga IMO |
| PROC-042 v1/v2 | Por bloco lógico (fórmula, multiplicadores, prazo, condições, transição) | Tabela de multiplicadores deve ser recuperada como unidade atômica |
| SLA-2025 | Por bloco de tabela + definições | Tabela cortada no meio perde o SLA de resolução de um tier |
| FAQ | Por item individual `## Item N` | Cada Q&A é uma unidade semântica; agrupar itens mistura tópicos díspares |

---

## Perguntas de teste e gabarito

| ID | Pergunta | Chunks esperados (Anexo B) | Propósito |
|----|----------|--------------------------|-----------|
| P1 | Qual o prazo de devolução? | POL-001-A, POL-001-B | Baseline |
| P2 | Posso devolver carga IMO? | POL-001-B, FAQ-03 | Negação explícita |
| P3 | Qual o SLA do cliente Gold? | SLA-2024-B | Domínio contratual / tabela |
| P4 | Qual o SLA do cliente Platinum? | SLA-2024-A (diz que não existe) | Teste de alucinação |
| P5 | Frete para 700kg para Belém? | PROC-042v2-A, PROC-042v2-B | Conflito v1 (Norte 1.55) vs v2 (Norte 1.70) |
| P6 | Frete para 350kg para Recife? | nenhum (carga abaixo de 400kg) | Não-cobertura documental |
