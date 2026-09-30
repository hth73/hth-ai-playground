# --------------------------------------------------
# Document Store
# --------------------------------------------------
# This module manages the local SQLite database
# and persistent storage for uploaded documents.
#
# The database stores document metadata.
# Original files are stored separately.
# --------------------------------------------------
import hashlib
import sqlite3
import uuid

from datetime import datetime, timezone
from pathlib import Path

# --------------------------------------------------
# Paths
# --------------------------------------------------
# Project root directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Central data directory.
DATA_DIR = PROJECT_ROOT / "data"

# Directory for original documents.
DOCUMENTS_DIR = DATA_DIR / "documents"

# SQLite database file.
DATABASE_PATH = DATA_DIR / "metadata.db"

# --------------------------------------------------
# Database Connection
# --------------------------------------------------
def get_database_connection() -> sqlite3.Connection:
    """
    Open a connection to the SQLite database.

    The database file is created automatically
    if it does not exist.
    """

    # Ensure that the data directory exists.
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Open the database connection.
    connection = sqlite3.connect(DATABASE_PATH)

    # Return database rows as dictionary-like objects.
    connection.row_factory = sqlite3.Row

    return connection

# --------------------------------------------------
# Initialize Database
# --------------------------------------------------
def initialize_database() -> None:
    """
    Create the documents table if it does not exist. Existing records are preserved.
    """
    connection = get_database_connection()
    try:

        # Create the documents table.
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                stored_path TEXT NOT NULL,
                file_hash TEXT NOT NULL UNIQUE,
                file_size INTEGER NOT NULL,
                file_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'uploaded'
                    CHECK (
                        status IN (
                            'uploaded',
                            'indexed',
                            'failed'
                        )
                    ),
                chunk_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                indexed_at TEXT,
                last_error TEXT
            )
            """
        )
        # Check whether the last_error column already exists.
        cursor = connection.execute(
            "PRAGMA table_info(documents)"
        )

        columns = [row["name"] for row in cursor.fetchall()]

        # Add the column to existing databases if necessary.
        if "last_error" not in columns:
            connection.execute(
                "ALTER TABLE documents ADD COLUMN last_error TEXT"
            )
        # Save the database changes.
        connection.commit()

    finally:
        # Always close the connection.
        connection.close()

# --------------------------------------------------
# Calculate File Hash
# --------------------------------------------------
def calculate_file_hash(file_content: bytes) -> str:
    """
    Calculate the SHA-256 hash of a file's content. The hash is used to identify duplicate files.
    """

    # Create a SHA-256 hash object.
    file_hash = hashlib.sha256()

    # Add the file content to the hash.
    file_hash.update(file_content)

    # Return the hexadecimal hash string.
    return file_hash.hexdigest()

# --------------------------------------------------
# Get Document by Hash
# --------------------------------------------------
def get_document_by_hash(file_hash: str) -> dict | None:
    """
    Find a document by its SHA-256 hash.

    Returns the document as a dictionary.
    Returns None if no matching document exists.
    """

    connection = get_database_connection()
    try:
        # Search for the document.
        result = connection.execute(
            """
            SELECT *
            FROM documents
            WHERE file_hash = ?
            """,
            (file_hash,)
        ).fetchone()

        # Return None if no document was found.
        if result is None:
            return None

        # Convert the database row into a dictionary.
        return dict(result)

    finally:
        # Always close the connection.
        connection.close()

# --------------------------------------------------
# Save Document
# --------------------------------------------------
def save_document(
    file_content: bytes,
    filename: str
) -> dict:
    """
    Save an original document and its metadata.

    The original file is stored using a UUID.
    Duplicate files are rejected based on their hash.

    Returns the newly created document record.

    Raises ValueError if the file is empty or
    a document with the same content already exists.
    """

    # Reject empty files.
    if not file_content:
        raise ValueError("Cannot save an empty document.")

    # Extract the filename without any directory path.
    original_filename = Path(filename).name

    # Reject filenames that are empty or invalid.
    if not original_filename or original_filename in {".", ".."}:
        raise ValueError("Invalid document filename.")

    # Calculate the SHA-256 hash.
    file_hash = calculate_file_hash(file_content)

    # Check whether the document already exists.
    existing_document = get_document_by_hash(file_hash)

    if existing_document is not None:
        raise ValueError(
            f"Duplicate document: {original_filename}"
        )

    # Generate a unique document ID.
    document_id = str(uuid.uuid4())

    # Preserve the original file extension.
    file_extension = Path(original_filename).suffix.lower()

    # Create a unique storage filename.
    stored_filename = f"{document_id}{file_extension}"

    # Define the destination path.
    stored_path = DOCUMENTS_DIR / stored_filename

    # Determine the file type.
    file_type = file_extension.lstrip(".")

    # Get the file size in bytes.
    file_size = len(file_content)

    # Generate a UTC timestamp.
    created_at = datetime.now(timezone.utc).isoformat()

    # Ensure that the document directory exists.
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

    # Save the original file.
    stored_path.write_bytes(file_content)

    connection = get_database_connection()
    try:
        # Insert the document metadata.
        connection.execute(
            """
            INSERT INTO documents (
                document_id,
                filename,
                stored_path,
                file_hash,
                file_size,
                file_type,
                status,
                chunk_count,
                created_at,
                indexed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                document_id,
                original_filename,
                str(stored_path),
                file_hash,
                file_size,
                file_type,
                "uploaded",
                0,
                created_at,
                None
            )
        )
        # Save the database changes.
        connection.commit()

    except Exception:
        # Remove the original file if database insertion fails.
        stored_path.unlink(missing_ok=True)

        # Propagate the original exception.
        raise

    finally:
        # Always close the connection.
        connection.close()

    # Return the newly created document record.
    return {
        "document_id": document_id,
        "filename": original_filename,
        "stored_path": str(stored_path),
        "file_hash": file_hash,
        "file_size": file_size,
        "file_type": file_type,
        "status": "uploaded",
        "chunk_count": 0,
        "created_at": created_at,
        "indexed_at": None
    }

