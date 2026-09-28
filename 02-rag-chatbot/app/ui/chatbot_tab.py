import streamlit as st

def show_chatbot_tab():

    # --------------------------------------------------
    # Document Upload
    # --------------------------------------------------
    st.header("Documents")

    uploaded_files = st.file_uploader(
        "Upload documents",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        st.success(
            f"{len(uploaded_files)} document(s) selected."
        )

    st.button(
        "Index Documents",
        disabled=not uploaded_files,
    )

    st.divider()

    # --------------------------------------------------
    # Chat Interface
    # --------------------------------------------------
    st.header("Chat")

    st.info(
        "The RAG engine is not connected yet."
    )

    # Placeholder for future chat messages
    st.chat_message("assistant").write(
        "Hello! I am your local RAG assistant. "
        "Once the backend is connected, "
        "you can ask questions about your documents."
    )

    # Question input
    st.chat_input(
        "Ask a question about your documents...",
        disabled=True,
    )
