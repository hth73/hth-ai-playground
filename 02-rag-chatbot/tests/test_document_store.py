# --------------------------------------------------
# Document Store Tests
# --------------------------------------------------
import pytest

from pathlib import Path

import rag.m10_document_store as document_store

from rag.m10_document_store import (
    initialize_database,
    get_database_connection,
    calculate_file_hash,
    get_document_by_hash,
    save_document,
    list_documents,
    update_document_status,
    mark_document_indexed,
    DATA_DIR,
    DOCUMENTS_DIR,
    DATABASE_PATH,
)

# --------------------------------------------------
# Test Fixture
# --------------------------------------------------
@pytest.fixture(autouse=True)
def temporary_document_store(tmp_path, monkeypatch):
    """
    Configure a temporary database and document directory. This ensures that tests never modify real project data.
    """

    # Define temporary paths.
    data_dir = tmp_path / "data"
    documents_dir = data_dir / "documents"
    database_path = data_dir / "metadata.db"

    # Replace the module paths with temporary paths.
    monkeypatch.setattr(
        document_store,
        "DATA_DIR",
        data_dir
    )
    monkeypatch.setattr(
        document_store,
        "DOCUMENTS_DIR",
        documents_dir
    )
    monkeypatch.setattr(
        document_store,
        "DATABASE_PATH",
        database_path
    )
    # Initialize the temporary database.
    document_store.initialize_database()

    return {
        "data_dir": data_dir,
        "documents_dir": documents_dir,
        "database_path": database_path
    }

# --------------------------------------------------
# Database Initialization
# --------------------------------------------------
def test_database_initialization(temporary_document_store):

    # Get the temporary database path.
    database_path = temporary_document_store["database_path"]

    # Check if the database file exists.
    assert database_path.exists()

    # Open a database connection.
    connection = document_store.get_database_connection()

    try:
        # Read the table structure.
        result = connection.execute(
            "PRAGMA table_info(documents)"
        ).fetchall()

        # Extract the column names.
        column_names = [
            column["name"]
            for column in result
        ]
        # Verify the expected columns.
        expected_columns = [
            "document_id",
            "filename",
            "stored_path",
            "file_hash",
            "file_size",
            "file_type",
            "status",
            "chunk_count",
            "created_at",
            "indexed_at",
            "last_error",
        ]
        assert column_names == expected_columns

    finally:
        # Close the database connection.
        connection.close()

# --------------------------------------------------
# File Hash
# --------------------------------------------------
def test_calculate_file_hash():

    # Define test content.
    file_content = b"Hello RAG Chatbot"

    # Calculate the hash.
    file_hash = document_store.calculate_file_hash(file_content)

    # Verify that the hash is a SHA-256 hexadecimal string.
    assert len(file_hash) == 64
    assert all(
        character in "0123456789abcdef"
        for character in file_hash
    )

def test_identical_content_produces_identical_hash():

    # Define identical content.
    first_content = b"Same document content"
    second_content = b"Same document content"

    # Calculate both hashes.
    first_hash = document_store.calculate_file_hash(first_content)
    second_hash = document_store.calculate_file_hash(second_content)

    # Verify that the hashes match.
    assert first_hash == second_hash

# --------------------------------------------------
# Save Document
# --------------------------------------------------
def test_save_document(temporary_document_store):

    # Define test content.
    file_content = b"Test document content"

    # Save the document.
    document = document_store.save_document(
        file_content=file_content,
        filename="test.pdf"
    )

    # Verify the metadata.
    assert document["filename"] == "test.pdf"
    assert document["file_size"] == len(file_content)
    assert document["file_type"] == "pdf"
    assert document["status"] == "uploaded"
    assert document["chunk_count"] == 0
    assert document["indexed_at"] is None

    # Verify that a document ID was generated.
    assert document["document_id"]

    # Verify that the original file exists.
    stored_path = Path(document["stored_path"])

    assert stored_path.exists()
    assert stored_path.read_bytes() == file_content

    # Verify that the file is stored in the expected directory.
    assert stored_path.parent == temporary_document_store["documents_dir"]

def test_saved_document_exists_in_database(temporary_document_store):

    # Save a document.
    document = document_store.save_document(
        file_content=b"Database test",
        filename="database.txt"
    )

    # Retrieve the document by its hash.
    result = document_store.get_document_by_hash(
        document["file_hash"]
    )

    # Verify the database record.
    assert result is not None
    assert result["document_id"] == document["document_id"]
    assert result["filename"] == "database.txt"

