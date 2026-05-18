"""
index_legal_docs.py — CellMate RAG Indexer
Run this once (and again whenever you add new PDFs):

    python index_legal_docs.py

Reads every PDF in legal_docs/, chunks the text, embeds with
nomic-embed-text via Ollama, and persists to chroma_db/.

Requirements:
    pip install pymupdf chromadb requests
    ollama pull nomic-embed-text
"""

import os
import json
import hashlib
import requests
import chromadb
import fitz  # pymupdf

# ── Configuration ────────────────────────────────────────────
LEGAL_DOCS_DIR  = "legal_docs"
CHROMA_DIR      = "chroma_db"
COLLECTION_NAME = "legal_docs"
EMBED_MODEL     = "nomic-embed-text"
OLLAMA_URL      = "http://localhost:11434"

CHUNK_SIZE      = 800   # characters per chunk
CHUNK_OVERLAP   = 150   # overlap between chunks


# ── Helpers ──────────────────────────────────────────────────

def get_embedding(text: str) -> list[float]:
    """Embed a single text string via Ollama."""
    resp = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["embedding"]


def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """
    Extract text page by page from a PDF using pymupdf.
    Returns a list of {text, page} dicts.
    """
    pages = []
    doc = fitz.open(pdf_path)
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        if text:
            pages.append({"text": text, "page": page_num})
    doc.close()
    return pages


def chunk_pages(pages: list[dict], chunk_size: int, overlap: int) -> list[dict]:
    """
    Split page texts into overlapping chunks.
    Tracks which page each chunk came from.
    Returns list of {text, page, chunk_index}.
    """
    chunks = []
    for page_data in pages:
        text = page_data["text"]
        page = page_data["page"]
        start = 0
        chunk_index = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "text":        chunk_text,
                    "page":        page,
                    "chunk_index": chunk_index,
                })
            chunk_index += 1
            start += chunk_size - overlap
    return chunks


def file_hash(path: str) -> str:
    """MD5 of file contents — used to skip already-indexed files."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


# ── Main indexing logic ──────────────────────────────────────

def main():
    # Verify Ollama is up
    try:
        requests.get(OLLAMA_URL, timeout=5)
    except Exception:
        print("❌  Ollama is not running. Start it with: ollama serve")
        return

    # Verify nomic-embed-text is available
    try:
        get_embedding("test")
        print(f"✅  {EMBED_MODEL} is ready")
    except Exception as e:
        print(f"❌  Cannot reach {EMBED_MODEL}: {e}")
        print(f"    Run: ollama pull {EMBED_MODEL}")
        return

    # Set up ChromaDB
    os.makedirs(CHROMA_DIR, exist_ok=True)
    client     = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # Load previously indexed file hashes to skip unchanged files
    hash_store_path = os.path.join(CHROMA_DIR, "indexed_hashes.json")
    if os.path.exists(hash_store_path):
        with open(hash_store_path) as f:
            indexed_hashes = json.load(f)
    else:
        indexed_hashes = {}

    # Find PDFs
    if not os.path.isdir(LEGAL_DOCS_DIR):
        print(f"❌  Folder not found: {LEGAL_DOCS_DIR}/")
        return

    pdf_files = [
        f for f in os.listdir(LEGAL_DOCS_DIR)
        if f.lower().endswith(".pdf")
    ]

    if not pdf_files:
        print(f"⚠️   No PDFs found in {LEGAL_DOCS_DIR}/")
        return

    print(f"\n📂  Found {len(pdf_files)} PDF(s) in {LEGAL_DOCS_DIR}/\n")

    for pdf_file in pdf_files:
        pdf_path = os.path.join(LEGAL_DOCS_DIR, pdf_file)
        fhash    = file_hash(pdf_path)

        if indexed_hashes.get(pdf_file) == fhash:
            print(f"  ⏭   Skipping (unchanged): {pdf_file}")
            continue

        print(f"  📄  Indexing: {pdf_file}")

        # Remove old chunks for this file if re-indexing
        existing = collection.get(where={"source": pdf_file})
        if existing["ids"]:
            collection.delete(ids=existing["ids"])
            print(f"       🗑   Removed {len(existing['ids'])} old chunks")

        # Extract + chunk
        pages  = extract_text_from_pdf(pdf_path)
        chunks = chunk_pages(pages, CHUNK_SIZE, CHUNK_OVERLAP)
        print(f"       📝  {len(pages)} pages → {len(chunks)} chunks")

        # Embed + insert in batches of 50
        batch_size = 50
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]

            ids        = []
            embeddings = []
            documents  = []
            metadatas  = []

            for j, chunk in enumerate(batch):
                chunk_id = f"{pdf_file}__p{chunk['page']}__c{chunk['chunk_index']}"
                ids.append(chunk_id)
                documents.append(chunk["text"])
                metadatas.append({
                    "source":      pdf_file,
                    "page":        chunk["page"],
                    "chunk_index": chunk["chunk_index"],
                })
                emb = get_embedding(chunk["text"])
                embeddings.append(emb)

            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )
            print(f"       ✅  Batch {i // batch_size + 1}: {len(batch)} chunks indexed")

        indexed_hashes[pdf_file] = fhash

    # Persist hash store
    with open(hash_store_path, "w") as f:
        json.dump(indexed_hashes, f, indent=2)

    total = collection.count()
    print(f"\n🎉  Done. ChromaDB now holds {total} total chunks.")
    print(f"    Stored in: {CHROMA_DIR}/\n")


if __name__ == "__main__":
    main()