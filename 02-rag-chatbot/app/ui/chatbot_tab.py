
import streamlit as st

from rag.m08_rag_pipeline import run_rag_pipeline
from rag.m09_document_indexer import index_documents


def show_chatbot_tab():

    # --------------------------------------------------
    # Initialize Session State
    # --------------------------------------------------
    if "indexed" not in st.session_state:
        st.session_state.indexed = False

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    if "indexing_debug" not in st.session_state:
        st.session_state.indexing_debug = None

    # --------------------------------------------------
    # Document Management
    # --------------------------------------------------
    with st.expander(
        "📁 Manage Documents",
        expanded=not st.session_state.indexed,
    ):

        uploaded_files = st.file_uploader(
            "Upload documents",
            type=["pdf", "txt", "md"],
            accept_multiple_files=True,
        )

        if st.button(
            "Index Documents",
            disabled=not uploaded_files,
            width="stretch",
        ):

            files = [
                (file.name, file.getvalue())
                for file in uploaded_files
            ]

            with st.spinner("Processing and indexing documents..."):

                try:
                    result = index_documents(files)

                    # Update the application state.
                    st.session_state.indexed = True
                    st.session_state.chat_history = []
                    st.session_state.last_result = None

                    # Keep indexing details available for the Debug tab.
                    st.session_state.indexing_debug = result["debug"]

                    st.success(
                        f"Successfully indexed "
                        f"{result['document_count']} document(s) "
                        f"and {result['chunk_count']} chunk(s)."
                    )

                    # Refresh the UI to show the updated state.
                    st.rerun()

                except Exception as error:
                    st.error(f"Indexing failed: {error}")

    # --------------------------------------------------
    # Indexing Status
    # --------------------------------------------------
    if st.session_state.indexed:
        st.caption("🟢 Documents are ready for questions.")
    else:
        st.info("Please upload and index documents to start chatting.")

    st.divider()

    # --------------------------------------------------
    # Chat Interface
    # --------------------------------------------------

    # Display previous messages.
    for message in st.session_state.chat_history:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept a new question.
    question = st.chat_input(
        "Ask a question about your documents...",
        disabled=not st.session_state.indexed,
    )

    if question:

        # Display and store the user's question.
        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": question,
            }
        )

        with st.chat_message("user"):
            st.markdown(question)

        # Generate the answer.
        with st.chat_message("assistant"):

            with st.spinner("Searching documents and generating answer..."):

                try:
                    result = run_rag_pipeline(question)

                    answer = result["answer"]

                    st.markdown(answer)

                    # Display the sources used to generate the answer.
                    with st.expander("📚 Sources"):

                        for chunk in result["retrieved_chunks"]:

                            metadata = chunk.payload

                            source = metadata.get(
                                "source",
                                "Unknown source",
                            )

                            chunk_number = metadata.get(
                                "chunk_number",
                                "Unknown",
                            )

                            score = chunk.score

                            st.markdown(
                                f"**Document:** {source}  \n"
                                f"**Chunk:** {chunk_number}  \n"
                                f"**Similarity Score:** {score:.4f}"
                            )

                            st.divider()

                    # Store the complete result for the Debug tab.
                    st.session_state.last_result = result

                    # Store the assistant response.
                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": answer,
                        }
                    )

                except Exception as error:
                    st.error(f"An error occurred: {error}")
