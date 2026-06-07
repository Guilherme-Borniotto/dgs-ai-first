# SLA-2025 – Tabela de SLA por Tipo de Cliente

**Versão:** 2025.1
**Última atualização:** 15/01/2025
**Responsável:** Diretoria Comercial + Gerência de Operações
**Classificação:** Documento contratual – os SLAs listados aqui são compromissos formais com o cliente

## 1. Classificação de clientes

A ViaLog classifica seus clientes em 3 (três) tiers com base no volume mensal de operações e no valor do contrato:

| Tier | Critério de elegibilidade | Revisão |
|------|--------------------------|---------|
| Gold | Contrato anual acima de R$ 450.000 OU mais de 170 operações/mês | Semestral |
| Silver | Contrato anual entre R$ 90.000 e R$ 450.000 OU entre 45 e 170 operações/mês | Semestral |
| Standard | Todos os demais clientes | Anual |

Nota: Não existem outros tiers além dos três listados acima. Solicitações de SLA diferenciado fora desses tiers devem ser encaminhadas ao Comercial para análise de viabilidade.

## 2. Tabela de SLAs

| Métrica | Gold | Silver | Standard |
|---------|------|--------|----------|
| Tempo de primeira resposta (chamados gerais) | Até 3h úteis | Até 6h úteis | Até 12h úteis |
| Tempo de resolução (chamados gerais) | Até 36h úteis | Até 60h úteis | Até 96h úteis |
| Tempo de primeira resposta (incidentes críticos) | Até 45min | Até 90min | Até 3h |
| Tempo de resolução (incidentes críticos) | Até 6h corridas | Até 12h corridas | Até 24h corridas |
| Disponibilidade do portal de tracking | 99,7% | 99,2% | 98,5% |
| Gerente de conta dedicado | Sim | Não | Não |
| Relatório mensal de performance | Sim (detalhado) | Sim (resumido) | Sob demanda |

## 3. Definição de incidente crítico

Um incidente é classificado como crítico quando atende a pelo menos um dos seguintes critérios:

- Carga com valor declarado acima de R$ 80.000 está com status desconhecido há mais de 4 horas.
- Carga IMO (classes 3, 6 ou 8) com qualquer irregularidade de documentação ou rastreamento.
- Mais de 4 chamados do mesmo cliente nas últimas 12 horas sobre o mesmo problema.
- Qualquer situação que envolva risco à segurança de pessoas ou ao meio ambiente.

## 4. Penalidades por descumprimento

- Primeira violação de SLA no mês: registro interno, sem impacto contratual.
- Segunda violação no mesmo mês: crédito de 4% sobre o valor do frete do chamado afetado.
- Terceira violação ou mais no mesmo mês: crédito de 8% + reunião obrigatória com o gerente de conta (Gold) ou gerente de operações (Silver/Standard).

## 5. Medição e reportes

Os SLAs são medidos pelo sistema de chamados (Azure DevOps) a partir do timestamp de abertura do chamado. O relógio de SLA pausa fora do horário comercial (08h-18h, dias úteis) para chamados gerais, mas não pausa para incidentes críticos de clientes Gold.
