# --------------------------------------------------
# Test: Embeddings mit Ollama erzeugen
# --------------------------------------------------
from rag.m03_embeddings import embed_documents

# Testdaten
chunks = [
    "Retrieval-Augmented Generation combines information retrieval with language models.",
    "Embeddings represent text as numerical vectors.",
    "Qdrant stores vectors for semantic search.",
]

# Embeddings erzeugen
vectors = embed_documents(chunks)

# Ergebnisse überprüfen
assert len(vectors) == len(chunks)

for index, vector in enumerate(vectors):

    assert isinstance(vector, list)
    assert len(vector) > 0

    print(f"\nChunk {index + 1}")
    print(f"Dimensions: {len(vector)}")
    print(f"First 5 values: {vector[:5]}")

print("\nAll embedding checks passed!")
