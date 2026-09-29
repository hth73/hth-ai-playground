# --------------------------------------------------
# RAG Pipeline
# --------------------------------------------------
from rag.m04_vector_store import get_qdrant_client
from rag.m05_retriever import retrieve_chunks
from rag.m06_context_builder import build_context
from rag.m07_llm import generate_answer

def run_rag_pipeline(question: str, limit: int = 5) -> dict:
    """
    Execute the complete RAG pipeline.

    1. Retrieve relevant chunks from Qdrant.
    2. Build a context from the retrieved chunks.
    3. Generate an answer using the LLM.

    Return the answer and intermediate results.
    """

    # Step 1: Connect to Qdrant.
    client = get_qdrant_client()

    # Step 2: Retrieve relevant chunks.
    retrieved_chunks = retrieve_chunks(
        client=client,
        question=question,
        limit=limit,
    )

    # Step 3: Build the context.
    context = build_context(retrieved_chunks)

    # Step 4: Generate the answer.
    answer = generate_answer(
        context=context,
        question=question,
    )

    # Step 5: Return all results.
    return {
        "question": question,
        "answer": answer,
        "context": context,
        "retrieved_chunks": retrieved_chunks,
    }
