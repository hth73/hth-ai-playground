# --------------------------------------------------
# Connect to LLM (Large Language Model) for answer generation.
# --------------------------------------------------
import json
from urllib.request import Request, urlopen

# --------------------------------------------------
# Ollama API configuration.
# --------------------------------------------------
OLLAMA_URL = "http://localhost:11434/api/chat"
CHAT_MODEL = "qwen3:1.7b"

def build_messages(context: str, question: str) -> list[dict]:
    """
    Build the messages sent to the chat model.
    """

    # Define the system instructions.
    system_prompt = (
        "You are a helpful assistant. "
        "Answer the user's question using only the provided context. "
        "If the context does not contain enough information, "
        "say that you do not know. "
        "Do not invent facts."
    )

    # Build the user prompt.
    user_prompt = (
        f"Context:\n{context}\n\n"
        f"Question:\n{question}"
    )

    # Return the messages.
    return [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]

def generate_answer(context: str, question: str) -> str:
    """
    Generate an answer using the local Ollama chat model.

    The retrieved context is provided to the model
    to answer the user's question.
    """

    # Define the system instructions.
    system_prompt = (
        "You are a helpful assistant. "
        "Answer the user's question using only the provided context. "
        "If the context does not contain enough information, "
        "say that you do not know. "
        "Do not invent facts."
    )

    # Build the user prompt.
    user_prompt = (
        f"Context:\n{context}\n\n"
        f"Question:\n{question}"
    )

    # Prepare the API request.
    payload = {
        "model": CHAT_MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        "stream": False,
    }

    # Convert the payload to JSON.
    data = json.dumps(payload).encode("utf-8")

    # Create the HTTP request.
    request = Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    # Send the request and read the response.
    with urlopen(request, timeout=120) as response:
        result = json.loads(response.read().decode("utf-8"))

    # Extract the generated answer.
    answer = result["message"]["content"]

    return answer.strip()
