# --------------------------------------------------
# Document Indexer
# --------------------------------------------------
from rag.m01_document_loader import load_document
from rag.m02_text_splitter import (
    split_text_with_metadata,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)
from rag.m03_embeddings import (
    embed_documents,
    EMBEDDING_MODEL,
)
from rag.m04_vector_store import (
    get_qdrant_client,
    create_collection,
    store_embeddings,
    QDRANT_COLLECTION,
)

def index_documents(files: list[tuple[str, bytes]]) -> dict:
    """
    Process uploaded documents and store their embeddings in Qdrant.

    Existing collection data is replaced after successful processing.
    """

    # Connect to Qdrant.
    client = get_qdrant_client()

    all_chunks = []
    all_metadata = []
    document_debug = []

    next_chunk_id = 0

    # --------------------------------------------------
    # Step 1: Load documents and split text into chunks.
    # --------------------------------------------------
    for file_name, file_bytes in files:

        # Extract text from the document.
        text = load_document(file_name, file_bytes)

        if not text.strip():
            continue

        # Split the extracted text into chunks.
        metadata = split_text_with_metadata(
            text=text,
            file_name=file_name,
            start_chunk_id=next_chunk_id,
        )

        # Collect chunks and metadata for indexing.
        all_metadata.extend(metadata)
        all_chunks.extend(
            item["text"] for item in metadata
        )

        # Save information for the Debug tab.
        document_debug.append(
            {
                "filename": file_name,
                "file_type": file_name.split(".")[-1].lower(),
                "character_count": len(text),
                "extracted_text": text,
                "chunk_count": len(metadata),
                "chunks": metadata,
            }
        )

        next_chunk_id += len(metadata)

    # Stop if no usable text was extracted.
    if not all_chunks:
        raise ValueError(
            "No text could be extracted from the uploaded documents."
        )

    # --------------------------------------------------
    # Step 2: Generate embeddings.
    # --------------------------------------------------
    vectors = embed_documents(all_chunks)

    if not vectors:
        raise ValueError("No embeddings were generated.")

    vector_dimension = len(vectors[0])

    # --------------------------------------------------
    # Step 3: Replace the Qdrant collection.
    # --------------------------------------------------
    # Only delete the old collection after successful
    # document processing and embedding generation.
    if client.collection_exists(QDRANT_COLLECTION):
        client.delete_collection(QDRANT_COLLECTION)

    create_collection(client)

    # --------------------------------------------------
    # Step 4: Store embeddings and metadata in Qdrant.
    # --------------------------------------------------
    stored_count = store_embeddings(
        client=client,
        chunks=all_chunks,
        vectors=vectors,
        metadata=all_metadata,
    )

    # Read the collection information from Qdrant.
    collection_info = client.get_collection(QDRANT_COLLECTION)

    # --------------------------------------------------
    # Return indexing results and debug information.
    # --------------------------------------------------
    return {
        "document_count": len(document_debug),
        "chunk_count": stored_count,
        "debug": {
            "documents": document_debug,
            "embedding_model": EMBEDDING_MODEL,
            "vector_dimension": vector_dimension,
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP,
            "collection_name": QDRANT_COLLECTION,
            "stored_points": collection_info.points_count,
        },
    }
