# --------------------------------------------------
# Qdrant Retriever
# --------------------------------------------------
from rag.m03_embeddings import embed_documents
from rag.m04_vector_store import QDRANT_COLLECTION

# --------------------------------------------------
# Semantische Suche
# --------------------------------------------------
def retrieve_chunks(
    client,
    question: str,
    limit: int = 5,
) -> list:
    """
    Sucht die relevantesten Chunks zu einer Benutzerfrage.
    """

    # Frage in einen Embedding-Vektor umwandeln
    query_vector = embed_documents([question])[0]

    # Ähnliche Vektoren in Qdrant suchen
    search_result = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_vector,
        limit=limit,
        with_payload=True,
    )

    # Gefundene Points zurückgeben
    return search_result.points
