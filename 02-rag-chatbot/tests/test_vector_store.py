# --------------------------------------------------
# Test: Qdrant Vector Store
# --------------------------------------------------
from rag.m04_vector_store import (
    get_qdrant_client,
    create_collection,
    QDRANT_COLLECTION,
    VECTOR_SIZE,
)

# --------------------------------------------------
# 1. Verbindung zu Qdrant testen
# --------------------------------------------------
print("Connecting to Qdrant...")

client = get_qdrant_client()

print("Qdrant connection successful!")

# --------------------------------------------------
# 2. Collection erstellen
# --------------------------------------------------
print(f"\nChecking collection: {QDRANT_COLLECTION}")

create_collection(client)

print("Collection is ready!")

# --------------------------------------------------
# 3. Collection und Dimensionen überprüfen
# --------------------------------------------------
collection_info = client.get_collection(QDRANT_COLLECTION)

actual_vector_size = (
    collection_info.config.params.vectors.size
)

print(f"\nCollection: {QDRANT_COLLECTION}")
print(f"Vector dimensions: {actual_vector_size}")

assert actual_vector_size == VECTOR_SIZE

print("Vector dimensions check passed!")

# --------------------------------------------------
# 4. Collection erneut prüfen
# --------------------------------------------------
create_collection(client)
print("\nCollection exists and can be reused!")

# --------------------------------------------------
# 5. Alle Collections anzeigen
# --------------------------------------------------
collections = client.get_collections()

print("\nAvailable collections:")

for collection in collections.collections:
    print(f"- {collection.name}")

print("\nAll Qdrant checks passed!")
