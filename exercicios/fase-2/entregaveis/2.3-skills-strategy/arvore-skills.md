# Exercício 2.3 — Árvore de Skills do Projeto NovaTech Assistant
**Autor:** Guilherme Borniotto  
**Data:** 18/06/2026  

---

## Hierarquia Foundation → Domain → Artifact

```
skills/
├── foundation/
│   ├── typescript-conventions.md       ← BASE: consumida por TODAS as outras skills
│   ├── error-handling.md
│   └── project-structure.md
│
├── domain/
│   ├── azure-functions-endpoint.md
│   ├── azure-ai-search-integration.md
│   ├── react-components.md
│   └── testing-patterns.md
│
└── artifact/
    ├── create-rag-endpoint.md
    ├── create-integration-test.md
    └── create-react-card.md
```

---

## Catálogo de Skills

### FOUNDATION

#### `typescript-conventions`
| Campo | Valor |
|---|---|
| **Arquivo** | `skills/foundation/typescript-conventions.md` |
| **Descrição** | Convenções TypeScript do projeto: strict mode, imports absolutos, naming, organização de tipos |
| **Frase-ativação** | "Quando gerar qualquer arquivo TypeScript neste projeto" |
| **Quem cria** | Tech Lead |
| **Quem consome** | Dev (implementação), Copilot (geração de código), Claude Code |
| **Frequência** | Alta — toda geração de código TS |
| **Dependências** | Nenhuma (é a base) |

#### `error-handling`
| Campo | Valor |
|---|---|
| **Arquivo** | `skills/foundation/error-handling.md` |
| **Descrição** | Padrão de erros customizados, logging de erros com pino, retry com exponential backoff |
| **Frase-ativação** | "Quando implementar qualquer serviço que faz chamadas externas ou pode falhar" |
| **Quem cria** | Tech Lead |
| **Quem consome** | Dev (services), Copilot |
| **Frequência** | Alta — todos os services Azure |
| **Dependências** | `typescript-conventions` |

#### `project-structure`
| Campo | Valor |
|---|---|
| **Arquivo** | `skills/foundation/project-structure.md` |
| **Descrição** | Mapa de diretórios do repositório, onde cada tipo de arquivo vive, convenções de módulos e exports |
| **Frase-ativação** | "Quando criar um novo arquivo ou decidir onde colocar código" |
| **Quem cria** | Tech Lead |
| **Quem consome** | Dev, QA, Product Specialist, Copilot |
| **Frequência** | Média — especialmente no onboarding e ao criar novos módulos |
| **Dependências** | Nenhuma |

---

### DOMAIN

#### `azure-functions-endpoint`
| Campo | Valor |
|---|---|
| **Arquivo** | `skills/domain/azure-functions-endpoint.md` |
| **Descrição** | Padrão de HTTP trigger v4: estrutura de handler, validação Zod, logging, auth level, registro de rota |
| **Frase-ativação** | "Quando criar ou modificar um Azure Function HTTP trigger" |
| **Quem cria** | Tech Lead |
| **Quem consome** | Dev, Copilot |
| **Frequência** | Alta — 3+ endpoints no projeto (query, feedback, health) |
| **Dependências** | `typescript-conventions`, `error-handling` |

#### `azure-ai-search-integration`
| Campo | Valor |
|---|---|
| **Arquivo** | `skills/domain/azure-ai-search-integration.md` |
| **Descrição** | Padrão de query ao Azure AI Search: cliente, filtros de vigência (ADR-0003), paginação, tratamento de results vazio |
| **Frase-ativação** | "Quando implementar ou testar uma chamada ao Azure AI Search" |
| **Quem cria** | Tech Lead + Dev Sênior |
| **Quem consome** | Dev, Copilot |
| **Frequência** | Média — principalmente no pipeline e no query endpoint |
| **Dependências** | `typescript-conventions`, `error-handling` |

#### `react-components`
| Campo | Valor |
|---|---|
| **Arquivo** | `skills/domain/react-components.md` |
| **Descrição** | Padrão de componentes funcionais React para o painel web: props tipadas, sem estado global desnecessário, acessibilidade básica |
| **Frase-ativação** | "Quando criar ou modificar um componente React do painel web" |
| **Quem cria** | Dev Sênior |
| **Quem consome** | Dev, Copilot |
| **Frequência** | Média — painel web tem escopo limitado (dashboard + histórico) |
| **Dependências** | `typescript-conventions` |

