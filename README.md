# SecAI Assistant MVP - Local Repo

This small repo contains a minimal assistant that uses your CSV (`/mnt/data/devices_scan 2.csv`)
to build a retrieval (RAG) knowledge base and a tiny FastAPI service to answer questions.

## Files
- prepare_rag_docs.py  : convert CSV -> rag_docs_devices.jsonl
- index_chroma.py      : index JSONL into local Chroma (duckdb+parquet)
- assistant_api.py     : FastAPI assistant (endpoints: /chat, /action/run_scan, /action/create_ticket)
- requirements.txt     : python packages
- HANDOVER.md          : short handover instructions

## Quickstart (local)
1. Create venv and install:
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Prepare RAG docs:
   ```
   python prepare_rag_docs.py
   ```

3. Index into Chroma:
   ```
   python index_chroma.py
   ```

4. Run the assistant:
   ```
   uvicorn assistant_api:app --reload --port 8000
   ```

5. Test:
   ```
   curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d '{"user_id":"you","message":"Why is device device-0 risky?","device_id":"device-0"}'
   ```

## Notes
- The LLM call in `assistant_api.py` is a placeholder. Replace `llm_call()` with your OpenAI or other LLM invocation.
- The scripts reference your data file at `/mnt/data/devices_scan 2.csv`. Keep that path or update scripts accordingly.
