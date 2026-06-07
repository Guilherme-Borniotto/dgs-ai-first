"""
Ingestão: lê os 5 documentos .md, aplica chunking por tipo de documento,
gera embeddings e persiste no ChromaDB.

Estratégia de chunking por tipo (não por token fixo):
- POL-001:      por subseção ### (cada regra é uma unidade semântica independente)
- PROC-042 v1/v2: por bloco lógico (fórmula, tabela de multiplicadores, prazo, condições)
- SLA-2024:     por tabela + bloco de definições
- FAQ:          por item individual ## Item N
"""

import re
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

DOCS_DIR = Path(__file__).parent.parent / "assets" / "anexos" / "anexo-a-documentos-individuais"
CHROMA_DIR = Path(__file__).parent / "chroma_db"
COLLECTION = "novatech"
MODEL = "all-MiniLM-L6-v2"


def _meta(content: str) -> dict:
    v = re.search(r"\*\*Versão:\*\*\s*(.+)", content)
    d = re.search(r"\*\*(?:Última atualização|Data de emissão):\*\*\s*(.+)", content)
    return {
        "version": v.group(1).strip() if v else "N/A",
        "date": d.group(1).strip() if d else "N/A",
    }


def _breadcrumb(source: str, meta: dict, section: str) -> str:
    return f"[Fonte: {source} | Versão: {meta['version']} | Data: {meta['date']} | Seção: {section}]"


def chunk_by_subsection(content: str, source: str) -> list[dict]:
    """Divide por cabeçalhos ### (subseções de terceiro nível)."""
    meta = _meta(content)
    parts = re.split(r"(?=\n### )", content)
    chunks = []
    for i, part in enumerate(parts):
        part = part.strip()
        if len(part) < 80:
            continue
        title = re.match(r"^(#{2,3} .+)", part)
        section = title.group(1) if title else f"bloco-{i}"
        chunks.append({
            "id": f"{source}--{i:02d}",
            "text": f"{_breadcrumb(source, meta, section)}\n\n{part}",
            "metadata": {"source": source, **meta, "section": section},
        })
    return chunks


def chunk_by_logical_block(content: str, source: str) -> list[dict]:
    """Divide por blocos lógicos: ## e ### de segundo e terceiro nível."""
    meta = _meta(content)
    parts = re.split(r"(?=\n#{2,3} )", content)
    chunks = []
    for i, part in enumerate(parts):
        part = part.strip()
        if len(part) < 80:
            continue
        title = re.match(r"^(#{2,3} .+)", part)
        section = title.group(1) if title else f"bloco-{i}"
        chunks.append({
            "id": f"{source}--{i:02d}",
            "text": f"{_breadcrumb(source, meta, section)}\n\n{part}",
            "metadata": {"source": source, **meta, "section": section},
        })
    return chunks


def chunk_by_faq_item(content: str, source: str) -> list[dict]:
    """Divide por item do FAQ (## Item N)."""
    meta = _meta(content)
    parts = re.split(r"(?=\n## Item \d+)", content)
    chunks = []
    for i, part in enumerate(parts):
        part = part.strip()
        if len(part) < 60:
            continue
        title = re.match(r"^(## Item \d+ .+)", part)
        section = title.group(1)[:60] if title else f"item-{i}"
        chunks.append({
            "id": f"{source}--{i:02d}",
            "text": f"{_breadcrumb(source, meta, section)}\n\n{part}",
            "metadata": {"source": source, **meta, "section": section},
        })
    return chunks


CHUNKERS = {
    "POL-001-politica-devolucao": chunk_by_subsection,
    "PROC-042-frete-especial-v1": chunk_by_logical_block,
    "PROC-042-v2-frete-especial-revisado": chunk_by_logical_block,
    "SLA-2024-tabela-sla-clientes": chunk_by_logical_block,
    "FAQ-atendimento": chunk_by_faq_item,
}

def ingest():
    all_chunks = []
    for filepath in sorted(DOCS_DIR.glob("*.md")):
        stem = filepath.stem
        content = filepath.read_text(encoding="utf-8")
        chunker = CHUNKERS.get(stem, chunk_by_logical_block)
        chunks = chunker(content, stem)
        all_chunks.extend(chunks)
        print(f"  {filepath.name}: {len(chunks)} chunks")

    print(f"\nTotal: {len(all_chunks)} chunks")

    model = SentenceTransformer(MODEL)
    embeddings = model.encode([c["text"] for c in all_chunks], show_progress_bar=True)

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    
    col = client.create_collection(COLLECTION)
    col.add(
        ids=[c["id"] for c in all_chunks],
        embeddings=embeddings.tolist(),
        documents=[c["text"] for c in all_chunks],
        metadatas=[c["metadata"] for c in all_chunks],
    )
    print("Ingestão concluída.")


if __name__ == "__main__":
    ingest()

