import streamlit as st

def show_debug_tab():

    st.header("RAG Pipeline Debugger")

    st.info(
        "The RAG pipeline is not connected yet."
    )

    # --------------------------------------------------
    # Processing Stages
    # --------------------------------------------------
    st.subheader("1. User Question")

    st.text_area(
        "Question",
        placeholder="The user's question will appear here.",
        disabled=True,
    )

    st.subheader("2. Retrieval")

    st.caption(
        "Retrieved chunks and similarity scores."
    )

    st.dataframe(
        {
            "Chunk": [],
            "Source": [],
            "Similarity Score": [],
        },
        width="stretch",
    )

    st.subheader("3. Context Builder")

    st.text_area(
        "Retrieved Context",
        placeholder="The assembled context will appear here.",
        disabled=True,
    )

    st.subheader("4. Prompt Builder")

    st.text_area(
        "Final Prompt",
        placeholder="The prompt sent to Ollama will appear here.",
        disabled=True,
    )

    st.subheader("5. LLM Generation")

    st.text_area(
        "Generated Answer",
        placeholder="The generated answer will appear here.",
        disabled=True,
    )
