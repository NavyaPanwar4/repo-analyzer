import chromadb
from chromadb.config import Settings
from app.services.embedder import embed_texts

CHROMA_PATH = "./chroma_db"

def get_client():
    return chromadb.PersistentClient(path=CHROMA_PATH)

def get_or_create_collection(repo_id: str):
    client = get_client()
    return client.get_or_create_collection(
        name=repo_id,
        metadata={"hnsw:space": "cosine"},
    )

def store_chunks(repo_id: str, chunks: list[dict]):
    """
    Embed and store all chunks into a Chroma collection.
    repo_id is used as the collection name — one collection per repo.
    """
    collection = get_or_create_collection(repo_id)

    texts = [c["text"] for c in chunks]
    ids = [c["id"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    # Embed in batches of 100
    all_embeddings = []
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        all_embeddings.extend(embed_texts(batch))

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=all_embeddings,
        metadatas=metadatas,
    )
    return len(chunks)

def query_chunks(repo_id: str, question: str, n_results: int = 8) -> list[dict]:
    """
    Embed a question and retrieve the top-n most relevant chunks.
    """
    from app.services.embedder import embed_single
    collection = get_or_create_collection(repo_id)

    query_embedding = embed_single(question)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({
            "text": doc,
            "metadata": meta,
            "score": round(1 - dist, 4),  # cosine similarity
        })
    return hits

def delete_collection(repo_id: str):
    client = get_client()
    try:
        client.delete_collection(repo_id)
    except Exception:
        pass