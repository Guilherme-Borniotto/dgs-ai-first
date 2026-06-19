# Exercício 2 — Fase de Estruturação do Trabalho
**Papel:** Desenvolvedor  
**Autor:** Guilherme Borniotto  
**Data:** 18/06/2026  
**Projeto:** NovaTech Assistant (Cenário-Âncora 2)

---

## Estrutura de Entregas

```
exercicio-2/
├── README.md                            # Este arquivo
│
├── 2.1-mcp-servers/
│   ├── mapeamento-mcp.md               # Mapeamento de necessidades → servers MCP
│   ├── mcp.json                        # Configuração final com least privilege
│   ├── evidencia-uso.md                # Evidência de execução real dos servers
│   └── analise-riscos.md               # 2+ riscos de segurança com mitigações
│
├── 2.2-sdd-implementacao/
│   ├── tasks.md                        # Tasks atômicas derivadas do plan.md
│   ├── src/functions/query/
│   │   ├── handler.ts                  # Azure Function HTTP trigger (TASK-001)
│   │   └── validator.ts                # Validação Zod de input/output (TASK-001)
│   └── revisao-critica.md              # Revisão crítica do código gerado
│
└── 2.3-skills-strategy/
    ├── arvore-skills.md                # Árvore Foundation → Domain → Artifact
    └── skills/foundation/
        └── typescript-conventions.md   # SKILL.md Foundation mais importante
```

## Resumo dos Exercícios

| # | Título | Entregáveis Principais |
|---|--------|------------------------|
| 2.1 | Configuração e uso real de MCP servers | mcp.json, mapeamento, evidência, análise de riscos |
| 2.2 | Implementação de spec com SDD | tasks.md, handler.ts + validator.ts, revisão crítica |
| 2.3 | Definição de estratégia de skills | arvore-skills.md, typescript-conventions.md (SKILL.md) |
