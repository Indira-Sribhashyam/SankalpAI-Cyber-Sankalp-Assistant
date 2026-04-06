# index_chroma.py
# Updated for persistent storage and cleaned up duplication.

import json
from chromadb import PersistentClient

# 1) Create a Chroma client using persistent storage
client = PersistentClient(path="./chroma_db")

# 2) Create or get the collection
try:
    col = client.create_collection(name="cctv_devices")
except:
    col = client.get_collection(name="cctv_devices")

# 3) Load JSONL docs created by prepare_rag_docs.py
docs = []
with open("rag_docs_devices.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            docs.append(json.loads(line))

ids = [d["id"] for d in docs]
documents = [d["content"] for d in docs]
metadatas = [d["metadata"] for d in docs]

# 4) Upload into the Chroma collection
col.upsert(
    ids=ids,
    documents=documents,
    metadatas=metadatas
)

print(f"Indexed {len(ids)} documents into Chroma collection 'cctv_devices' at './chroma_db'")
