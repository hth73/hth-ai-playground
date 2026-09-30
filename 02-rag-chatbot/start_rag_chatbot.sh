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
"$VENV_DIR/bin/python" -m pip install -e .

# Start the infrastructure services. Existing images and model volumes are reused.
echo "==> Starting Qdrant and Ollama..."
docker compose up -d qdrant ollama

# Wait briefly and verify that both containers are running.
for service in qdrant ollama; do
    running="$(docker compose ps --status=running -q "$service")"
    if [[ -z "$running" ]]; then
        echo "ERROR: Docker service '$service' is not running." >&2
        docker compose ps "$service"
        exit 1
    fi
    echo "    $service is running"
done

echo "==> Starting Streamlit..."
exec "$VENV_DIR/bin/streamlit" run "$PROJECT_DIR/app/streamlit_app.py"
