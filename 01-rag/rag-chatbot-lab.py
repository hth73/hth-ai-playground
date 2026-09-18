# --------------------------------------------------
# Import Python Modules
# --------------------------------------------------
import os
import math
import pdfplumber
import streamlit as st

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --------------------------------------------------
# Application constants
# --------------------------------------------------
VERSION = "0.0.1"

# --------------------------------------------------
# OpenAI API Key
# --------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --------------------------------------------------
# Script Aufbau
# --------------------------------------------------
# 1. WebUI erstellen
# 2. Dokumente hinzufügen
# 3. Text Extraction
# 4. Chunks erzeugen
# 5. Metadaten hinzufügen
# 6. Chunks in Embeddings konvertieren
# 7. Similarity Test
# 8. Manueller Retriever
# 9. Qdrant DB erstellen
#    ├── Collection
#    ├── Points speichern
#    └── Qdrant Retriever
# 10. RAG Pipeline
#     ├── 10.1 Retrieval
#     ├── 10.2 Context
#     ├── 10.3 Prompt
#     └── 10.4 LLM

# --------------------------------------------------
# 1. WebUI erstellen
# --------------------------------------------------
st.header("Zeig mir den kompletten Retrieval Augmented Generation (RAG) Prozess", text_alignment="center", divider="grey")

# --------------------------------------------------
# 2. Dokumente hinzufügen
# --------------------------------------------------
with st.sidebar:
    st.title("Meine Dokumente")
    files = st.file_uploader(
        "Hier kannst du PDF/TXT Dateien hochladen "
        "und anschließend über den Manual oder Qdrant Retriever Fragen stellen.",
        type=["pdf", "txt"],
        accept_multiple_files=True
    )

# --------------------------------------------------
# Datenstrukturen
# --------------------------------------------------
all_chunks = []
all_vectors = []
all_metadata = []

# --------------------------------------------------
# Embedding Modul laden
# --------------------------------------------------
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=OPENAI_API_KEY
)

# --------------------------------------------------
# 3. Text Extraction
# --------------------------------------------------
if files:
    for file in files:
        st.subheader(f"Document: {file.name}")

        # ------------------------------------------
        # Text Extraction
        # ------------------------------------------
        if file.name.lower().endswith(".pdf"):
            text = ""
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()

                    if page_text:
                        text += page_text + "\n"

        elif file.name.lower().endswith(".txt"):
            text = file.read().decode("utf-8")

        else:
            st.warning(
                f"Unsupported file type: {file.name}"
            )
            continue

        # --------------------------------------------------
        # 4. Chunks erzeugen
        # --------------------------------------------------
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ". ", " ", ""],
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_text(text)

        st.write(
            f"Number of chunks: {len(chunks)}"
        )

        # --------------------------------------------------
        # 5. Metadaten hinzufügen
        # --------------------------------------------------
        file_type = file.name.split(".")[-1].lower()
        for chunk_number, chunk in enumerate(chunks):

            metadata = {
                "chunk_id": len(all_chunks),
                "source": file.name,
                "file_type": file_type,
                "chunk_number": chunk_number + 1,
                "text": chunk
            }
            all_metadata.append(metadata)

        # --------------------------------------------------
        # 6. Chunks in Embeddings konvertieren
        # --------------------------------------------------
        vectors = embeddings.embed_documents(chunks)
        all_chunks.extend(chunks)
        all_vectors.extend(vectors)

# --------------------------------------------------
# Chunks und Embeddings anzeigen
# --------------------------------------------------
st.header("Chunks und Embeddings anzeigen", divider="grey")

if all_chunks:
    selected_chunk = st.selectbox(
        "Select a chunk",
        range(len(all_chunks)),
        format_func=lambda i: (
            f"{all_metadata[i]['source']} | "
            f"Chunk {all_metadata[i]['chunk_number']}"
        )
    )
    st.write("Selected chunk:")
    st.code(all_chunks[selected_chunk])

    selected_vector = all_vectors[selected_chunk]

    st.write("Embedding:")
    st.write(f"Dimensions: {len(selected_vector)}")

    st.write("First 20 values:")
    st.code(selected_vector[:20])

# --------------------------------------------------
# Metadaten anzeigen
# --------------------------------------------------
if all_metadata:
    st.header("Metadaten anzeigen", divider="grey")

    selected_metadata = st.selectbox(
        "Select a chunk",
        range(len(all_metadata)),
        format_func=lambda i: (
            f"{all_metadata[i]['source']} | "
            f"Chunk {all_metadata[i]['chunk_number']}"
        ),
        key="metadata_chunk"
    )
    metadata = all_metadata[selected_metadata]

    st.write("Chunk ID:")
    st.write(metadata["chunk_id"])

    st.write("Source:")
    st.write(metadata["source"])

    st.write("File Type:")
    st.write(metadata["file_type"])

    st.write("Chunk Number:")
    st.write(metadata["chunk_number"])

    st.write("Text:")
    st.code(metadata["text"])

