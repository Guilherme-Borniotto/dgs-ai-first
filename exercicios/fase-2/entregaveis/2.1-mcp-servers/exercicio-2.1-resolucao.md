# Exercício 2.1 — Configuração e Uso Real de MCP Servers no Projeto
**Papel:** Desenvolvedor  
**Autor:** Guilherme Borniotto  
**Data:** 18/06/2026  

---

## 1. Mapeamento de Necessidades × MCP Servers

O projeto NovaTech Assistant tem 5 necessidades de acesso que precisam ser atendidas pelos agentes de IA (Copilot, Claude Code). Abaixo o mapeamento de cada necessidade para o server MCP mais adequado, com justificativa de escopo e least privilege aplicado.

---

### Necessidade 1 — Código, specs e skills do repositório (R/W)

**Server:** `filesystem-rw`  
**Escopo:** `./src ./specs ./skills ./prompts`  
**Acesso:** Read-Write  
**O que expõe:** `read_file`, `write_file`, `list_directory`, `create_directory`, `search_files`  
**Quem consome:** Dev (escrever código e tasks), Tech Lead (skills domain), QA (specs de teste)  

**Justificativa de escopo mínimo:** Agentes precisam criar e editar arquivos de código, tasks e skills. Não inclui `docs/`, `data/` nem a raiz — essas têm tratamento separado. Sem escrita aqui, o Copilot não consegue aplicar sugestões nem criar novos arquivos de spec.

---

### Necessidade 2 — Documentação de negócio da NovaTech (read-only)

**Server:** `filesystem-ro`  
**Escopo:** `./docs/novatech ./data/retrieval-corpus`  
**Acesso:** Read-Only (flag `--readonly`)  
**O que expõe:** `read_file`, `list_directory`, `search_files`  
**Quem consome:** Dev (entender regras ao codificar guardrails), QA (dados de teste realistas)  

**Justificativa de least privilege total:** Os documentos de negócio são a fonte de verdade da NovaTech. Um agente jamais deve modificá-los — qualquer alteração quebraria a rastreabilidade e poderia introduzir informações falsas no corpus de RAG. O corpus de chunks (`data/retrieval-corpus/`) também é read-only porque é gerado pelo pipeline de ingestão, não pelo agente.

---

### Necessidade 3 — Histórico e branches do repositório

**Server:** `git`  
**Escopo:** `.` (raiz do repositório)  
**O que expõe:** `git_log`, `git_diff`, `git_status`, `git_show`, `git_branch`, `git_commit`  
**Quem consome:** Dev (entender contexto de mudanças, mensagens de commit Conventional Commits), Tech Lead  

**Por que git e não filesystem:** O server `git` entende semântica de controle de versão — expõe diff estruturado, log com metadata e estado da árvore de trabalho. Usar `filesystem` para isso seria parsear saída bruta de shell.

---

### Necessidade 4 — Memória persistente de decisões e linguagem ubíqua

**Server:** `memory`  
**Escopo:** grafo local persistente entre sessões  
**O que expõe:** `create_entities`, `create_relations`, `add_observations`, `read_graph`, `search_nodes`  
**Quem consome:** Dev (decisões de implementação), Tech Lead (glossário de linguagem ubíqua)  

**Por que memory e não filesystem:** O server `memory` mantém um grafo de entidades e relações — ideal para conhecimento estruturado como "termo X significa Y no domínio Z". Arquivos markdown para isso resultariam em buscas textuais imprecisas entre sessões.

---

### Necessidade 5 — Exploração das primitivas MCP (aprendizado)

**Server:** `everything`  
**Escopo:** servidor de demonstração oficial  
**O que expõe:** implementação de referência de todas as primitivas MCP: Tools, Resources, Prompts, Sampling  
**Quem consome:** Dev e Tech Lead (aprendizado antes de criar servers customizados)  

---

### Tabela Resumo

| Necessidade | Server | Paths | Acesso |
|---|---|---|---|
| Código + specs + skills | `filesystem-rw` | `./src ./specs ./skills ./prompts` | R/W |
| Docs NovaTech + corpus chunks | `filesystem-ro` | `./docs/novatech ./data/retrieval-corpus` | R-only |
| Histórico git | `git` | `.` (repo raiz) | R + commit explícito |
| Memória persistente | `memory` | grafo local | R/W |
| Exploração MCP | `everything` | — | R (demo) |

---

## 2. Configuração `.mcp/mcp.json`

```json
{
  "mcpServers": {
    "filesystem-rw": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "./src",
        "./specs",
        "./skills",
        "./prompts"
      ]
    },
    "filesystem-ro": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "--readonly",
        "./docs/novatech",
        "./data/retrieval-corpus"
      ]
    },
    "git": {
      "command": "uvx",
      "args": [
        "mcp-server-git",
        "--repository",
        "."
      ]
    },
    "memory": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-memory"
      ]
    },
    "everything": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-everything"
      ]
    }
  }
}
```

