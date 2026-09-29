# --------------------------------------------------
# Context Builder
# --------------------------------------------------
def build_context(retrieved_chunks: list) -> str:
    """
    Combine retrieved chunks into a context string.

    Each chunk contains text and source metadata.
    The context is later passed to the language model.
    """

    context_parts = []

    for chunk in retrieved_chunks:
        
        # Get the metadata stored in Qdrant.
        metadata = chunk.payload

        # Extract the relevant information.
        text = metadata.get("text", "")
        source = metadata.get("source", "Unknown source")
        chunk_number = metadata.get("chunk_number", "Unknown")

        # Skip empty chunks.
        if not text.strip():
            continue

        # Add source information to the chunk.
        context_part = (
            f"[Source: {source} | Chunk: {chunk_number}]\n"
            f"{text}"
        )

        context_parts.append(context_part)

    # Combine all chunks into one context string.
    context = "\n\n".join(context_parts)

    return context
