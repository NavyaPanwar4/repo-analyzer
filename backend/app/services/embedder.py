from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")  

def embed_texts(texts: list) -> list:
    if not texts:
        return []
    embeddings = model.encode(texts, show_progress_bar=False)
    return embeddings.tolist()

def embed_single(text: str) -> list:
    return embed_texts([text])[0]