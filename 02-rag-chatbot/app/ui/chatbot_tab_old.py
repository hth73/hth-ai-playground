import streamlit as st

from rag.m08_rag_pipeline import run_rag_pipeline
from rag.m10_document_store import (
    initialize_database,
    list_documents,
    save_document,
)
from rag.m11_indexer import index_document


def _get_document_state() -> tuple[list[dict], int, int]:
    """Return persisted documents and aggregate counts."""
    initialize_database()
    documents = list_documents()
    indexed_documents = [
        document
        for document in documents
        if document.get("status") == "indexed"
    ]
    total_chunks = sum(
        document.get("chunk_count", 0)
        for document in indexed_documents
    )
    return documents, len(indexed_documents), total_chunks


def _render_document_sidebar() -> None:
    """Render document upload and status in Streamlit's left sidebar."""
    documents, indexed_count, total_chunks = _get_document_state()

    with st.sidebar:
        st.header("📁 Documents")
        st.caption("Manage your local knowledge base.")

        uploaded_files = st.file_uploader(
            "Add documents",
            type=["pdf", "txt", "md"],
            accept_multiple_files=True,
            key="document_uploader",
            help="Supported formats: PDF, TXT, and Markdown.",
        )

        if st.button(
            "Upload and index",
            disabled=not uploaded_files,
            type="secondary",
            width="stretch",
            key="upload_and_index",
        ):
            successful_documents = 0
            successful_chunks = 0
            duplicate_files = []
            failed_files = []
            debug_documents = []
            latest_debug = None

            with st.spinner("Saving and indexing documents..."):
                for uploaded_file in uploaded_files:
                    try:
                        record = save_document(
                            file_content=uploaded_file.getvalue(),
                            filename=uploaded_file.name,
                        )
                    except ValueError as error:
                        if "Duplicate document" in str(error):
                            duplicate_files.append(uploaded_file.name)
                        else:
                            failed_files.append((uploaded_file.name, str(error)))
                        continue

                    try:
                        result = index_document(
                            record["document_id"],
                            include_debug=True,
                        )
                        successful_documents += 1
                        successful_chunks += result["chunk_count"]
                        latest_debug = result["debug"]
                        debug_documents.extend(
                            result["debug"]["documents"]
                        )
                    except Exception as error:
                        failed_files.append((uploaded_file.name, str(error)))

            if latest_debug is not None:
                latest_debug["documents"] = debug_documents
                st.session_state.indexing_debug = latest_debug

            if successful_documents:
                st.session_state.last_result = None
                st.success(
                    f"Indexed {successful_documents} document(s) "
                    f"and {successful_chunks} chunk(s)."
                )
            if duplicate_files:
                st.warning(
                    "Already stored (duplicate content): "
                    + ", ".join(duplicate_files)
                )
            for filename, error in failed_files:
                st.error(f"{filename}: {error}")

            st.rerun()

        st.divider()
        st.subheader("Knowledge base")

        documents, indexed_count, total_chunks = _get_document_state()
        st.metric("Indexed documents", indexed_count)
        st.metric("Indexed chunks", total_chunks)

        if documents:
            for document in documents:
                status = document["status"]
                icon = "🟢" if status == "indexed" else "🟠"
                with st.container(border=True):
                    st.markdown(f"**{document['filename']}**")
                    st.caption(
                        f"{icon} {status.capitalize()} · "
                        f"{document['chunk_count']} chunk(s)"
                    )
        else:
            st.info("No documents uploaded yet.")


def show_chatbot_tab():
    """Render the chat experience with document controls in the sidebar."""
    initialize_database()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "indexing_debug" not in st.session_state:
        st.session_state.indexing_debug = None

    _, indexed_count, total_chunks = _get_document_state()
    has_indexed_documents = indexed_count > 0

    _render_document_sidebar()

    # Main conversation header
    title_column, action_column = st.columns([5, 1])
    with title_column:
        st.subheader("💬 Chat")
        if has_indexed_documents:
            st.caption(
                f"🟢 Knowledge base ready · {indexed_count} document(s) · "
                f"{total_chunks} indexed chunk(s)"
            )
        else:
            st.caption("Upload and index documents from the sidebar to begin.")

    with action_column:
        # Keep the control enabled even for an empty conversation, so it
        # never appears disabled. Clicking it simply leaves an empty chat.
        st.write("")
        if st.button(
            "New chat",
            type="secondary",
            help="Clear the conversation. Your indexed documents are preserved.",
            width="stretch",
            key="new_chat",
        ):
            st.session_state.chat_history = []
            st.session_state.last_result = None
            st.rerun()

    st.divider()

    if not st.session_state.chat_history and has_indexed_documents:
        st.markdown(
            "Ask a question about your indexed documents. "
            "Retrieved source chunks are available below each answer."
        )
    elif not has_indexed_documents:
        st.info(
            "Your knowledge base is empty. Upload a PDF, TXT, or Markdown "
            "document using the left sidebar."
        )

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("sources"):
                with st.expander("📚 Sources"):
                    for source in message["sources"]:
                        st.markdown(
                            f"**Document:** {source['document']}  \n"
                            f"**Chunk:** {source['chunk']}  \n"
                            f"**Similarity:** {source['score']:.4f}"
                        )
                        st.divider()

    question = st.chat_input(
        "Ask a question about your documents...",
        disabled=not has_indexed_documents,
    )

    if question:
        st.session_state.chat_history.append(
            {"role": "user", "content": question}
        )
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching documents and generating an answer..."):
                try:
                    result = run_rag_pipeline(question)
                    answer = result["answer"]
                    sources = []

                    for chunk in result["retrieved_chunks"]:
                        metadata = chunk.payload or {}
                        sources.append(
                            {
                                "document": metadata.get(
                                    "source",
                                    "Unknown source",
                                ),
                                "chunk": metadata.get(
                                    "chunk_number",
                                    "Unknown",
                                ),
                                "score": float(chunk.score),
                            }
                        )

                    st.markdown(answer)
                    if sources:
                        with st.expander("📚 Sources"):
                            for source in sources:
                                st.markdown(
                                    f"**Document:** {source['document']}  \n"
                                    f"**Chunk:** {source['chunk']}  \n"
                                    f"**Similarity:** {source['score']:.4f}"
                                )
                                st.divider()

                    st.session_state.last_result = result
                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                        }
                    )
                except Exception as error:
                    st.error(f"An error occurred: {error}")
