# --------------------------------------------------
# Document Store
# --------------------------------------------------
# This module manages the local SQLite database
# for uploaded documents.
#
# The database stores document metadata.
# Original files are stored separately.
# --------------------------------------------------
import sqlite3
from pathlib import Path

# --------------------------------------------------
# Paths
# --------------------------------------------------
# Project root directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Central data directory.
DATA_DIR = PROJECT_ROOT / "data"

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
                indexed_at TEXT
            )
            """
        )
        # Save the database changes.
        connection.commit()

    finally:
        # Always close the connection.
        connection.close()
