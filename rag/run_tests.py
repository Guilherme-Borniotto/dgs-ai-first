"""
Testes de retrieval: roda as 6 perguntas do gabarito (Anexo B),
compara os chunks recuperados com os esperados e salva os prompts
prontos em prompts_para_claude/p{n}_prompt.txt para colar no Claude chat.
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path
from search import search
from prompt_builder import build

OUT_DIR = Path(__file__).parent / "prompts_para_claude"
OUT_DIR.mkdir(exist_ok=True)

# Gabarito: mapa pergunta → fontes que DEVEM aparecer nos chunks recuperados
TESTS = [
    {
        "id": "P1",
        "pergunta": "Qual o prazo de devolução de mercadorias?",
        "fontes_esperadas": ["POL-001-politica-devolucao"],
        "descricao": "Baseline — regra geral + exceções da POL-001",
        "armadilha": "Não deve dizer que carga IMO tem 6 dias de prazo",
    },
    {
        "id": "P2",
        "pergunta": "Posso devolver carga IMO? Qual o procedimento?",
        "fontes_esperadas": ["POL-001-politica-devolucao"],
        "descricao": "Negação explícita — POL-001 seção 3.2",
        "armadilha": "Inversão de regra: dizer que pode devolver é erro crítico",
    },
    {
        "id": "P3",
        "pergunta": "Qual o SLA do cliente Gold para resolução de chamados?",
        "fontes_esperadas": ["SLA-2024-tabela-sla-clientes"],
        "descricao": "Domínio contratual — tabela de SLAs",
        "armadilha": "Não deve inventar SLA de tier inexistente",
    },
    {
        "id": "P4",
        "pergunta": "Qual o SLA do cliente Platinum?",
        "fontes_esperadas": ["SLA-2024-tabela-sla-clientes"],
        "descricao": "Teste de alucinação — tier Platinum não existe",
        "armadilha": "Inventar SLA para Platinum é alucinação pura. SLA-2025 diz explicitamente que só existem 3 tiers.",
    },
    {
        "id": "P5",
        "pergunta": "Quanto custa o frete especial para 700kg com destino a Belém?",
        "fontes_esperadas": ["PROC-042-v2-frete-especial-revisado"],
        "descricao": "Conflito v1 vs v2 — multiplicador Norte: 1.55 (v1) vs 1.70 (v2)",
        "armadilha": "Usar multiplicador da v1 sem avisar sobre a contradição",
    },
    {
        "id": "P6",
        "pergunta": "Qual o valor do frete para 350kg com destino a Recife?",
        "fontes_esperadas": [],
        "descricao": "Não-cobertura documental — frete padrão (<400kg) não está nos documentos",
        "armadilha": "Inventar um valor ou regra de frete padrão. Resposta correta: informar que não há documentação",
    },
]


def run():
    print("=" * 70)
    print("TESTES DE RETRIEVAL — NOVATECH RAG PIPELINE")
    print("=" * 70)

    resultados = []

    for test in TESTS:
        print(f"\n[{test['id']}] {test['descricao']}")
        print(f"Pergunta: {test['pergunta']}")
        print(f"Armadilha: {test['armadilha']}")
        print("-" * 70)

        chunks = search(test["pergunta"], n=5)
        fontes = {c["source"] for c in chunks}

        print("Chunks recuperados:")
        for c in chunks:
            print(f"  [{c['score']:.4f}] {c['source']} | {c['section'][:55]}")

        # Verifica cobertura do gabarito
        if not test["fontes_esperadas"]:
            # P6: esperamos que nenhuma fonte relevante seja recuperada com score alto
            min_score = min(c["score"] for c in chunks) if chunks else 1.0
            ok = min_score > 0.5  # score alto = baixa similaridade em distância cosseno
            status = "✅ OK (score alto = sem cobertura real)" if ok else "⚠️  Atenção: chunk relevante pode ter sido recuperado"
        else:
            ok = any(e in fontes for e in test["fontes_esperadas"])
            status = "✅ Fonte esperada recuperada" if ok else "❌ Fonte esperada NÃO recuperada"

        print(f"\n  {status}")

        # Monta e salva prompt
        prompt = build(test["pergunta"], chunks[:3])
        out_file = OUT_DIR / f"{test['id'].lower()}_prompt.txt"
        out_file.write_text(prompt, encoding="utf-8")
        print(f"  Prompt salvo: {out_file.name}")

        resultados.append({"id": test["id"], "ok": ok})

    print("\n" + "=" * 70)
    print("RESUMO")
    print("=" * 70)
    ok_count = sum(1 for r in resultados if r["ok"])
    print(f"Retrieval correto: {ok_count}/{len(resultados)}")
    for r in resultados:
        print(f"  {'✅' if r['ok'] else '❌'} {r['id']}")
    print(f"\nPrompts salvos em: {OUT_DIR}")


if __name__ == "__main__":
    run()