#### `testing-patterns`
| Campo | Valor |
|---|---|
| **Arquivo** | `skills/domain/testing-patterns.md` |
| **Descrição** | Padrão de testes Vitest: estrutura describe/it, arrange-act-assert, mocking com msw, factories de dados |
| **Frase-ativação** | "Quando escrever qualquer teste neste projeto" |
| **Quem cria** | QA |
| **Quem consome** | Dev, QA, Copilot |
| **Frequência** | Alta — toda task tem critérios de aceite que resultam em testes |
| **Dependências** | `typescript-conventions`, `project-structure` |

---

### ARTIFACT

#### `create-rag-endpoint`
| Campo | Valor |
|---|---|
| **Arquivo** | `skills/artifact/create-rag-endpoint.md` |
| **Descrição** | Receita completa para criar um endpoint RAG: handler → validator → embedding → search → prompt → completion → response |
| **Frase-ativação** | "Crie um endpoint RAG para [funcionalidade]" |
| **Quem cria** | Dev Sênior + Tech Lead |
| **Quem consome** | Dev Pleno, Copilot |
| **Frequência** | Baixa — 1-2 vezes no projeto (query endpoint principal + possível variante) |
| **Dependências** | `azure-functions-endpoint`, `azure-ai-search-integration`, `error-handling`, `typescript-conventions` |

#### `create-integration-test`
| Campo | Valor |
|---|---|
| **Arquivo** | `skills/artifact/create-integration-test.md` |
| **Descrição** | Receita para criar teste de integração de endpoint: msw handlers, fixtures, cenários de happy path + edge case, assertions específicas |
| **Frase-ativação** | "Crie testes de integração para [endpoint/service]" |
| **Quem cria** | QA + Dev Sênior |
| **Quem consome** | Dev, QA, Copilot |
| **Frequência** | Alta — uma por endpoint (8 tasks de teste mapeadas no tasks.md) |
| **Dependências** | `testing-patterns`, `typescript-conventions`, `project-structure` |

#### `create-react-card`
| Campo | Valor |
|---|---|
| **Arquivo** | `skills/artifact/create-react-card.md` |
| **Descrição** | Receita para criar um card de resposta no painel web: layout, exibição de source_document, indicador de confiança, feedback button |
| **Frase-ativação** | "Crie um card React para exibir [tipo de dado]" |
| **Quem cria** | Dev Sênior |
| **Quem consome** | Dev Pleno, Copilot |
| **Frequência** | Baixa — 2-3 componentes de card no painel web |
| **Dependências** | `react-components`, `typescript-conventions` |

---

## Mapa de Criação e Consumo por Papel

| Skill | Tech Lead (cria) | Dev Sênior (cria) | QA (cria) | Dev Pleno (consome) | Copilot (consome) |
|---|:---:|:---:|:---:|:---:|:---:|
| `typescript-conventions` | ✅ | — | — | ✅ | ✅ |
| `error-handling` | ✅ | — | — | ✅ | ✅ |
| `project-structure` | ✅ | — | — | ✅ | ✅ |
| `azure-functions-endpoint` | ✅ | — | — | ✅ | ✅ |
| `azure-ai-search-integration` | ✅ | ✅ | — | ✅ | ✅ |
| `react-components` | — | ✅ | — | ✅ | ✅ |
| `testing-patterns` | — | — | ✅ | ✅ | ✅ |
| `create-rag-endpoint` | ✅ | ✅ | — | ✅ | ✅ |
| `create-integration-test` | — | ✅ | ✅ | ✅ | ✅ |
| `create-react-card` | — | ✅ | — | ✅ | ✅ |

---

## Sequência de Criação Recomendada

1. **Sprint 0 (antes de qualquer código):**
   - `typescript-conventions` — Tech Lead (desbloqueador de tudo)
   - `project-structure` — Tech Lead (orienta onde cada arquivo vai)
   - `error-handling` — Tech Lead (necessária antes dos services)

2. **Sprint 1 (junto com TASK-001 a TASK-007):**
   - `azure-functions-endpoint` — Tech Lead
   - `azure-ai-search-integration` — Tech Lead + Dev Sênior
   - `testing-patterns` — QA

3. **Sprint 2 (quando artefatos de alto nível forem necessários):**
   - `create-rag-endpoint` — Dev Sênior + Tech Lead
   - `create-integration-test` — QA + Dev Sênior

4. **Sprint 3 (painel web):**
   - `react-components` — Dev Sênior
   - `create-react-card` — Dev Sênior
