# index_chroma.py
# Updated for the new Chroma client architecture (no migration needed)

import json
from chromadb import Client

# 1) Create a Chroma client using the new default API
client = Client()   # simplified, no persist directory required

# 2) Create or get the collection
try:
    col = client.create_collection(name="cctv_devices")
except:
    col = client.get_collection(name="cctv_devices")

# 3) Load JSONL docs created by prepare_rag_docs.py
docs = []
with open("rag_docs_devices.jsonl", "r", encoding="utf-8") as f:
    for line in f:
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

print(f"Indexed {len(ids)} documents into Chroma collection 'cctv_devices'")
# index_chroma.py
# Updated for the new Chroma client architecture (no migration needed)

import json
from chromadb import Client

# 1) Create a Chroma client using the new default API
client = Client()   # simplified, no persist directory required

# 2) Create or get the collection
try:
    col = client.create_collection(name="cctv_devices")
except:
    col = client.get_collection(name="cctv_devices")

# 3) Load JSONL docs created by prepare_rag_docs.py
docs = []
with open("rag_docs_devices.jsonl", "r", encoding="utf-8") as f:
    for line in f:
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

print(f"Indexed {len(ids)} documents into Chroma collection 'cctv_devices'")
