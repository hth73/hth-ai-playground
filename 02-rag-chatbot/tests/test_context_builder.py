# --------------------------------------------------
# Context Builder Test
# --------------------------------------------------
from types import SimpleNamespace
from rag.m06_context_builder import build_context

# Simulate the Qdrant results.
retrieved_chunks = [
    SimpleNamespace(
        payload={
            "text": "RAG combines retrieval with generative AI.",
            "source": "rag-introduction.pdf",
            "chunk_number": 1,
        }
    ),
    SimpleNamespace(
        payload={
            "text": "The retrieved context improves answer relevance.",
            "source": "rag-introduction.pdf",
            "chunk_number": 2,
        }
    ),
]

# --------------------------------------------------
# Build the context.
# --------------------------------------------------
context = build_context(retrieved_chunks)
print(context)

# --------------------------------------------------
# Validate the result.
# --------------------------------------------------
assert "RAG combines retrieval" in context
assert "answer relevance" in context
assert "rag-introduction.pdf" in context
assert "Chunk: 1" in context
assert "Chunk: 2" in context

print("\nAll context builder checks passed!")
