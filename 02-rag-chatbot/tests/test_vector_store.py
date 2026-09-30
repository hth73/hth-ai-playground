# --------------------------------------------------
# Tests: Qdrant Vector Store
# --------------------------------------------------
from unittest.mock import Mock
from uuid import UUID

import pytest
from qdrant_client.models import FieldCondition, Filter, MatchValue

from rag.m04_vector_store import (
    QDRANT_COLLECTION,
    delete_document_embeddings,
    store_embeddings,
)


@pytest.fixture
def qdrant_client():
    """Stellt einen gemockten Qdrant-Client bereit."""
    return Mock()


def test_store_embeddings_creates_unique_ids_and_document_payload(qdrant_client):
    chunks = ["Erster Chunk", "Zweiter Chunk"]
    vectors = [[0.1, 0.2], [0.3, 0.4]]
    metadata = [
        {"source": "beispiel.txt", "chunk_number": 0},
        {"source": "beispiel.txt", "chunk_number": 1},
    ]

    stored_count = store_embeddings(
        qdrant_client,
        chunks,
        vectors,
        metadata,
        document_id="doc-123",
    )

    assert stored_count == 2
    qdrant_client.upsert.assert_called_once()

    call = qdrant_client.upsert.call_args.kwargs
    assert call["collection_name"] == QDRANT_COLLECTION
    assert call["wait"] is True

    points = call["points"]
    assert len(points) == 2
    assert points[0].id != points[1].id

    # IDs müssen gültige UUIDs sein.
    UUID(points[0].id)
    UUID(points[1].id)

    assert points[0].payload["document_id"] == "doc-123"
    assert points[1].payload["document_id"] == "doc-123"
    assert points[0].payload["text"] == chunks[0]
    assert points[1].payload["text"] == chunks[1]


def test_store_embeddings_keeps_documents_separate(qdrant_client):
    common = {
        "chunks": ["Ein Chunk"],
        "vectors": [[0.1, 0.2]],
        "metadata": [{"source": "same.txt"}],
    }

    store_embeddings(qdrant_client, **common, document_id="doc-A")
    store_embeddings(qdrant_client, **common, document_id="doc-B")

    first_point = qdrant_client.upsert.call_args_list[0].kwargs["points"][0]
    second_point = qdrant_client.upsert.call_args_list[1].kwargs["points"][0]

    assert first_point.id != second_point.id
    assert first_point.payload["document_id"] == "doc-A"
    assert second_point.payload["document_id"] == "doc-B"


def test_store_embeddings_rejects_mismatched_lengths(qdrant_client):
    with pytest.raises(ValueError, match="stimmt nicht überein"):
        store_embeddings(
            qdrant_client,
            chunks=["Chunk"],
            vectors=[],
            metadata=[{}],
            document_id="doc-123",
        )

    qdrant_client.upsert.assert_not_called()


@pytest.mark.parametrize("document_id", ["", "   "])
def test_store_embeddings_rejects_empty_document_id(qdrant_client, document_id):
    with pytest.raises(ValueError, match="document_id darf nicht leer sein"):
        store_embeddings(
            qdrant_client,
            chunks=[],
            vectors=[],
            metadata=[],
            document_id=document_id,
        )

    qdrant_client.upsert.assert_not_called()


def test_store_embeddings_empty_input_does_not_call_upsert(qdrant_client):
    result = store_embeddings(
        qdrant_client,
        chunks=[],
        vectors=[],
        metadata=[],
        document_id="doc-123",
    )

    assert result == 0
    qdrant_client.upsert.assert_not_called()


def test_delete_document_embeddings_filters_by_document_id(qdrant_client):
    delete_document_embeddings(qdrant_client, "doc-123")

    qdrant_client.delete.assert_called_once()
    call = qdrant_client.delete.call_args.kwargs

    assert call["collection_name"] == QDRANT_COLLECTION
    assert call["wait"] is True

    selector = call["points_selector"]
    assert isinstance(selector, Filter)
    assert selector.must == [
        FieldCondition(
            key="document_id",
            match=MatchValue(value="doc-123"),
        )
    ]


@pytest.mark.parametrize("document_id", ["", "   "])
def test_delete_document_embeddings_rejects_empty_document_id(
    qdrant_client, document_id
):
    with pytest.raises(ValueError, match="document_id darf nicht leer sein"):
        delete_document_embeddings(qdrant_client, document_id)

    qdrant_client.delete.assert_not_called()
