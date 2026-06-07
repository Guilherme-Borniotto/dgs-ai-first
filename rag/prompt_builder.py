"""
Monta o prompt completo (system prompt estático + chunks dinâmicos + pergunta)
pronto para colar no Claude chat.

Anatomia do contexto por query:
  Estático  (~540 tokens):  identidade + regras + formato de resposta
  Dinâmico  (~1.500 tokens): chunks recuperados (top 3, ~500 tokens cada)
  Dinâmico  (~50 tokens):   pergunta do atendente
  Total médio: ~2.090 tokens — 1,6% da janela de 128K do GPT-4o
"""

SYSTEM_PROMPT = """## IDENTIDADE
Você é o Assistente de Atendimento da ViaLog Soluções Logísticas.
Responda perguntas dos atendentes com base exclusivamente nos documentos abaixo.

## REGRAS

1. Cite sempre a fonte: "Conforme [Documento] | [Versão] | [Seção]: [informação]"
2. Nunca invente prazos, valores ou multiplicadores. Se o dado não estiver nos documentos, não o mencione.
3. Documentos contraditórios: use o de data mais recente E informe ao atendente que existe contradição na base.
4. Ausência de resposta: "Não encontrei essa informação na documentação disponível. Recomendo [ação]."
5. FAQ: sinalizar como fonte informal. "Segundo o FAQ interno (não validado formalmente)..."
6. Responda em português formal. Resposta direta primeiro, detalhes depois.

## FORMATO
1. Resposta direta (1-2 frases)
2. Exceções ou detalhes relevantes
3. Fonte(s) citada(s)
4. Ação recomendada ao atendente (quando aplicável)
"""


def build(query: str, chunks: list[dict]) -> str:
    """
    Monta prompt. Chunks com menor score (mais relevantes) vão para
    o início e fim do bloco — mitiga o efeito lost-in-the-middle.
    """
    if len(chunks) > 2:
        ordered = [chunks[0]] + chunks[2:] + [chunks[1]]
    else:
        ordered = chunks

    docs = "## DOCUMENTOS RECUPERADOS\n\n"
    for i, c in enumerate(ordered, 1):
        docs += f"--- [{i}] ---\n{c['text']}\n\n"

    return f"{SYSTEM_PROMPT}\n{docs}\n## PERGUNTA DO ATENDENTE\n{query}\n\n## SUA RESPOSTA\n"
