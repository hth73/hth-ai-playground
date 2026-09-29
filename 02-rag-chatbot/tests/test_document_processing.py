# --------------------------------------------------
# Test: Dokumentenverarbeitung und Metadaten
# --------------------------------------------------
from rag.m01_document_loader import load_document
from rag.m02_text_splitter import split_text_with_metadata

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

# Text in Bytes umwandeln, wie es später beim Datei-Upload passiert
file_bytes = sample_text.encode("utf-8")

# --------------------------------------------------
# 2. Dokument laden
# --------------------------------------------------
text = load_document(file_name, file_bytes)

print("Document loaded successfully.")
print(f"Text length: {len(text)} characters")

# --------------------------------------------------
# 3. Chunks mit Metadaten erzeugen
# --------------------------------------------------
all_metadata = split_text_with_metadata(
    text=text,
    file_name=file_name,
)

print(f"\nNumber of chunks: {len(all_metadata)}")

# --------------------------------------------------
# 4. Metadaten überprüfen
# --------------------------------------------------
# Es müssen mehrere Chunks vorhanden sein
assert len(all_metadata) > 1

# Alle Chunks durchlaufen und prüfen
for index, metadata in enumerate(all_metadata):

    # Chunk-ID muss fortlaufend sein
    assert metadata["chunk_id"] == index

    # Dateiname muss korrekt übernommen worden sein
    assert metadata["source"] == file_name

    # Dateityp muss korrekt erkannt worden sein
    assert metadata["file_type"] == "txt"

    # Chunk-Nummer beginnt bei 1
    assert metadata["chunk_number"] == index + 1

    # Der Chunk muss Text enthalten
    assert isinstance(metadata["text"], str)
    assert len(metadata["text"]) > 0

print("\nAll metadata checks passed!")

# --------------------------------------------------
# 5. Beispiel ausgeben
# --------------------------------------------------
print("\n--- First chunk ---")

print(f"Chunk ID:     {all_metadata[0]['chunk_id']}")
print(f"Source:       {all_metadata[0]['source']}")
print(f"File type:    {all_metadata[0]['file_type']}")
print(f"Chunk number: {all_metadata[0]['chunk_number']}")
print(f"Text:         {all_metadata[0]['text'][:200]}...")