# --------------------------------------------------
# List Document
# --------------------------------------------------
def list_documents() -> list[dict]:
    """
    Retrieve all documents from the database.
    Returns:
        A list of document records as dictionaries.
    """

    connection = get_database_connection()
    try:
        cursor = connection.execute(
            """
            SELECT *
            FROM documents
            ORDER BY created_at DESC
            """
        )
        return [dict(row) for row in cursor.fetchall()]

    finally:
        connection.close()

# --------------------------------------------------
# Update Document Status
# --------------------------------------------------
def update_document_status(
    document_id: str,
    status: str,
    error_message: str | None = None,
) -> None:
    """
    Update the status of a document.

    Optionally stores an error message if indexing failed.

    Raises:
        ValueError: If the status is invalid.
        ValueError: If the document does not exist.
    """

    # Allowed document statuses.
    allowed_statuses = {"uploaded", "indexed", "failed"}

    # Validate the requested status.
    if status not in allowed_statuses:
        raise ValueError(f"Invalid document status: {status}")

    connection = get_database_connection()

    try:
        # Update the document record.
        cursor = connection.execute(
            """
            UPDATE documents
            SET status = ?,
                last_error = ?
            WHERE document_id = ?
            """,
            (status, error_message, document_id),
        )

        # Check whether a document was updated.
        if cursor.rowcount == 0:
            raise ValueError(
                f"Document not found: {document_id}"
            )

        # Save the changes.
        connection.commit()

    finally:
        connection.close()

# --------------------------------------------------
# Mark Document as Indexed
# --------------------------------------------------
def mark_document_indexed(
    document_id: str,
    chunk_count: int,
) -> None:
    """
    Mark a document as successfully indexed.

    Stores the chunk count and indexing timestamp.
    Clears any previous error message.

    Raises:
        ValueError: If the chunk count is negative.
        ValueError: If the document does not exist.
    """

    # Validate the chunk count.
    if chunk_count < 0:
        raise ValueError("Chunk count cannot be negative.")

    # Generate a UTC timestamp.
    indexed_at = datetime.now(timezone.utc).isoformat()

    connection = get_database_connection()

    try:
        # Update the indexing information.
        cursor = connection.execute(
            """
            UPDATE documents
            SET status = ?,
                chunk_count = ?,
                indexed_at = ?,
                last_error = NULL
            WHERE document_id = ?
            """,
            ("indexed", chunk_count, indexed_at, document_id),
        )

        # Check whether a document was updated.
        if cursor.rowcount == 0:
            raise ValueError(
                f"Document not found: {document_id}"
            )

        # Save the changes.
        connection.commit()

    finally:
        connection.close()
