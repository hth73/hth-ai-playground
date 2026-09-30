# --------------------------------------------------
# Manual Persistence Verification
# --------------------------------------------------
# Verifies that a previously indexed document remains
# registered in SQLite and that its vectors remain in
# Qdrant after a container restart.
#
# Usage:
#   python tests/manual_verify_persistence.py <document_id>
# --------------------------------------------------

import argparse
import sys

from qdrant_client.models import FieldCondition, Filter, MatchValue

from rag.m04_vector_store import (
    QDRANT_COLLECTION,
    get_qdrant_client,
)
from rag.m10_document_store import initialize_database, list_documents


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify persistence of an indexed document."
    )
    parser.add_argument("document_id", help="ID of the indexed document")
    args = parser.parse_args()

    print("\n[1/3] Checking SQLite metadata...")
    initialize_database()

    document = next(
        (
            item for item in list_documents()
            if item["document_id"] == args.document_id
        ),
        None,
    )

    if document is None:
        print("ERROR: Document not found in SQLite.", file=sys.stderr)
        return 1

    print(f"Filename: {document['filename']}")
    print(f"Status: {document['status']}")
    print(f"Expected chunks: {document['chunk_count']}")

    if document["status"] != "indexed":
        print("ERROR: Document is not marked as indexed.", file=sys.stderr)
        return 1

    print("\n[2/3] Checking Qdrant after container restart...")
    client = get_qdrant_client()

    points, _ = client.scroll(
        collection_name=QDRANT_COLLECTION,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=args.document_id),
                )
            ]
        ),
        limit=max(document["chunk_count"], 1),
        with_payload=True,
        with_vectors=False,
    )

    actual_count = len(points)
    print(f"Qdrant points found: {actual_count}")

    if actual_count != document["chunk_count"]:
        print(
            "ERROR: Qdrant point count differs from SQLite metadata.",
            file=sys.stderr,
        )
        return 1

    print("\n[3/3] Displaying persisted chunk previews...")
    for number, point in enumerate(points, start=1):
        payload = point.payload or {}
        chunk_text = payload.get("text", "")
        preview = " ".join(chunk_text.split())[:180]
        print(f"Chunk {number} (point {point.id}): {preview}")

    print("\nSUCCESS: SQLite metadata and Qdrant vectors survived the restart.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
