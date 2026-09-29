# --------------------------------------------------
# Test: Qdrant Retriever
# --------------------------------------------------
from rag.m04_vector_store import (
    get_qdrant_client,
    QDRANT_COLLECTION,
)

from app.rag.m05_retriever import retrieve_chunks

# --------------------------------------------------
# 1. Verbindung zu Qdrant herstellen
# --------------------------------------------------
client = get_qdrant_client()

print("Qdrant connection successful!")

# --------------------------------------------------
# 2. Frage vorbereiten
# --------------------------------------------------
user_question = "How does Retrieval-Augmented Generation work?"

print(f"\nQuestion: {user_question}")

# --------------------------------------------------
# 3. Semantische Suche durchführen
# --------------------------------------------------
search_result = retrieve_chunks(
    client=client,
    question=user_question,
    limit=5,
)

# --------------------------------------------------
# 4. Ergebnisse anzeigen
# --------------------------------------------------
print("\nTop 5 relevant chunks from Qdrant")

for rank, result in enumerate(search_result, start=1):
    print(
        f"\n{rank}. "
        f"{result.payload['source']} | "
        f"Chunk {result.payload['chunk_number']}"
    )

    print(f"Similarity: {result.score:.4f}")
    print(f"Point ID: {result.id}")

    print(f"Text: {result.payload['text'][:300]}")

# --------------------------------------------------
# 5. Ergebnisse überprüfen
# --------------------------------------------------
assert len(search_result) > 0

for result in search_result:

    assert result.payload is not None
    assert "text" in result.payload
    assert result.score is not None

print("\nAll retriever checks passed!")
