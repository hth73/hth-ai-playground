# --------------------------------------------------
# Document Store Test
# --------------------------------------------------
from rag.m10_document_store import (
    initialize_database,
    get_database_connection,
    DATABASE_PATH,
)

def test_database_initialization():

    # Initialize the database.
    initialize_database()

    # Check if the database file exists.
    assert DATABASE_PATH.exists()

    # Open a database connection.
    connection = get_database_connection()

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
        ]
        assert column_names == expected_columns

    finally:
        # Close the database connection.
        connection.close()
