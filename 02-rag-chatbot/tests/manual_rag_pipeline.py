# --------------------------------------------------
# Test: RAG Pipeline
# --------------------------------------------------
from rag.m08_rag_pipeline import run_rag_pipeline

# Define a question for the RAG pipeline.
question = "How does Retrieval-Augmented Generation work?"

# Execute the complete RAG pipeline.
result = run_rag_pipeline(question)

# Display the question and answer.
print("Question:")
print(result["question"])

print("\nAnswer:")
print(result["answer"])

# Display the retrieved chunks.
print("\nRetrieved chunks:")

for chunk in result["retrieved_chunks"]:
    print(f"\nSource: {chunk.payload.get('source')}")
    print(f"Chunk: {chunk.payload.get('chunk_number')}")
    print(f"Score: {chunk.score:.4f}")
    print(f"Text: {chunk.payload.get('text')[:200]}...")

# Validate the result.
assert result["answer"].strip(), "The answer is empty."
assert result["context"].strip(), "The context is empty."
assert len(result["retrieved_chunks"]) > 0, "No chunks were retrieved."

print("\nAll RAG pipeline checks passed!")
