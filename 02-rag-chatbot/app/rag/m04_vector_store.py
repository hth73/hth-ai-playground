# --------------------------------------------------
# Qdrant Vector Database
# --------------------------------------------------
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

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
) -> int:
    """
    Speichert Chunks, Embeddings und Metadaten in Qdrant.
    """

    # Prüfen, ob alle Listen gleich viele Einträge enthalten
    if not (len(chunks) == len(vectors) == len(metadata)):
        raise ValueError(
            "Anzahl der Chunks, Vektoren und Metadaten stimmt nicht überein."
        )

    # Points für Qdrant vorbereiten
    points = []

    for index, vector in enumerate(vectors):
        point = PointStruct(
            id=index,
            vector=vector,
            payload=metadata[index],
        )
        points.append(point)

    # Points in Qdrant speichern
    client.upsert(
        collection_name=QDRANT_COLLECTION,
        points=points,
        wait=True,
    )
    return len(points)
