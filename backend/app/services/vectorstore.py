import os
import chromadb
from sentence_transformers import SentenceTransformer

def get_embedder(model_name: str):
    return SentenceTransformer(model_name)

def get_chroma_client(chroma_dir: str):
    os.makedirs(chroma_dir, exist_ok=True)
    return chromadb.PersistentClient(path=chroma_dir)

def get_collection(client, name: str = "documents"):
    return client.get_or_create_collection(name=name)

def upsert_document(collection, embedder, doc_type: str, pages: list[dict], doc_id: str):
    ids, embeddings, metadatas, documents = [], [], [], []
    for p in pages:
        page_num = p["page"]
        for idx, chunk in enumerate(_safe_chunks(p["text"])):
            emb = embedder.encode(chunk).tolist()
            ids.append(f"{doc_id}_{doc_type}_p{page_num}_c{idx}")
            embeddings.append(emb)
            metadatas.append({"source": doc_type, "page": page_num, "doc_id": doc_id})
            documents.append(chunk)
    if ids:
        collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)

def query(collection, embedder, query_text: str, k: int = 6, source_filter: str | None = None):
    emb = embedder.encode(query_text).tolist()
    where = {"source": source_filter} if source_filter else None
    res = collection.query(query_embeddings=[emb], n_results=k, where=where)
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    return [{"text": d, "meta": m} for d, m in zip(docs, metas)]

def _safe_chunks(text: str):
    from app.services.chunking import chunk_text
    return chunk_text(text)