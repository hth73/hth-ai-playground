# --------------------------------------------------
# Import Python Modules
# --------------------------------------------------
import streamlit as st

from ui.chatbot_tab import show_chatbot_tab
from ui.debug_tab import show_debug_tab

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Local RAG Chatbot",
    page_icon="🤖",
    layout="wide",
)

# --------------------------------------------------
# Application Header
# --------------------------------------------------
st.title("🤖 Local RAG Chatbot")

st.caption(
    "A fully local Retrieval-Augmented Generation learning project."
)

# --------------------------------------------------
# Application Tabs
# --------------------------------------------------
chatbot_tab, debug_tab = st.tabs(
    ["💬 Chatbot", "🔍 Debug Chatbot"]
)

# --------------------------------------------------
# Render Tabs
# --------------------------------------------------
with chatbot_tab:
    show_chatbot_tab()

with debug_tab:
    show_debug_tab()