# --------------------------------------------------
# 7. Similarity Test
# --------------------------------------------------
st.header("Embedding Similarity Test", divider="grey")

if len(all_chunks) >= 2:
    chunk_options = [
        f"Chunk {i + 1}: "
        f"{chunk[:80].replace(chr(10), ' ')}..."
        for i, chunk in enumerate(all_chunks)
    ]

    chunk_a_index = st.selectbox(
        "Select Chunk A",
        range(len(all_chunks)),
        format_func=lambda i: chunk_options[i],
        key="chunk_a"
    )

    chunk_b_index = st.selectbox(
        "Select Chunk B",
        range(len(all_chunks)),
        format_func=lambda i: chunk_options[i],
        key="chunk_b"
    )
    vector_a = all_vectors[chunk_a_index]
    vector_b = all_vectors[chunk_b_index]

    # --------------------------------------------------
    # Cosine Similarity
    # --------------------------------------------------
    def cosine_similarity(vector_a, vector_b):
        dot_product = sum(
            a * b
            for a, b in zip(vector_a, vector_b)
        )

        magnitude_a = math.sqrt(
            sum(a * a for a in vector_a)
        )

        magnitude_b = math.sqrt(
            sum(b * b for b in vector_b)
        )

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot_product / (
            magnitude_a * magnitude_b
        )

    similarity = cosine_similarity(
        vector_a,
        vector_b
    )

    st.subheader("Selected Chunks")
    st.write("### Chunk A")
    st.code(all_chunks[chunk_a_index])

    st.write("### Chunk B")
    st.code(all_chunks[chunk_b_index])

    st.subheader("Cosine Similarity")

    st.metric(
        "Similarity",
        f"{similarity:.4f}"
    )

else:
    st.info(
        "Lade mindestens zwei Chunks hoch, "
        "um die Embeddings zu vergleichen."
    )

# --------------------------------------------------
# 8. Manueller Retriever
# --------------------------------------------------
st.header("Manual Retriever", divider="grey")

if all_chunks:
    user_question = st.text_input(
        "Was möchtest du wissen?:"
    )

    if user_question:
        # --------------------------------------------------
        # Generate embedding for the question
        # --------------------------------------------------
        query_vector = embeddings.embed_query(
            user_question
        )

        # --------------------------------------------------
        # Calculate similarity against all chunks
        # --------------------------------------------------
        results = []

        for index, vector in enumerate(all_vectors):
            similarity = cosine_similarity(
                query_vector,
                vector
            )
            results.append({
                "index": index,
                "similarity": similarity
            })

        # --------------------------------------------------
        # Sort results by similarity
        # --------------------------------------------------
        results.sort(
            key=lambda result: result["similarity"],
            reverse=True
        )

        # --------------------------------------------------
        # Select Top K results
        # --------------------------------------------------
        top_k = 5
        top_results = results[:top_k]

        # --------------------------------------------------
        # Display results
        # --------------------------------------------------
        st.subheader(
            f"Top {top_k} relevant chunks"
        )

        for rank, result in enumerate(top_results, start=1):
            index = result["index"]
            similarity = result["similarity"]
            metadata = all_metadata[index]
            st.markdown(
                f"### {rank}. "
                f"{metadata['source']} | "
                f"Chunk {metadata['chunk_number']}"
            )
            st.write(
                f"Similarity: {similarity:.4f}"
            )
            st.code(
                all_chunks[index]
            )

else:
    st.info(
        "Lade zuerst mindestens ein Dokument hoch."
    )

# --------------------------------------------------
# 9. Qdrant DB erstellen (docker-compose.yml)
# --------------------------------------------------
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

qdrant_client = QdrantClient(
    host="localhost",
    port=6333
)
QDRANT_COLLECTION = "rag_documents"

# --------------------------------------------------
# 9. Qdrant Collection erstellen und schreiben
# --------------------------------------------------
if not qdrant_client.collection_exists(QDRANT_COLLECTION):
    qdrant_client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(
            size=1536, # Vector Dimensions - Siehe Chunks und Embeddings anzeigen (Dimensions: 1536)
            distance=Distance.COSINE # vergleiche die Vectoren anhand der Cosine Distance/Similarity
        )
    )
    # st.write(qdrant_client.get_collections())

st.header("Qdrant Database", divider="grey")

st.write(
    f"Collection: `{QDRANT_COLLECTION}`"
)

st.write(
    f"Chunks: {len(all_chunks)} | "
    f"Vectors: {len(all_vectors)} | "
    f"Metadata: {len(all_metadata)}"
)

