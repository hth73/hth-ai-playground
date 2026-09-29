# --------------------------------------------------
# Text in Chunks aufteilen und Metadaten hinzufügen
# --------------------------------------------------
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Einstellungen für die Textaufteilung
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def split_text(text: str) -> list[str]:
    """
    Teilt einen Text in kleinere Abschnitte (Chunks) auf.
    """

    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " ", ""],
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    chunks = text_splitter.split_text(text)

    return chunks

def split_text_with_metadata(
    text: str,
    file_name: str,
    start_chunk_id: int = 0,
) -> list[dict]:
    """
    Erstellt Chunks und ergänzt die zugehörigen Metadaten.
    """

    # Text in Chunks aufteilen
    chunks = split_text(text)

    # Dateityp aus dem Dateinamen ermitteln
    file_type = file_name.split(".")[-1].lower()

    # Liste für Chunks mit Metadaten
    all_metadata = []

    # Jeden Chunk mit Metadaten versehen
    for chunk_number, chunk in enumerate(chunks):

        metadata = {
            "chunk_id": start_chunk_id + chunk_number,
            "source": file_name,
            "file_type": file_type,
            "chunk_number": chunk_number + 1,
            "text": chunk,
        }

        all_metadata.append(metadata)

    return all_metadata
