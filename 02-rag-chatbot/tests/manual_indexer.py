# --------------------------------------------------
# Manual Indexer Integration Test
# --------------------------------------------------
# Uploads and indexes one document using the real SQLite,
# Ollama, and Qdrant services.
#
# Usage:
#   python tests/manual_indexer.py path/to/document.pdf
#
# This script does not delete existing documents or vectors.
# --------------------------------------------------

import argparse
import sys
from pathlib import Path

from qdrant_client.models import FieldCondition, Filter, MatchValue

from rag.m04_vector_store import (
    QDRANT_COLLECTION,
    get_qdrant_client,
)
from rag.m10_document_store import (
    initialize_database,
    list_documents,
    save_document,
)
from rag.m11_indexer import index_document


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload and index a document using the real RAG services."
    )
    parser.add_argument(
        "document",
        type=Path,
        help="Path to a supported PDF, TXT, or Markdown document.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_path = args.document.expanduser().resolve()

    if not source_path.is_file():
        print(f"ERROR: File not found: {source_path}", file=sys.stderr)
        return 1

    file_content = source_path.read_bytes()
    if not file_content:
        print("ERROR: The selected file is empty.", file=sys.stderr)
        return 1

    print("\n[1/5] Initializing SQLite database...")
    initialize_database()

    print(f"\n[2/5] Registering document: {source_path.name}")
    try:
        document = save_document(
            file_content=file_content,
            filename=source_path.name,
        )
    except ValueError as error:
        print(f"ERROR: Could not register document: {error}", file=sys.stderr)
        return 1

    document_id = document["document_id"]
    print(f"Document ID: {document_id}")
    print(f"Stored path: {document['stored_path']}")

    print("\n[3/5] Running indexer (Ollama + Qdrant)...")
    try:
        indexed_chunk_count = index_document(document_id)
    except Exception as error:
        print(f"ERROR: Indexing failed: {error}", file=sys.stderr)
        current = next(
            (item for item in list_documents()
             if item["document_id"] == document_id),
            None,
        )
        if current:
            print(f"Database status: {current['status']}")
            if current.get("last_error"):
                print(f"Recorded error: {current['last_error']}")
        return 1

    print(f"Indexer reported {indexed_chunk_count} stored chunks.")

    print("\n[4/5] Verifying SQLite metadata...")
    record = next(
        (item for item in list_documents()
         if item["document_id"] == document_id),
        None,
    )
    if record is None:
        print("ERROR: Document record is missing from SQLite.", file=sys.stderr)
        return 1

    print(f"Status: {record['status']}")
    print(f"Chunk count: {record['chunk_count']}")
    print(f"Indexed at: {record['indexed_at']}")

    if record["status"] != "indexed":
        print("ERROR: Document status is not 'indexed'.", file=sys.stderr)
        return 1

    if record["chunk_count"] != indexed_chunk_count:
        print("ERROR: SQLite chunk count does not match indexer result.", file=sys.stderr)
        return 1

    print("\n[5/5] Verifying Qdrant points...")
    client = get_qdrant_client()
    result, _ = client.scroll(
        collection_name=QDRANT_COLLECTION,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id),
                )
            ]
        ),
        limit=max(indexed_chunk_count, 1),
        with_payload=True,
        with_vectors=False,
    )

    qdrant_count = len(result)
    print(f"Qdrant points found for document: {qdrant_count}")

    if qdrant_count != indexed_chunk_count:
        print(
            "ERROR: Qdrant point count does not match the indexed chunk count.",
            file=sys.stderr,
        )
        return 1

    print("\nSUCCESS: Document upload, indexing, and metadata/vector checks passed.")
    print(
        "Next: restart the Qdrant container, then run a separate persistence "
        "verification before deleting or modifying any data."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
