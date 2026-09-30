#!/usr/bin/env bash
set -Eeuo pipefail

# Start the local RAG chatbot from any working directory.
PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

VENV_DIR="$PROJECT_DIR/.venv"
PYTHON="${PYTHON:-python3}"

echo "==> Project: $PROJECT_DIR"

# Check required commands.
for command in docker "$PYTHON"; do
    if ! command -v "$command" >/dev/null 2>&1; then
        echo "ERROR: Required command not found: $command" >&2
        exit 1
    fi
done

# Create the virtual environment if it does not exist.
if [[ ! -x "$VENV_DIR/bin/python" ]]; then
    echo "==> Creating Python virtual environment..."
    "$PYTHON" -m venv "$VENV_DIR"
fi

# Install/update project dependencies.
echo "==> Installing project dependencies..."
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r requirements.txt

# Start the infrastructure services. Existing images and model volumes are reused.
echo "==> Starting Qdrant..."
docker compose up -d qdrant

if [[ -n "$(docker compose ps --status=running -q qdrant)" ]]; then
    echo "Qdrant container is running"
else
    echo "Qdrant container is not running"
    docker compose up -d qdrant
    sleep 5
    echo "Qdrant container is starting"
fi

echo "==> Starting Streamlit..."
exec "$VENV_DIR/bin/streamlit" run "$PROJECT_DIR/rag-chatbot-lab.py"
