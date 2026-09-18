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
VERSION = "1.0.0"

# --------------------------------------------------
# OpenAI API Key
# --------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