def test_duplicate_document_is_rejected(temporary_document_store):

    # Define test content.
    file_content = b"Duplicate content"

    # Save the first document.
    document_store.save_document(
        file_content=file_content,
        filename="first.txt"
    )

    # Attempt to save identical content with a different filename.
    with pytest.raises(ValueError, match="Duplicate document"):
        document_store.save_document(
            file_content=file_content,
            filename="second.txt"
        )

    # Verify that only one document was stored.
    connection = document_store.get_database_connection()

    try:

        result = connection.execute(
            "SELECT COUNT(*) FROM documents"
        ).fetchone()

        assert result[0] == 1

    finally:
        connection.close()

def test_empty_document_is_rejected(temporary_document_store):

    # Attempt to save an empty document.
    with pytest.raises(ValueError, match="empty document"):
        document_store.save_document(
            file_content=b"",
            filename="empty.txt"
        )

def test_invalid_filename_is_rejected(temporary_document_store):

    # Attempt to save a document without a valid filename.
    with pytest.raises(ValueError, match="Invalid document filename"):
        document_store.save_document(
            file_content=b"Some content",
            filename=""
        )

# --------------------------------------------------
# Document Lookup
# --------------------------------------------------
def test_get_document_by_unknown_hash_returns_none(
    temporary_document_store
):

    # Search for a hash that does not exist.
    result = document_store.get_document_by_hash(
        "unknown-hash"
    )

    # Verify that no document was found.
    assert result is None

# --------------------------------------------------
# Test: List Documents
# --------------------------------------------------
def test_list_documents_empty():
    """
    Verify that an empty database returns an empty list.
    """

    documents = list_documents()
    assert documents == []

def test_list_documents():
    """
    Verify that all saved documents are returned.
    """

    # Save two documents.
    document_1 = save_document(
        file_content=b"First test document",
        filename="document1.txt",
    )

    document_2 = save_document(
        file_content=b"Second test document",
        filename="document2.txt",
    )

    # Retrieve all documents.
    documents = list_documents()

    # Verify the number of returned documents.
    assert len(documents) == 2

    # Extract document IDs.
    document_ids = [
        document["document_id"]
        for document in documents
    ]

    # Verify that both documents are present.
    assert document_1["document_id"] in document_ids
    assert document_2["document_id"] in document_ids

def test_list_documents_order():
    """
    Verify that documents are sorted by creation date,
    with the newest document first.
    """

    # Save two documents.
    document_1 = save_document(
        file_content=b"Older document",
        filename="older.txt",
    )

    document_2 = save_document(
        file_content=b"Newer document",
        filename="newer.txt",
    )

    # Retrieve all documents.
    documents = list_documents()

    # Verify descending order by creation date.
    assert documents[0]["created_at"] >= documents[1]["created_at"]

    # Verify that the newer document is first.
    assert documents[0]["document_id"] == document_2["document_id"]
    assert documents[1]["document_id"] == document_1["document_id"]

def test_update_document_status(temporary_document_store):
    """Test updating a document status."""

    content = b"Test document"
    document = save_document(
        content,
        "test.txt",
    )

    update_document_status(
        document["document_id"],
        "failed",
        "Test error",
    )

    updated = document_store.get_document_by_hash(
        document["file_hash"]
    )

    assert updated["status"] == "failed"
    assert updated["last_error"] == "Test error"

def test_update_document_status_invalid(temporary_document_store):
    """Test rejecting an invalid document status."""

    content = b"Test document"
    document = save_document(
        content,
        "test.txt",
    )

    with pytest.raises(ValueError):
        update_document_status(
            document["document_id"],
            "invalid",
        )

def test_mark_document_indexed(temporary_document_store):
    """Test marking a document as indexed."""

    content = b"Test document"
    document = save_document(
        content,
        "test.txt",
    )

    mark_document_indexed(
        document["document_id"],
        5,
    )

    updated = get_document_by_hash(
        document["file_hash"]
    )

    assert updated["status"] == "indexed"
    assert updated["chunk_count"] == 5
    assert updated["indexed_at"] is not None
    assert updated["last_error"] is None

def test_mark_document_indexed_negative_chunk_count(temporary_document_store):
    """Test rejecting a negative chunk count."""

    content = b"Test document"
    document = save_document(
        content,
        "test.txt",
    )

    with pytest.raises(ValueError):
        document_store.mark_document_indexed(
            document["document_id"],
            -1,
        )

def test_update_unknown_document(temporary_document_store):
    """Test updating a document that does not exist."""

    with pytest.raises(ValueError):
        document_store.update_document_status(
            "unknown-id",
            "failed",
            "Test error",
        )
