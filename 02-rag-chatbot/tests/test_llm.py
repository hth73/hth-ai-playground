# --------------------------------------------------
# Test: LLM (Large Language Model) answer generation.
# --------------------------------------------------
from rag.m07_llm import generate_answer

# --------------------------------------------------
# Define a test context.
# --------------------------------------------------
context = """
RAG stands for Retrieval-Augmented Generation.
A RAG system retrieves relevant information from external documents
and provides this information to a language model.
"""

# --------------------------------------------------
# Define a test question.
# --------------------------------------------------
question = "What does RAG stand for?"

# --------------------------------------------------
# Generate the answer.
# --------------------------------------------------
answer = generate_answer(context, question)

# --------------------------------------------------
# Display the result.
# --------------------------------------------------
print("Question:")
print(question)

print("\nAnswer:")
print(answer)

# --------------------------------------------------
# Validate the response.
# --------------------------------------------------
assert answer.strip(), "The model returned an empty answer."

print("\nAll LLM checks passed!")
