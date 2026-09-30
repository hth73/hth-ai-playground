import json

import streamlit as st
from qdrant_client.models import FieldCondition, Filter, MatchValue

from rag.m01_document_loader import load_document
from rag.m02_text_splitter import (
    split_text_with_metadata,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)
from rag.m03_embeddings import EMBEDDING_MODEL
from rag.m04_vector_store import (
    get_qdrant_client,
    QDRANT_COLLECTION,
)
from rag.m07_llm import build_messages
from rag.m10_document_store import initialize_database, list_documents


def _load_persisted_indexing_data():
    """Reconstruct chunk previews from stored originals and read Qdrant points."""
    initialize_database()
    documents = [
        document
        for document in list_documents()
        if document.get("status") == "indexed"
    ]

    client = get_qdrant_client()
    try:
        collection_info = client.get_collection(QDRANT_COLLECTION)
    except Exception:
        return documents, [], None

    points = []
    offset = None
    while True:
        batch, offset = client.scroll(
            collection_name=QDRANT_COLLECTION,
            scroll_filter=None,
            limit=256,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        points.extend(batch)
        if offset is None:
            break

    points_by_document = {}
    for point in points:
        payload = point.payload or {}
        document_id = payload.get("document_id")
        if document_id:
            points_by_document.setdefault(document_id, []).append(point)

    reconstructed = []
    for document in documents:
        try:
            from pathlib import Path

            file_bytes = Path(document["stored_path"]).read_bytes()
            extracted_text = load_document(document["filename"], file_bytes)
            chunk_data = split_text_with_metadata(
                text=extracted_text,
                file_name=document["filename"],
            )
            qdrant_points = points_by_document.get(
                document["document_id"], []
            )
            qdrant_points.sort(
                key=lambda point: (point.payload or {}).get("chunk_number", 0)
            )

            chunks = []
            for index, chunk in enumerate(chunk_data):
                point = (
                    qdrant_points[index]
                    if index < len(qdrant_points)
                    else None
                )
                chunks.append(
                    {
                        **chunk,
                        "chunk_id": point.id if point else None,
                        "point": point,
                    }
                )

            reconstructed.append(
                {
                    **document,
                    "extracted_text": extracted_text,
                    "character_count": len(extracted_text),
                    "chunks": chunks,
                    "chunk_count": len(chunks),
                }
            )
        except Exception as error:
            reconstructed.append(
                {
                    **document,
                    "extracted_text": "",
                    "character_count": 0,
                    "chunks": [],
                    "debug_error": str(error),
                }
            )

    return reconstructed, points, collection_info


def _render_document_indexing_debug():
    st.header("Document Indexing")
    st.caption(
        "Diese Ansicht wird aus den dauerhaft gespeicherten Originaldateien "
        "und den Qdrant-Datensätzen aufgebaut. Sie bleibt daher auch nach "
        "einem Streamlit-Neustart verfügbar."
    )

    try:
        documents, points, collection_info = _load_persisted_indexing_data()
    except Exception as error:
        st.error(f"Could not load persisted indexing data: {error}")
        return

    if not documents:
        st.info("Noch keine indexierten Dokumente vorhanden.")
        return

    all_chunks = [
        chunk
        for document in documents
        for chunk in document.get("chunks", [])
    ]

    st.subheader("1. Document Loader")
    st.write(f"**Anzahl indexierter Dokumente:** {len(documents)}")

    for document in documents:
        with st.expander(f"Document: {document['filename']}"):
            if document.get("debug_error"):
                st.error(document["debug_error"])
                continue
            col1, col2 = st.columns(2)
            col1.metric("File Type", document["file_type"].upper())
            col2.metric(
                "Extracted Characters",
                document["character_count"],
            )
            st.text_area(
                "Document Content",
                value=document["extracted_text"],
                height=300,
                key=f"persisted_debug_document_{document['document_id']}",
                disabled=True,
            )

    st.subheader("2. Text Splitter")
    col1, col2, col3 = st.columns(3)
    col1.metric("Chunk Size", CHUNK_SIZE)
    col2.metric("Chunk Overlap", CHUNK_OVERLAP)
    col3.metric("Total Chunks", len(all_chunks))

    for document in documents:
        st.markdown(f"**Document: {document['filename']}**")
        for chunk in document.get("chunks", []):
            with st.expander(
                f"Chunk {chunk.get('chunk_number', '?')} | "
                f"{document['filename']}"
            ):
                st.text_area(
                    "Chunk Text",
                    value=chunk["text"],
                    height=200,
                    key=f"persisted_debug_chunk_{chunk.get('chunk_id') or chunk.get('chunk_number')}",
                    disabled=True,
                )

    st.subheader("3. Embeddings")
    st.metric("Embedding Model", EMBEDDING_MODEL)
    st.metric("Stored Qdrant Points", len(points))
    st.caption(
        "Die folgenden Explorer lesen die gespeicherten Vektoren direkt "
        "aus Qdrant. Die Vektoren werden nicht bei jedem Öffnen neu erzeugt."
    )

    chunks_with_points = [
        (document, chunk)
        for document in documents
        for chunk in document.get("chunks", [])
        if chunk.get("chunk_id") is not None
    ]

    st.subheader("4. Embedding Explorer")
    if chunks_with_points:
        labels = [
            (
                f"{document['filename']} | "
                f"Chunk {chunk.get('chunk_number', '?')} | "
                f"Point {chunk['chunk_id']}"
            )
            for document, chunk in chunks_with_points
        ]
        selected_index = st.selectbox(
            "Select Chunk",
            options=range(len(labels)),
            format_func=lambda index: labels[index],
            key="persisted_embedding_selection",
        )
        selected_document, selected_chunk = chunks_with_points[selected_index]
        client = get_qdrant_client()
        selected_points = client.retrieve(
            collection_name=QDRANT_COLLECTION,
            ids=[selected_chunk["chunk_id"]],
            with_payload=True,
            with_vectors=True,
        )
        if selected_points:
            point = selected_points[0]
            vector = point.vector
            st.write(f"**Point ID:** {point.id}")
            st.write(f"**Vector Dimension:** {len(vector)}")
            with st.expander("Show complete embedding vector"):
                st.json(vector)
                st.text_area(
                    "Embedding JSON",
                    value=json.dumps(vector, indent=2),
                    height=250,
                    key="persisted_embedding_json",
                    disabled=True,
                )
        else:
            st.warning("Der ausgewählte Point wurde in Qdrant nicht gefunden.")
    else:
        st.info("Keine zugeordneten Qdrant-Punkte gefunden.")

    st.subheader("5. Qdrant Vector Store")
    if collection_info is not None:
        st.metric("Collection", QDRANT_COLLECTION)
        st.metric("Stored Points", collection_info.points_count or 0)
        st.caption(
            "Qdrant ist die persistente Quelle für die gespeicherten "
            "Embeddings und Chunk-Metadaten."
        )
    else:
        st.warning("Die Qdrant-Collection ist nicht verfügbar.")

    st.subheader("6. Database Explorer")
    if chunks_with_points:
        labels = [
            (
                f"{document['filename']} | "
                f"Chunk {chunk.get('chunk_number', '?')} | "
                f"Point {chunk['chunk_id']}"
            )
            for document, chunk in chunks_with_points
        ]
        selected_index = st.selectbox(
            "Select Database Entry",
            options=range(len(labels)),
            format_func=lambda index: labels[index],
            key="persisted_database_selection",
        )
        _, selected_chunk = chunks_with_points[selected_index]
        database_points = get_qdrant_client().retrieve(
            collection_name=QDRANT_COLLECTION,
            ids=[selected_chunk["chunk_id"]],
            with_payload=True,
            with_vectors=True,
        )
        if database_points:
            point = database_points[0]
            st.write(f"**Point ID:** {point.id}")
            st.markdown("**Payload / Metadata**")
            st.code(
                json.dumps(point.payload, indent=2, ensure_ascii=False),
                language="json",
            )
            with st.expander("Show stored vector"):
                st.json(point.vector)
        else:
            st.warning("Der ausgewählte Datenbankeintrag wurde nicht gefunden.")


def _render_rag_query_debug():
    st.divider()
    st.header("RAG Query")
    result = st.session_state.get("last_result")

    if not result:
        st.info(
            "Noch keine RAG-Abfrage vorhanden. Stelle zuerst im Chatbot-Tab "
            "eine Frage."
        )
        return

    st.subheader("7. User Question")
    st.text_area(
        "Question",
        value=result["question"],
        height=100,
        disabled=True,
        key="debug_rag_question",
    )

    st.subheader("8. Retrieval")
    retrieved_chunks = result["retrieved_chunks"]
    st.write(f"**Anzahl gefundener Chunks:** {len(retrieved_chunks)}")

    chunk_data = []
    for chunk in retrieved_chunks:
        metadata = chunk.payload or {}
        chunk_data.append(
            {
                "Chunk ID": metadata.get("chunk_id"),
                "Source": metadata.get("source"),
                "Chunk Number": metadata.get("chunk_number"),
                "Similarity Score": round(float(chunk.score), 4),
            }
        )

    if chunk_data:
        st.dataframe(chunk_data, width="stretch", hide_index=True)
    else:
        st.info("Das Retrieval hat keine Chunks zurückgegeben.")

    st.markdown("**Retrieved Chunk Details**")
    for index, chunk in enumerate(retrieved_chunks, start=1):
        metadata = chunk.payload or {}
        source = metadata.get("source", "Unbekannte Quelle")
        chunk_number = metadata.get("chunk_number", "Unbekannt")
        with st.expander(
            f"Chunk {index}: {source} | Chunk Number: {chunk_number}"
        ):
            st.caption(f"Similarity Score: {float(chunk.score):.4f}")
            st.text_area(
                "Chunk Text",
                value=metadata.get("text", ""),
                height=200,
                key=f"debug_retrieved_chunk_{index}",
                disabled=True,
            )

    st.subheader("9. Context Builder")
    st.text_area(
        "Retrieved Context",
        value=result["context"],
        height=350,
        disabled=True,
        key="debug_retrieved_context",
    )

    st.subheader("10. Prompt Builder")
    messages = build_messages(
        context=result["context"],
        question=result["question"],
    )
    for index, message in enumerate(messages):
        role = message["role"]
        st.markdown(f"**{role.capitalize()} Prompt**")
        st.text_area(
            f"{role.capitalize()} Message",
            value=message["content"],
            height=250,
            key=f"debug_prompt_{role}_{index}",
            disabled=True,
        )

    st.subheader("11. LLM Generation")
    st.caption("Antwort des lokalen Sprachmodells.")
    st.markdown(result["answer"])


def show_debug_tab():
    st.header("RAG Pipeline Debugger")
    indexing_tab, query_tab = st.tabs(
        ["📚 Document Indexing & Database", "🔎 RAG Query"]
    )
    with indexing_tab:
        _render_document_indexing_debug()
    with query_tab:
        _render_rag_query_debug()
