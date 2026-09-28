#!/usr/bin/env bash
set -e

if [[ -n "$(docker compose ps --status=running -q qdrant)" ]]; then
    echo "Qdrant container is running"
else
    echo "Qdrant container is not running"
    docker compose up -d qdrant
    sleep 5
    echo "Qdrant container is starting"
fi

.venv/bin/streamlit run ~/repo-privat/github/hth-ai-playground/01-rag/rag-chatbot-lab.py
