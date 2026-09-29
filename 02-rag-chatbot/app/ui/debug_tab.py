
import json

import streamlit as st

from rag.m07_llm import build_messages
from rag.m04_vector_store import (
    get_qdrant_client,
    QDRANT_COLLECTION,
)


def show_debug_tab():

    st.header("RAG Pipeline Debugger")

    # --------------------------------------------------
    # 1. Document Indexing
    # --------------------------------------------------
    st.header("Document Indexing")

    # Indexierungsinformationen aus dem Session State abrufen.
    indexing_debug = st.session_state.get("indexing_debug")

    if not indexing_debug:
        st.info(
            "Noch keine Dokumente indexiert. "
            "Lade zuerst im Chatbot-Tab Dokumente hoch "
            "und starte die Indexierung."
        )

    else:

        documents = indexing_debug["documents"]

        # --------------------------------------------------
        # 1.1 Document Loader
        # --------------------------------------------------
        st.subheader("1. Document Loader")

        st.write(
            f"**Anzahl verarbeiteter Dokumente:** {len(documents)}"
        )

        for document in documents:

            filename = document["filename"]
            file_type = document["file_type"]
            character_count = document["character_count"]
            extracted_text = document["extracted_text"]

            with st.expander(f"Document: {filename}"):

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "File Type",
                        file_type.upper(),
                    )

                with col2:
                    st.metric(
                        "Extracted Characters",
                        character_count,
                    )

                st.markdown("**Extracted Text**")

                st.text_area(
                    "Document Content",
                    value=extracted_text,
                    height=300,
                    key=f"debug_document_{filename}",
                    disabled=True,
                )

        # --------------------------------------------------
        # 1.2 Text Splitter
        # --------------------------------------------------
        st.subheader("2. Text Splitter")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Chunk Size",
                indexing_debug["chunk_size"],
            )

        with col2:
            st.metric(
                "Chunk Overlap",
                indexing_debug["chunk_overlap"],
            )

        with col3:
            st.metric(
                "Total Chunks",
                sum(
                    document["chunk_count"]
                    for document in documents
                ),
            )

        st.markdown("**Generated Chunks**")

        for document in documents:

            filename = document["filename"]

            st.markdown(f"**Document: {filename}**")

            for chunk in document["chunks"]:

                chunk_id = chunk["chunk_id"]
                chunk_number = chunk["chunk_number"]
                chunk_text = chunk["text"]

                with st.expander(
                    f"Chunk ID: {chunk_id} | "
                    f"Chunk Number: {chunk_number}"
                ):

                    st.text_area(
                        "Chunk Text",
                        value=chunk_text,
                        height=200,
                        key=f"debug_index_chunk_{chunk_id}",
                        disabled=True,
                    )

        # --------------------------------------------------
        # 1.3 Embeddings
        # --------------------------------------------------
        st.subheader("3. Embeddings")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Embedding Model",
                indexing_debug["embedding_model"],
            )

        with col2:
            st.metric(
                "Vector Dimension",
                indexing_debug["vector_dimension"],
            )

        with col3:
            st.metric(
                "Generated Vectors",
                indexing_debug["stored_points"],
            )

        st.caption(
            "Für jeden gespeicherten Chunk wurde ein Embedding "
            "erzeugt. Die Vektordimension gibt die Anzahl der "
            "Werte pro Embedding an."
        )

        # --------------------------------------------------
        # 1.4 Embedding Explorer
        # --------------------------------------------------
        st.subheader("4. Embedding Explorer")

        st.caption(
            "Wähle einen Chunk aus, um den tatsächlich in Qdrant "
            "gespeicherten Embedding-Vektor anzuzeigen."
        )

        # Alle indexierten Chunks für die Auswahl sammeln.
        all_chunks = []

        for document in documents:
            for chunk in document["chunks"]:
                all_chunks.append(
                    {
                        "id": chunk["chunk_id"],
                        "source": document["filename"],
                        "chunk_number": chunk["chunk_number"],
                        "text": chunk["text"],
                    }
                )

        if all_chunks:

            chunk_options = {
                (
                    f"Chunk ID {chunk['id']} | "
                    f"{chunk['source']} | "
                    f"Chunk {chunk['chunk_number']}"
                ): chunk["id"]
                for chunk in all_chunks
            }

            selected_chunk_label = st.selectbox(
                "Select Chunk",
                options=list(chunk_options.keys()),
                key="embedding_explorer_selection",
            )

            selected_chunk_id = chunk_options[selected_chunk_label]

            # Qdrant-Verbindung herstellen.
            client = get_qdrant_client()

            # Den ausgewählten Point inklusive Vektor abrufen.
            points = client.retrieve(
                collection_name=QDRANT_COLLECTION,
                ids=[selected_chunk_id],
                with_payload=True,
                with_vectors=True,
            )

            if points:

                point = points[0]
                vector = point.vector

                st.markdown(
                    f"**Point ID:** {point.id}"
                )

                st.markdown(
                    f"**Vektordimension:** {len(vector)}"
                )

                # Vollständigen Vektor anzeigen.
                with st.expander(
                    "Show complete embedding vector",
                    expanded=False,
                ):

                    st.json(vector)

                    # Optional: Vektor als JSON kopieren.
                    vector_json = json.dumps(
                        vector,
                        indent=2,
                    )

                    st.text_area(
                        "Embedding JSON",
                        value=vector_json,
                        height=250,
                        key="embedding_vector_json",
                        disabled=True,
                    )

            else:
                st.warning(
                    "Der ausgewählte Point wurde in Qdrant "
                    "nicht gefunden."
                )

        # --------------------------------------------------
        # 1.5 Qdrant Vector Store
        # --------------------------------------------------
        st.subheader("5. Qdrant Vector Store")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Collection",
                indexing_debug["collection_name"],
            )

        with col2:
            st.metric(
                "Stored Points",
                indexing_debug["stored_points"],
            )

        st.caption(
            "Jeder Point enthält den Vektor und die zugehörigen "
            "Metadaten des Chunks."
        )

        # --------------------------------------------------
        # 1.6 Database Explorer
        # --------------------------------------------------
        st.subheader("6. Database Explorer")

        st.caption(
            "Hier kannst du die tatsächlich gespeicherten "
            "Qdrant-Datensätze untersuchen."
        )

        if all_chunks:

            selected_point_label = st.selectbox(
                "Select Database Entry",
                options=list(chunk_options.keys()),
                key="database_explorer_selection",
            )

            selected_point_id = chunk_options[selected_point_label]

            # Den ausgewählten Datensatz inklusive Payload
            # und Vektor aus Qdrant lesen.
            database_points = client.retrieve(
                collection_name=QDRANT_COLLECTION,
                ids=[selected_point_id],
                with_payload=True,
                with_vectors=True,
            )

            if database_points:

                point = database_points[0]

                st.markdown(
                    f"**Point ID:** {point.id}"
                )

                # Payload und Metadaten anzeigen.
                st.markdown("**Payload / Metadata**")

                payload_json = json.dumps(
                    point.payload,
                    indent=2,
                    ensure_ascii=False,
                )

                st.code(
                    payload_json,
                    language="json",
                )

                # Gespeicherten Vektor anzeigen.
                with st.expander(
                    "Show stored vector",
                    expanded=False,
                ):

                    st.json(point.vector)

            else:
                st.warning(
                    "Der ausgewählte Datenbankeintrag "
                    "wurde nicht gefunden."
                )

    # --------------------------------------------------
    # 2. RAG Query
    # --------------------------------------------------
    st.divider()

    st.header("RAG Query")

    # Letztes Pipeline-Ergebnis aus dem Chatbot-Tab abrufen.
    result = st.session_state.get("last_result")

    if not result:
        st.info(
            "Noch keine RAG-Abfrage vorhanden. "
            "Stelle zuerst im Chatbot-Tab eine Frage."
        )
        return

    # --------------------------------------------------
    # 2.1 User Question
    # --------------------------------------------------
    st.subheader("7. User Question")

    st.text_area(
        "Question",
        value=result["question"],
        height=100,
        disabled=True,
    )

    # --------------------------------------------------
    # 2.2 Retrieval
    # --------------------------------------------------
    st.subheader("8. Retrieval")

    retrieved_chunks = result["retrieved_chunks"]

    st.write(
        f"**Anzahl gefundener Chunks:** {len(retrieved_chunks)}"
    )

    # Übersicht der gefundenen Chunks.
    chunk_data = []

    for chunk in retrieved_chunks:

        metadata = chunk.payload

        chunk_data.append(
            {
                "Chunk ID": metadata.get("chunk_id"),
                "Source": metadata.get("source"),
                "Chunk Number": metadata.get("chunk_number"),
                "Similarity Score": round(chunk.score, 4),
            }
        )

    st.dataframe(
        chunk_data,
        width="stretch",
        hide_index=True,
    )

    # Vollständigen Text jedes gefundenen Chunks anzeigen.
    st.markdown("**Retrieved Chunk Details**")

    for index, chunk in enumerate(retrieved_chunks, start=1):

        metadata = chunk.payload

        source = metadata.get("source", "Unbekannte Quelle")
        chunk_number = metadata.get("chunk_number", "Unbekannt")
        text = metadata.get("text", "")

        with st.expander(
            f"Chunk {index}: {source} | "
            f"Chunk Number: {chunk_number}"
        ):

            st.caption(
                f"Similarity Score: {chunk.score:.4f}"
            )

            st.text_area(
                "Chunk Text",
                value=text,
                height=200,
                key=f"debug_retrieved_chunk_{index}",
                disabled=True,
            )

    # --------------------------------------------------
    # 2.3 Context Builder
    # --------------------------------------------------
    st.subheader("9. Context Builder")

    st.caption(
        "Der folgende Kontext wurde aus den gefundenen "
        "Chunks zusammengesetzt."
    )

    st.text_area(
        "Retrieved Context",
        value=result["context"],
        height=350,
        disabled=True,
    )

    # --------------------------------------------------
    # 2.4 Prompt Builder
    # --------------------------------------------------
    st.subheader("10. Prompt Builder")

    # Dieselbe Funktion verwenden, die auch die
    # LLM-Anfrage vorbereitet.
    messages = build_messages(
        context=result["context"],
        question=result["question"],
    )

    for message in messages:

        role = message["role"]
        content = message["content"]

        st.markdown(f"**{role.capitalize()} Prompt**")

        st.text_area(
            f"{role.capitalize()} Message",
            value=content,
            height=250,
            key=f"debug_prompt_{role}",
            disabled=True,
        )

    # --------------------------------------------------
    # 2.5 LLM Generation
    # --------------------------------------------------
    st.subheader("11. LLM Generation")

    st.caption(
        "Antwort des lokalen Sprachmodells Qwen3."
    )

    st.markdown(result["answer"])
