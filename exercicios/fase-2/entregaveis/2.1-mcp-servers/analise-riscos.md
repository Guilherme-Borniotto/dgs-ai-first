# Exercício 2.1 — Análise de Riscos de Segurança (MCP Servers Locais)
**Autor:** Guilherme Borniotto  
**Data:** 18/06/2026  

---

## Risco 1 — Escopo Amplo no Filesystem Expõe Segredos

**Descrição do risco:**  
Se o `filesystem` server receber a raiz do repositório (`.`) como escopo, um agente que execute `list_directory` ou `read_file` pode acessar arquivos como `.env`, `*.pem`, `local.settings.json` (que no Azure Functions contém connection strings), e qualquer arquivo de credencial que o desenvolvedor tenha localmente mas não commitado.

**Vetor de ataque:**  
Um prompt do usuário como "leia todos os arquivos de configuração do projeto" leva o agente a invocar `read_file` em `.env`. Se o agente usar esse conteúdo em uma resposta ou log, as credenciais são expostas.

**Probabilidade:** Alta (comportamento padrão de modelos que recebem instrução aberta)  
**Impacto:** Crítico (vazamento de connection strings Azure, API keys, tokens)

**Mitigação aplicada neste projeto:**
1. O `filesystem-rw` aponta apenas para `./src ./specs ./skills ./prompts` — não inclui a raiz.
2. O `filesystem-docs-readonly` aponta apenas para `./docs/novatech ./data/retrieval-corpus`.
3. Nenhum server recebe `.` como escopo.
4. O arquivo `.env` está no `.gitignore` E fora de todos os escopos MCP.
5. Adicionar ao `AGENTS.md`: "Nunca leia, processe ou cite conteúdo de arquivos `.env`, `*.pem`, `local.settings.json` ou qualquer arquivo não listado nos escopos MCP."

**Verificação:**
```bash
# Confirmar que .env não está acessível via MCP
# O filesystem server retornará "path not allowed" para qualquer tentativa de ler fora do escopo
```

---

## Risco 2 — Escrita sem Gate Humano Permite Alteração Silenciosa de Código

**Descrição do risco:**  
O `filesystem-rw` server tem acesso de escrita em `./src ./specs ./skills`. Um agente com escrita habilitada pode modificar código de produção (ex.: alterar lógica de validação em `validator.ts`) sem que o desenvolvedor revise explicitamente. Se o desenvolvedor simplesmente aceitar a sugestão do Copilot sem verificar o diff, código incorreto entra na base.

**Vetor de ataque:**  
Um prompt como "corrija o bug no handler" leva o agente a usar `write_file` para sobrescrever `handler.ts` com uma versão que introduz uma vulnerabilidade ou remove uma checagem crítica. O desenvolvedor, sem revisar o diff completo, faz commit.

**Probabilidade:** Média (requer que o dev não revise o diff — mas é um comportamento comum sob pressão)  
**Impacto:** Alto (bugs em produção, vulnerabilidades de segurança, violação de guardrails)

**Mitigação aplicada neste projeto:**
1. **Gate 3 (Code → Merge)** definido no AGENTS.md: todo código gerado por agente deve passar por `git diff` revisado pelo Dev + aprovação do Tech Lead via PR local.
2. Instrução no AGENTS.md: "Após qualquer `write_file` via MCP, execute `git diff` e revise o output antes de fazer staging. Nunca execute `git add` sem revisão humana explícita."
3. O `git` server expõe `git_diff` como tool — o agente pode ser instruído a mostrar o diff automaticamente após cada escrita.
4. Convenção de branch: nenhuma escrita direta em `main`. Todo trabalho de agente acontece em feature branches.

---

## Risco 3 — Memory Server Sem Controle de Fonte Persiste Desinformação

**Descrição do risco:**  
O `memory` server persiste entidades e relações entre sessões. Um agente mal-instruído (ou um prompt adversarial) pode gravar no grafo informações falsas sobre o domínio — ex.: "frete especial começa em 300kg" quando na verdade é 500kg. Sessões futuras herdarão essa desinformação.

**Probabilidade:** Baixa (requer prompt malicioso ou erro grave de instrução)  
**Impacto:** Médio (código gerado com base em regras de negócio erradas)

**Mitigação:**
1. O grafo de memória deve ser inicializado com as entidades corretas do domínio no início do projeto (a partir do Anexo A).
2. Instrução no AGENTS.md: "Antes de gravar uma entidade de domínio no servidor memory, confirme o valor contra um documento em `./docs/novatech/`."
3. Revisão periódica do grafo (`read_graph`) pelo Tech Lead ao final de cada sprint.

---

## Tabela de Riscos

| # | Risco | Prob | Impacto | Status |
|---|-------|------|---------|--------|
| 1 | Escopo amplo expõe segredos | Alta | Crítico | **Mitigado** — escopos mínimos, .env fora de qualquer path |
| 2 | Escrita sem gate permite alteração silenciosa | Média | Alto | **Mitigado** — gate no AGENTS.md + branch strategy |
| 3 | Memory persiste desinformação | Baixa | Médio | **Mitigado** — inicialização controlada + revisão periódica |
