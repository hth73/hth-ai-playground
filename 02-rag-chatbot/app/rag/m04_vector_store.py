# --------------------------------------------------
# Qdrant Vector Database
# --------------------------------------------------
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

# --------------------------------------------------
# Konfiguration
# --------------------------------------------------
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_COLLECTION = "rag_chatbot_documents"

# Embedding-Dimensionen von nomic-embed-text
VECTOR_SIZE = 768


# --------------------------------------------------
# Verbindung zu Qdrant herstellen
# --------------------------------------------------
def get_qdrant_client() -> QdrantClient:
    """
    Stellt eine Verbindung zu Qdrant her und prüft die Erreichbarkeit.
    """
    client = QdrantClient(
        host=QDRANT_HOST,
        port=QDRANT_PORT,
    )

    # Verbindung testen
    client.get_collections()

    return client


# --------------------------------------------------
# Collection erstellen
# --------------------------------------------------
def create_collection(client: QdrantClient) -> None:
    """
    Erstellt die Qdrant-Collection, falls sie noch nicht existiert.
    """
    if not client.collection_exists(QDRANT_COLLECTION):
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )


# --------------------------------------------------
# Chunks, Vektoren und Metadaten speichern
# --------------------------------------------------
def store_embeddings(
    client: QdrantClient,
    chunks: list[str],
    vectors: list[list[float]],
    metadata: list[dict],
    document_id: str,
) -> int:
    """
    Speichert Chunks, Embeddings und Metadaten in Qdrant.

    Jeder Point erhält eine eindeutige UUID als ID und wird über
    document_id seinem Quelldokument zugeordnet.
    """
    if not document_id or not document_id.strip():
        raise ValueError("document_id darf nicht leer sein.")

    if not (len(chunks) == len(vectors) == len(metadata)):
        raise ValueError(
            "Anzahl der Chunks, Vektoren und Metadaten stimmt nicht überein."
        )

    points = []

    for chunk, vector, chunk_metadata in zip(chunks, vectors, metadata):
        payload = dict(chunk_metadata)
        payload["text"] = chunk
        payload["document_id"] = document_id

        point = PointStruct(
            id=str(uuid4()),
            vector=vector,
            payload=payload,
        )
        points.append(point)

    if points:
        client.upsert(
            collection_name=QDRANT_COLLECTION,
            points=points,
            wait=True,
        )

    return len(points)


# --------------------------------------------------
# Alle Embeddings eines Dokuments löschen
# --------------------------------------------------
def delete_document_embeddings(
    client: QdrantClient,
    document_id: str,
) -> None:
    """
    Löscht alle Points, die zur angegebenen document_id gehören.
    """
    if not document_id or not document_id.strip():
        raise ValueError("document_id darf nicht leer sein.")

    client.delete(
        collection_name=QDRANT_COLLECTION,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id),
                )
            ]
        ),
        wait=True,
    )