if all_vectors and all_metadata:
    if st.button("Embeddings in Qdrant speichern"):
        points = []
        for index, vector in enumerate(all_vectors):
            point = PointStruct(
                id=index,
                vector=vector,
                payload=all_metadata[index]
            )
            points.append(point)

        qdrant_client.upsert(
            collection_name=QDRANT_COLLECTION,
            points=points
        )

        st.success(
            f"{len(points)} Points erfolgreich in Qdrant gespeichert."
        )

# --------------------------------------------------
# 9. Datensätze aus Qdrant anzeigen
# --------------------------------------------------
# points, next_page = qdrant_client.scroll(
#     collection_name=QDRANT_COLLECTION,
#     limit=100,
#     with_vectors=False
# )
# st.write(points)

points, next_page = qdrant_client.scroll(
    collection_name=QDRANT_COLLECTION,
    limit=1,
    with_vectors=True
)
st.write(points[0])

# --------------------------------------------------
# 9. Qdrant Retriever
# --------------------------------------------------
st.header("Qdrant Retriever", divider="grey")
if all_chunks:
    user_question_qdrant = st.text_input(
        "Was möchtest du wissen? (Qdrant):"
    )

    if user_question_qdrant:
        # Frage in einen Embedding-Vektor umwandeln
        query_vector = embeddings.embed_query(
            user_question_qdrant
        )

        # Ähnliche Vektoren in Qdrant suchen
        search_result = qdrant_client.query_points(
            collection_name=QDRANT_COLLECTION,
            query=query_vector,
            limit=5,
            with_payload=True
        )
        st.subheader("Top 5 relevante Chunks aus Qdrant")

        for rank, result in enumerate(
            search_result.points,
            start=1
        ):

            st.markdown(
                f"### {rank}. "
                f"{result.payload['source']} | "
                f"Chunk {result.payload['chunk_number']}"
            )

            st.write(
                f"Similarity: {result.score:.4f}"
            )

            st.write(
                f"Point ID: {result.id}"
            )

            st.code(
                result.payload["text"]
            )
# --------------------------------------------------
# 10. RAG Pipeline
# --------------------------------------------------
st.header("RAG Pipeline", divider="grey")

# --------------------------------------------------
# 10.1 Retrieval
# --------------------------------------------------
st.subheader("10.1 Retrieval")

rag_question = st.text_input(
    "Frage für die RAG Pipeline:"
)

if rag_question:
    # Frage in einen Embedding-Vektor umwandeln
    rag_query_vector = embeddings.embed_query(
        rag_question
    )

    # Ähnliche Points aus Qdrant holen
    rag_search_result = qdrant_client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=rag_query_vector,
        limit=5,
        with_payload=True
    )

    st.write(
        f"Gefundene Chunks: "
        f"{len(rag_search_result.points)}"
    )

    for rank, result in enumerate(
        rag_search_result.points,
        start=1
    ):

        st.markdown(
            f"**{rank}. "
            f"{result.payload['source']} | "
            f"Chunk {result.payload['chunk_number']}**"
        )

        st.write(
            f"Similarity: {result.score:.4f} | "
            f"Point ID: {result.id}"
        )

# --------------------------------------------------
# 10.2 Context Builder
# --------------------------------------------------
    st.subheader("10.2 Context Builder")

    context = "\n\n".join(
        result.payload["text"]
        for result in rag_search_result.points
    )

    st.write("Context für das LLM:")
    st.code(context)

# --------------------------------------------------
# 10.3 Prompt
# --------------------------------------------------
st.subheader("10.3 Prompt")

system_prompt = (
    "Du bist ein hilfreicher Assistent, der Fragen "
    "mithilfe des bereitgestellten Kontexts beantwortet.\n\n"
    "Richtlinien:\n"
    "1. Gib vollständige und gut verständliche Antworten auf Grundlage des folgenden Kontexts.\n"
    "2. Berücksichtige relevante Details, Zahlen und Erklärungen.\n"
    "3. Verwende ausschließlich Informationen aus dem bereitgestellten Kontext.\n"
    "4. Verwende kein Wissen außerhalb des bereitgestellten Kontexts.\n"
    "5. Wenn die benötigte Information nicht im Kontext enthalten ist, "
    "teile dies höflich mit.\n\n"
    "Kontext:\n"
    f"{context}"
)

user_prompt = rag_question
st.write("System Prompt:")

st.code(system_prompt)
st.write("User Prompt:")

st.code(user_prompt)

# --------------------------------------------------
# 10.4 LLM
# --------------------------------------------------
st.subheader("10.4 LLM")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    max_tokens=1000,
    openai_api_key=OPENAI_API_KEY
)

if st.button("Frage an LLM senden"):
    response = llm.invoke(
        [
            (
                "system",
                system_prompt
            ),
            (
                "human",
                user_prompt
            )
        ]
    )
    st.write("Antwort des LLM:")
    st.write(response.content)
