# --------------------------------------------------
# Text in Embedding-Vektoren umwandeln
# --------------------------------------------------
import json
from urllib.request import Request, urlopen

# Ollama API
OLLAMA_URL = "http://localhost:11434/api/embed"

# Verwendetes Embedding-Modell
EMBEDDING_MODEL = "nomic-embed-text"

def embed_documents(chunks: list[str]) -> list[list[float]]:
    """
    Wandelt eine Liste von Text-Chunks in Embedding-Vektoren um.
    """

    # API-Anfrage vorbereiten
    payload = {
        "model": EMBEDDING_MODEL,
        "input": chunks,
    }

    # Daten in JSON umwandeln
    data = json.dumps(payload).encode("utf-8")

    # HTTP-Request erstellen
    request = Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    # Anfrage an Ollama senden
    with urlopen(request, timeout=120) as response:
        result = json.loads(response.read().decode("utf-8"))

    # Embedding-Vektoren aus der Antwort zurückgeben
    return result["embeddings"]