**Least privilege aplicado:**
- `filesystem-rw` não inclui raiz `.`, `docs/`, nem `data/` — evita exposição de `.env` e arquivos de segredo
- `filesystem-ro` com flag `--readonly` impede qualquer escrita nos documentos de negócio
- `git` expõe operações de commit mas requerem instrução explícita do humano
- `memory` e `everything` sem acesso a arquivos do projeto

---

## 3. Evidência de Uso dos MCP Servers

Os servers foram ativados com o `.mcp/mcp.json` acima no Claude com a pasta raiz do repositório `novatech-assistant/`.

### Evidência A — Agente lendo documento de `docs/novatech/`

**Query ao agente:**
> "Leia o documento de política de devolução da NovaTech e me diga: qual é o prazo e quais cargas não podem ser devolvidas?"

**Tool call executado (filesystem-ro):**
```json
{ "tool": "read_file", "server": "filesystem-ro",
  "input": { "path": "./docs/novatech/POL-001-politica-devolucao.md" } }
```

**Resposta do agente:**
> "O prazo padrão é **7 dias corridos** a partir do recebimento (POL-001, v3.1). Cargas das classes 1-6 da ANTT **não podem ser devolvidas** pelo processo padrão."

Agente citou a fonte, não inventou valores, usou o server read-only corretamente. ✅

---

### Evidência B — Agente recuperando chunk de `data/retrieval-corpus/`

**Query ao agente:**
> "Para a pergunta 'Qual o multiplicador regional para frete especial no Norte?', busque o chunk mais relevante no corpus."

**Tool call executado (filesystem-ro):**
```json
{ "tool": "search_files", "server": "filesystem-ro",
  "input": { "path": "./data/retrieval-corpus", "pattern": "multiplicador.*norte" } }
```

**Chunk recuperado:** `PROC-042-v2, Seção 3.2` — Norte: 1.8x (vigente desde 10/11/2023)

**Validação contra Anexo B:** chunk esperado = PROC-042-v2, Seção 3.2. Versão correta (v2, não v1 obsoleto). ✅

---

### Evidência C — Agente lendo histórico git

**Query ao agente:**
> "Quais foram as últimas mudanças no AGENTS.md? Mostre o diff."

**Tool calls executados (git):**
```json
{ "tool": "git_log", "server": "git", "input": { "repo": ".", "max_count": 5, "file_path": "AGENTS.md" } }
{ "tool": "git_diff", "server": "git", "input": { "repo": ".", "ref": "HEAD~1..HEAD", "path": "AGENTS.md" } }
```

**Resultado:** log com author/date/message + diff estruturado da seção "Project Management Rules" adicionada. ✅

---

## 4. Análise de Riscos de Segurança

### Risco 1 — Escopo Amplo Expõe Segredos

**Descrição:** Se o `filesystem` server receber `.` (raiz) como escopo, um agente pode acessar `.env`, `local.settings.json` (connection strings Azure) ou qualquer credencial local não commitada. Um prompt como "leia os arquivos de configuração" leva o agente a invocar `read_file` em `.env` e expor as credenciais na resposta.

**Probabilidade:** Alta | **Impacto:** Crítico

**Mitigação aplicada:**
- `filesystem-rw` aponta apenas para `./src ./specs ./skills ./prompts` — raiz excluída
- `.env` está fora de todos os escopos MCP
- Adicionar ao `AGENTS.md`: "Nunca leia arquivos `.env`, `*.pem` ou `local.settings.json`"

---

### Risco 2 — Escrita sem Gate Humano Permite Alteração Silenciosa de Código

**Descrição:** O `filesystem-rw` tem acesso de escrita em `./src`. Um agente pode modificar `validator.ts` ou `handler.ts` sem revisão explícita. Se o dev aceitar sugestão do Copilot sem revisar o diff completo, código incorreto entra na base.

**Probabilidade:** Média | **Impacto:** Alto

**Mitigação aplicada:**
- **Gate 3** no AGENTS.md: todo código gerado por agente passa por `git diff` revisado + aprovação do Tech Lead via PR local
- Instrução no AGENTS.md: "Após qualquer `write_file`, execute `git diff` antes de fazer staging. Nunca execute `git add` sem revisão humana explícita"
- Todo trabalho de agente em feature branches — nunca direto em `main`

---

### Risco 3 — Memory Server Persiste Desinformação Entre Sessões

**Descrição:** O `memory` server persiste entre sessões. Um agente mal-instruído pode gravar no grafo informações falsas sobre o domínio (ex.: "frete especial começa em 300kg" quando é 500kg). Sessões futuras herdarão essa desinformação.

**Probabilidade:** Baixa | **Impacto:** Médio

**Mitigação:** Grafo inicializado com entidades corretas do domínio a partir do Anexo A. Instrução no AGENTS.md: "Antes de gravar entidade de domínio no memory, confirme o valor contra `./docs/novatech/`."
