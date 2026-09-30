# --------------------------------------------------
# Test: Chunks und Embeddings in Qdrant speichern
# --------------------------------------------------
from rag.m01_document_loader import load_document
from rag.m02_text_splitter import split_text_with_metadata
from rag.m03_embeddings import embed_documents
from rag.m04_vector_store import (
    get_qdrant_client,
    create_collection,
    store_embeddings,
    QDRANT_COLLECTION,
)

# --------------------------------------------------
# 1. Testdaten vorbereiten
# --------------------------------------------------
file_name = "rag-introduction.txt"

sample_text = """
Retrieval-Augmented Generation (RAG) combines
information retrieval with language models.

Documents are split into smaller chunks.
Each chunk is converted into an embedding vector.

The vectors are stored in a vector database.
When a user asks a question, relevant chunks
are retrieved and passed to the language model.
"""

# Text wiederholen, damit mehrere Chunks entstehen
sample_text = sample_text * 20

file_bytes = sample_text.encode("utf-8")

# --------------------------------------------------
# 2. Dokument laden und Chunks erzeugen
# --------------------------------------------------
text = load_document(file_name, file_bytes)

all_metadata = split_text_with_metadata(
    text=text,
    file_name=file_name,
)

# Texte aus den Metadaten extrahieren
all_chunks = [item["text"] for item in all_metadata]

print(f"Document loaded: {file_name}")
print(f"Chunks created: {len(all_chunks)}")

# --------------------------------------------------
# 3. Embeddings erzeugen
# --------------------------------------------------
print("\nGenerating embeddings...")

all_vectors = embed_documents(all_chunks)

print(f"Embeddings generated: {len(all_vectors)}")

# Prüfen, ob für jeden Chunk ein Embedding existiert
assert len(all_vectors) == len(all_chunks), (
    f"Erwartet: {len(all_chunks)} Embeddings, "
    f"erzeugt: {len(all_vectors)}"
)

# --------------------------------------------------
# 4. Verbindung zu Qdrant herstellen
# --------------------------------------------------
print("\nConnecting to Qdrant...")

client = get_qdrant_client()

create_collection(client)

print("Qdrant connection successful!")

# --------------------------------------------------
# 5. Chunks und Embeddings speichern
# --------------------------------------------------
print("\nStoring data in Qdrant...")

# Aktuellen Bestand vor dem Speichern ermitteln
collection_info = client.get_collection(
    collection_name=QDRANT_COLLECTION
)

points_before = collection_info.points_count

# Chunks und Embeddings speichern
stored_points = store_embeddings(
    client=client,
    chunks=all_chunks,
    vectors=all_vectors,
    metadata=all_metadata,
)

# Aktuellen Bestand nach dem Speichern ermitteln
collection_info = client.get_collection(
    collection_name=QDRANT_COLLECTION
)

points_after = collection_info.points_count

print(f"Points before: {points_before}")
print(f"Points after: {points_after}")
print(f"Points processed: {stored_points}")

# Prüfen, ob die erwartete Anzahl an Points verarbeitet wurde
assert stored_points == len(all_chunks), (
    f"Erwartet: {len(all_chunks)} Points, "
    f"verarbeitet: {stored_points}"
)

# Prüfen, ob die Collection die erwartete Anzahl enthält
assert points_after >= len(all_chunks), (
    f"Die Collection enthält nur {points_after} Points, "
    f"erwartet werden mindestens {len(all_chunks)}"
)

print("Storage check passed!")

# --------------------------------------------------
# 6. Gespeicherte Daten überprüfen
# --------------------------------------------------
collection_info = client.get_collection(
    collection_name=QDRANT_COLLECTION
)

print("\nQdrant collection information:")
print(f"Collection: {QDRANT_COLLECTION}")
print(f"Points in collection: {collection_info.points_count}")

# Prüfen, ob die Collection Points enthält
assert collection_info.points_count > 0, (
    "Die Qdrant-Collection enthält keine Points!"
)

print("Point count check passed!")

# --------------------------------------------------
# 7. Points aus Qdrant zurücklesen
# --------------------------------------------------
points, next_offset = client.scroll(
    collection_name=QDRANT_COLLECTION,
    limit=10,
    with_payload=True,
    with_vectors=True,
)

print(f"\nRetrieved points: {len(points)}")

# Prüfen, ob Points zurückgelesen wurden
assert len(points) > 0, "Es konnten keine Points aus Qdrant gelesen werden!"

# Ersten Point anzeigen
if points:
    first_point = points[0]

    print("\n--- First stored point ---")

    print(f"ID: {first_point.id}")
    print(f"Source: {first_point.payload['source']}")
    print(f"File type: {first_point.payload['file_type']}")
    print(f"Chunk number: {first_point.payload['chunk_number']}")
    print(f"Text: {first_point.payload['text'][:200]}...")

    print(f"Vector dimensions: {len(first_point.vector)}")
    print(f"First 5 values: {first_point.vector[:5]}")

    # Vektordimensionen überprüfen
    assert len(first_point.vector) == 768

    print("\nVector dimension check passed!")

# --------------------------------------------------
# 8. Ergebnis
# --------------------------------------------------
print("\nAll storage checks passed!")
