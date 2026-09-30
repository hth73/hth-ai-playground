# --------------------------------------------------
# Persistent Document Indexer
# --------------------------------------------------
from pathlib import Path

from qdrant_client.models import FieldCondition, Filter, MatchValue

from rag.m01_document_loader import load_document
from rag.m02_text_splitter import (
    split_text_with_metadata,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)
from rag.m03_embeddings import embed_documents, EMBEDDING_MODEL
from rag.m04_vector_store import (
    create_collection,
    get_qdrant_client,
    store_embeddings,
    QDRANT_COLLECTION,
)
from rag.m10_document_store import (
    list_documents,
    mark_document_indexed,
    update_document_status,
)


def index_document(document_id: str, force: bool = False, include_debug: bool = False):
    """Index one persisted document. Optionally return the run's debug data.

    The default return remains an integer chunk count for compatibility with
    existing scripts and tests. Set include_debug=True for the Streamlit UI.
    """
    if not document_id or not document_id.strip():
        raise ValueError("document_id darf nicht leer sein.")

    document = next(
        (item for item in list_documents() if item["document_id"] == document_id),
        None,
    )
    if document is None:
        raise ValueError(f"Document not found: {document_id}")

    if document["status"] == "indexed" and not force:
        if include_debug:
            raise ValueError("Das Dokument ist bereits indexiert; kein neuer Debug-Lauf vorhanden.")
        return document["chunk_count"]

    try:
        stored_path = Path(document["stored_path"])
        file_bytes = stored_path.read_bytes()
        text = load_document(document["filename"], file_bytes)
        if not text.strip():
            raise ValueError("Das Dokument enthält keinen extrahierbaren Text.")

        chunk_metadata = split_text_with_metadata(
            text=text,
            file_name=document["filename"],
        )
        chunks = [item["text"] for item in chunk_metadata]
        if not chunks:
            raise ValueError("Die Dokumentverarbeitung hat keine Chunks erzeugt.")

        vectors = embed_documents(chunks)
        if len(vectors) != len(chunks):
            raise ValueError("Anzahl der Chunks und Embeddings stimmt nicht überein.")

        client = get_qdrant_client()
        create_collection(client)

        if force and document["status"] == "indexed":
            from rag.m04_vector_store import delete_document_embeddings
            delete_document_embeddings(client, document_id)

        stored_count = store_embeddings(
            client=client,
            chunks=chunks,
            vectors=vectors,
            metadata=chunk_metadata,
            document_id=document_id,
        )
        mark_document_indexed(document_id, stored_count)

        if not include_debug:
            return stored_count

        # Read back the exact persisted Qdrant point IDs so the existing
        # Debug tab's retrieve() calls continue to work without modification.
        points, _ = client.scroll(
            collection_name=QDRANT_COLLECTION,
            scroll_filter=Filter(
                must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
            ),
            limit=max(stored_count, 1),
            with_payload=True,
            with_vectors=False,
        )
        points.sort(key=lambda point: point.payload.get("chunk_number", 0))
        debug_chunks = []
        for metadata, point in zip(chunk_metadata, points):
            chunk_debug = dict(metadata)
            chunk_debug["chunk_id"] = point.id
            debug_chunks.append(chunk_debug)

        collection_info = client.get_collection(QDRANT_COLLECTION)
        debug = {
            "documents": [{
                "filename": document["filename"],
                "file_type": document["file_type"],
                "character_count": len(text),
                "extracted_text": text,
                "chunk_count": len(chunk_metadata),
                "chunks": debug_chunks,
            }],
            "embedding_model": EMBEDDING_MODEL,
            "vector_dimension": len(vectors[0]),
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP,
            "collection_name": QDRANT_COLLECTION,
            "stored_points": collection_info.points_count,
        }
        return {"chunk_count": stored_count, "debug": debug}

    except Exception as error:
        update_document_status(
            document_id=document_id,
            status="failed",
            error_message=str(error),
        )
        raise
