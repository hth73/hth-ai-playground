# --------------------------------------------------
# Unit Tests: Document Indexer
# --------------------------------------------------
from pathlib import Path
from unittest.mock import Mock

import pytest

import rag.m11_indexer as indexer


@pytest.fixture
def document_record(tmp_path, monkeypatch):
    """Stellt ein gespeichertes Beispieldokument bereit."""
    stored_file = tmp_path / "example.txt"
    stored_file.write_text("Beispieltext für die Indexierung.", encoding="utf-8")

    record = {
        "document_id": "doc-123",
        "filename": "example.txt",
        "stored_path": str(stored_file),
        "status": "uploaded",
        "chunk_count": 0,
    }
    monkeypatch.setattr(indexer, "list_documents", lambda: [record])
    return record


@pytest.fixture
def mocked_pipeline(monkeypatch):
    client = Mock()
    calls = {}

    monkeypatch.setattr(indexer, "load_document", lambda name, content: "Dokumenttext")
    monkeypatch.setattr(
        indexer,
        "split_text_with_metadata",
        lambda text, file_name: [
            {"text": "Chunk A", "source": file_name},
            {"text": "Chunk B", "source": file_name},
        ],
    )
    monkeypatch.setattr(indexer, "embed_documents", lambda chunks: [[0.1], [0.2]])
    monkeypatch.setattr(indexer, "get_qdrant_client", lambda: client)
    monkeypatch.setattr(indexer, "create_collection", lambda client: None)

    def store_embeddings(**kwargs):
        calls["store"] = kwargs
        return len(kwargs["chunks"])

    monkeypatch.setattr(indexer, "store_embeddings", store_embeddings)
    monkeypatch.setattr(
        indexer, "mark_document_indexed",
        lambda document_id, chunk_count: calls.update(
            indexed=(document_id, chunk_count)
        ),
    )
    monkeypatch.setattr(
        indexer, "update_document_status",
        lambda **kwargs: calls.update(failed=kwargs),
    )
    calls["client"] = client
    return calls


def test_index_document_processes_and_stores_chunks(
    document_record, mocked_pipeline
):
    result = indexer.index_document("doc-123")

    assert result == 2
    assert mocked_pipeline["store"]["document_id"] == "doc-123"
    assert mocked_pipeline["store"]["chunks"] == ["Chunk A", "Chunk B"]
    assert mocked_pipeline["indexed"] == ("doc-123", 2)
    assert "failed" not in mocked_pipeline


def test_index_document_skips_already_indexed_document(
    document_record, mocked_pipeline
):
    document_record["status"] = "indexed"
    document_record["chunk_count"] = 7

    result = indexer.index_document("doc-123")

    assert result == 7
    assert "store" not in mocked_pipeline


def test_index_document_rejects_unknown_document(monkeypatch):
    monkeypatch.setattr(indexer, "list_documents", lambda: [])

    with pytest.raises(ValueError, match="Document not found"):
        indexer.index_document("missing")


@pytest.mark.parametrize("document_id", ["", "   "])
def test_index_document_rejects_empty_id(document_id):
    with pytest.raises(ValueError, match="document_id darf nicht leer sein"):
        indexer.index_document(document_id)


def test_index_document_marks_failure_when_pipeline_raises(
    document_record, mocked_pipeline, monkeypatch
):
    def fail_embedding(chunks):
        raise RuntimeError("Ollama unavailable")

    monkeypatch.setattr(indexer, "embed_documents", fail_embedding)

    with pytest.raises(RuntimeError, match="Ollama unavailable"):
        indexer.index_document("doc-123")

    assert mocked_pipeline["failed"] == {
        "document_id": "doc-123",
        "status": "failed",
        "error_message": "Ollama unavailable",
    }


def test_index_document_rejects_mismatched_embedding_count(
    document_record, mocked_pipeline, monkeypatch
):
    monkeypatch.setattr(indexer, "embed_documents", lambda chunks: [[0.1]])

    with pytest.raises(ValueError, match="Chunks und Embeddings"):
        indexer.index_document("doc-123")

    assert mocked_pipeline["failed"]["status"] == "failed"
