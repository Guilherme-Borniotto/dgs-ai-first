"""
Busca semântica: converte a pergunta em embedding e retorna os N chunks
mais similares do ChromaDB.

Uso direto:
    python search.py "Qual o prazo de devolução?"
"""

import sys
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_DIR = Path(__file__).parent / "chroma_db"
COLLECTION = "novatech"
MODEL = "all-MiniLM-L6-v2"

_model = None
_col = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL)
    return _model


def _get_col():
    global _col
    if _col is None:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _col = client.get_collection(COLLECTION)
    return _col


def search(query: str, n: int = 5) -> list[dict]:
    emb = _get_model().encode([query])[0]
    res = _get_col().query(
        query_embeddings=[emb.tolist()],
        n_results=n,
        include=["documents", "metadatas", "distances"],
    )
    return [
        {
            "id": res["ids"][0][i],
            "text": res["documents"][0][i],
            "source": res["metadatas"][0][i].get("source", ""),
            "section": res["metadatas"][0][i].get("section", ""),
            "version": res["metadatas"][0][i].get("version", ""),
            "score": res["distances"][0][i],
        }
        for i in range(len(res["ids"][0]))
    ]


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Qual o prazo de devolução?"
    print(f"\nQuery: {query}\n")
    for r in search(query):
        print(f"  [{r['score']:.4f}] {r['source']} | {r['section'][:60]}")
