# Exercício 2.1 — Mapeamento de Necessidades × MCP Servers
**Autor:** Guilherme Borniotto  
**Data:** 18/06/2026  

---

## Necessidades do Projeto × Servers MCP

O projeto NovaTech Assistant tem 5 necessidades de acesso que precisam ser atendidas pelos agentes de IA (Copilot, Claude Code). Abaixo o mapeamento de cada necessidade para o server MCP mais adequado, com justificativa de escopo.

---

### Necessidade 1 — Código, specs e skills do repositório (leitura e escrita)

**Server:** `filesystem`  
**Escopo:** `./src ./specs ./skills`  
**Acesso:** Read-Write  

**O que expõe:**
- **Tools:** `read_file`, `write_file`, `list_directory`, `create_directory`, `move_file`, `search_files`, `get_file_info`
- **Resources:** conteúdo de arquivos como texto
- **Prompts:** nenhum (filesystem é purely tool-based)

**Quem consome:**
- Dev (escrever código e tasks)
- Tech Lead (escrever AGENTS.md e skills domain)
- QA (escrever specs de teste)

**Por que R/W é necessário aqui:** Agentes precisam criar e editar arquivos de código (`src/`), tasks (`specs/`) e skills (`skills/`). Sem escrita, o Copilot não consegue aplicar sugestões de código nem criar novos arquivos.

---

### Necessidade 2 — Documentação de negócio da NovaTech (somente leitura)

**Server:** `filesystem` (instância separada ou paths adicionais — ver mcp.json)  
**Escopo:** `./docs/novatech`  
**Acesso:** Read-Only (enforcement via não incluir esta pasta nos paths R/W)  

**O que expõe:**
- **Tools:** `read_file`, `list_directory`, `search_files`
- **Resources:** POL-001, PROC-042-v1, PROC-042-v2, SLA-2024, FAQ-Atendimento

**Quem consome:**
- Dev (entender regras de domínio ao codificar guardrails)
- QA (criar dados de teste realistas)
- Product Specialist (verificar guardrails contra documentos originais)

**Por que Read-Only:** Os documentos de negócio são a fonte de verdade da NovaTech. Um agente jamais deve modificá-los — qualquer alteração quebraria a rastreabilidade e poderia introduzir informações falsas no corpus de RAG. O least privilege aqui é total: leitura pura.

---

### Necessidade 3 — Corpus de chunks para recuperação simulada (somente leitura)

**Server:** `filesystem` (path adicional)  
**Escopo:** `./data/retrieval-corpus`  
**Acesso:** Read-Only  

**O que expõe:**
- **Tools:** `read_file`, `list_directory`, `search_files`
- **Resources:** Chunks do Anexo B (30+ chunks organizados por documento-fonte)

**Quem consome:**
- Dev (simular recuperação de chunks durante desenvolvimento do query endpoint)
- QA (criar fixtures de teste com chunks reais)

**Por que Read-Only:** O corpus de chunks é gerado pelo pipeline de ingestão, não pelo agente. Se um agente pudesse escrever aqui, poderia injetar chunks falsos que contaminariam os resultados de busca.

---

### Necessidade 4 — Histórico e branches do repositório

**Server:** `git`  
**Escopo:** `.` (raiz do repositório)  
**Acesso:** Read (histórico, diff, branches) + operações de staging/commit quando explicitamente solicitado  

**O que expõe:**
- **Tools:** `git_log`, `git_diff`, `git_status`, `git_show`, `git_branch`, `git_commit`, `git_add`
- **Resources:** histórico de commits, estado atual da árvore de trabalho

**Quem consome:**
- Dev (entender contexto de mudanças, gerar mensagens de commit no padrão Conventional Commits)
- Tech Lead (auditar histórico antes de aprovar PRs locais)

**Por que git e não filesystem para isso:** O server `git` entende semântica de controle de versão — não apenas lê arquivos, mas expõe diff estruturado, log com metadata, e estado da árvore de trabalho. Usar `filesystem` para isso seria como parsear `git log` manualmente: frágil e sem context.

---

### Necessidade 5 — Memória persistente de decisões e linguagem ubíqua

**Server:** `memory`  
**Escopo:** grafo local persistente (sem pasta fixa — persiste entre sessões via arquivo interno do server)  
**Acesso:** Read-Write (grafo de entidades e relações)  

**O que expõe:**
- **Tools:** `create_entities`, `create_relations`, `add_observations`, `delete_entities`, `delete_observations`, `delete_relations`, `read_graph`, `search_nodes`, `open_nodes`
- **Resources:** grafo de conhecimento persistido entre sessões

**Quem consome:**
- Dev (registrar decisões de implementação que não cabem em commits — ex.: "decidimos não usar async/await no indexer por causa de limitação do Azure SDK")
- Tech Lead (persistir glossário de linguagem ubíqua para que Copilot acesse em sessões futuras)
- Delivery Manager (registrar decisões de escopo)

**Por que memory e não filesystem para isso:** O server `memory` mantém um grafo de entidades e relações — ideal para conhecimento estruturado como "termo X significa Y no domínio Z". Usar arquivos markdown para isso resultaria em buscas textuais imprecisas.

---

### Necessidade Extra — Exploração das primitivas MCP (aprendizado)

**Server:** `everything`  
**Escopo:** servidor de demonstração (não aponta para dados reais)  
**Acesso:** Read (demonstração)  

**O que expõe:**
- Implementação de referência de todas as primitivas MCP: Tools, Resources, Prompts, Sampling
- Demonstrações de cada tipo de tool (echo, add, longRunning, etc.)

**Quem consome:**
- Dev e Tech Lead (aprendizado das primitivas antes de criar servers customizados)

**Por que está na config:** O Exercício 2.1 pede explicitamente que o agente explore primitivas de MCP. O `everything` server é o ambiente de sandbox oficial para isso.

---

## Tabela Resumo

| Necessidade | Server | Paths | Acesso | Consumers |
|---|---|---|---|---|
| Código + specs + skills | `filesystem` | `./src ./specs ./skills` | R/W | Dev, TL, QA |
| Docs NovaTech | `filesystem` | `./docs/novatech` | R-only | Dev, QA, PS |
| Corpus de chunks | `filesystem` | `./data/retrieval-corpus` | R-only | Dev, QA |
| Histórico git | `git` | `.` (repo raiz) | R + commit explícito | Dev, TL |
| Memória persistente | `memory` | grafo local | R/W | Dev, TL, DM |
| Exploração MCP | `everything` | — | R (demo) | Dev, TL |
