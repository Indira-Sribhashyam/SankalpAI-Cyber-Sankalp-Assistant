# assistant_api.py
# FastAPI assistant service: Chroma retrieval + FREE Groq LLM integration.

from fastapi import FastAPI, HTTPException, Request
import uuid
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import os, time, json
from chromadb import PersistentClient
from dotenv import load_dotenv
from typing import Optional
from groq import AsyncGroq
import numpy as np
import asyncio
from cachetools import TTLCache
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('secai')

# Fast in-memory TTLCache for identical queries
query_cache = TTLCache(maxsize=100, ttl=900)

# Load environment variables
load_dotenv()

# --- GROQ LLM Setup ---
groq_key = os.getenv("GROQ_API_KEY", "").strip()
groq_client = AsyncGroq(api_key=groq_key)

app = FastAPI(title='SankalpAI Assistant API')

@app.middleware("http")
async def log_latency_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Process the actual endpoint
    response = await call_next(request)
    
    # Record elapsed time
    process_time = time.time() - start_time
    
    # Log performance
    logger.info(
        f"{request.method} {request.url.path} "
        f"- Status: {response.status_code} "
        f"- Latency: {process_time:.4f}s"
    )
    
    # Optionally append header for client debug
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

@app.get("/logo")
async def logo():
    # Relative path for cloud readiness
    logo_path = "static/logo.png"
    if os.path.exists(logo_path):
        return FileResponse(logo_path)
    return HTMLResponse("SankalpAI Logo Placeholder", status_code=200)

# -------- Chat UI HTML/CSS/JS --------


# -------- Models --------
class ChatRequest(BaseModel):
    user_id: str
    message: str
    device_id: Optional[str] = None
    image_data: Optional[str] = None

class ActionRequest(BaseModel):
    device_id: Optional[str] = "network"
    context: Optional[str] = ""

# -------- ChromaDB --------
client = PersistentClient(path="./chroma_db")
try:
    col = client.get_collection("cctv_devices")
except:
    col = client.create_collection(name="cctv_devices")

def retrieve_context(query, device_id=None, severity_filter=None, k=5, fetch_k=20):
    try:
        where_filter = None
        conditions = []
        
        if device_id:
            conditions.append({"$or": [{"device_id": device_id}, {"doc_type": "cve_report"}]})
            
        if severity_filter:
            s_list = [severity_filter]
            if severity_filter == "HIGH": s_list = ["CRITICAL", "HIGH"]
            conditions.append({
                "$or": [
                    {"severity": {"$in": s_list}},
                    {"doc_type": "device_report"}
                ]
            })
            
        if len(conditions) == 1:
            where_filter = conditions[0]
        elif len(conditions) > 1:
            where_filter = {"$and": conditions}
        
        # Semantic Retrieval
        result = col.query(query_texts=[query], n_results=10, where=where_filter)
        if not result.get("documents") or not result["documents"][0]:
            return []
            
        docs = result["documents"][0]
        metas = result["metadatas"][0]
        ids = result["ids"][0]
        distances = result["distances"][0] if "distances" in result else [0]*len(docs)
        
        # Lightweight Reranking (Distance based + Limit)
        final_docs = []
        for i in range(len(docs)):
            final_docs.append({
                "content": docs[i], 
                "metadata": metas[i], 
                "id": ids[i],
                "score": float(1 - distances[i]) # Simple distance based score
            })
            
        # Optional: Sort by distance (if not already)
        return final_docs
    except Exception as e:
        logger.error(f"Retrieval Error: {e}")
        return []

# -------- Chat Engine --------
async def run_llm(system_prompt, user_prompt, image_data=None):
    try:
        if image_data:
            model = "llama-3.2-11b-vision-preview"
            content = [
                {"type": "text", "text": user_prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
            ]
        else:
            model = "llama-3.1-8b-instant"
            content = user_prompt

        completion = await groq_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            max_tokens=1024,
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM Error: {e}"); return f"[LLM Error] {str(e)}"

async def classify_intent(query: str):
    system_prompt = (
        "You are an intent classifier for a security assistant. Output JSON only. "
        "Keys: 'intent' ('info', 'run_scan', 'create_ticket'), "
        "and 'severity_filter' (one of: 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', or null). "
        "CRITICAL: Only return 'run_scan' or 'create_ticket' if the user EXPLICITLY asks to PERFORM an action (e.g., 'run', 'start', 'open', 'create'). "
        "If they are just asking for information, even about vulnerabilities, return 'info'."
    )
    try:
        completion = await groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        data = json.loads(completion.choices[0].message.content)
        return {"intent": data.get("intent", "info"), "severity_filter": data.get("severity_filter", None)}
    except Exception:
        return {"intent": "info", "severity_filter": None}

@app.post("/chat")
async def chat(req: ChatRequest):
    # Semantic caching
    cache_key = f"{req.user_id}:{req.device_id}:{req.message}"
    if not req.image_data and cache_key in query_cache:
        logger.info(f"Cache HIT for query: {req.message}")
        return query_cache[cache_key]

    # FAST-PATH for simple greetings
    greetings = {"hi", "hello", "hey", "hola", "sup", "howdy", "greetings"}
    if not req.image_data and req.message.strip().lower() in greetings:
        res = {
            "response": "Hello! I am your SankalpAI Assistant. How can I help you secure your environment?",
            "sources": []
        }
        query_cache[cache_key] = res
        return res

    # NEW: Classify user intent dynamically
    classification = await classify_intent(req.message)
    intent = classification.get("intent", "info")
    severity_filter = classification.get("severity_filter")
    
    if intent == "run_scan":
        import uuid
        job_id = f"scan-{uuid.uuid4().hex[:8]}"
        return {
            "response": f"🛡️ Action Triggered: Initiating vulnerability scan on {req.device_id or 'the system'}. Job ID: {job_id}",
            "sources": []
        }
    elif intent == "create_ticket":
        import time
        ticket_id = f"TICKET-{time.time()}"
        return {
            "response": f"🎫 Action Triggered: Security incident ticket generated successfully. Ticket ID: {ticket_id}",
            "sources": []
        }

    # 1. Retrieve Context in background thread (unblocks async loop)
    ctx = await asyncio.to_thread(retrieve_context, req.message, device_id=req.device_id, severity_filter=severity_filter)
    context_text = "\n\n".join([f"<LOG_ENTRY id=\"{d.get('id')}\">\n{d['content']}\n</LOG_ENTRY>" for d in ctx])
    
    # 2. Prepare Hybrid System Prompt
    system_prompt = (
        "You are SecAI, an advanced assistant for CCTV security. "
        "You operate in HYBRID KNOWLEDGE MODE:\n"
        "1. LOCAL DATA: If the user asks about specific devices, IPs, or logs in their environment, use the provided <LOG_ENTRY> tags. ALWAYS cite the [ID] when using local data.\n"
        "2. GENERAL KNOWLEDGE: If the query is about general cybersecurity concepts (e.g., 'What is a buffer overflow?'), provide an accurate explanation using your internal knowledge.\n"
        "3. GROUNDING: If the user asks about a specific device/resource NOT found in the <LOG_ENTRY> blocks, state: 'I could not find [Device Name] in your local logs.' Do NOT invent local data.\n"
        "4. STYLE: Use small paragraphs and bullet points for high readability."
    )
    user_prompt = f"LOCAL DATABASE CONTEXT:\n{context_text}\n\nUSER QUERY: {req.message}"
    
    # 3. Generate Response
    response = await run_llm(system_prompt, user_prompt, image_data=req.image_data)
    
    response_data = {"response": response, "sources": ctx}
    if not req.image_data:
        query_cache[cache_key] = response_data
        
    return response_data

# -------- Actions --------
@app.post("/action/run_scan")
async def run_scan(req: ActionRequest):
    target = req.device_id if req.device_id else "network"
    logger.info(f"Triggering remote scan on {target}...")
    await asyncio.sleep(2) # Simulate scan
    
    prompt = f"Write a 2-sentence mock vulnerability scan report for {target}. Mention 1 open port and a quick remediation."
    findings = await run_llm("You are an automated scanner.", prompt)
    
    return {
        "job_id": f"scan-{uuid.uuid4().hex[:8]}",
        "status": "COMPLETED",
        "findings": findings
    }

@app.post("/action/create_ticket")
async def create_ticket(req: ActionRequest):
    target = req.device_id if req.device_id else "unknown"
    logger.info(f"Opening JIRA Incident for {target}")
    await asyncio.sleep(1) # Simulate Jira
    
    ticket_payload = {"project": "SEC", "summary": f"Incident on {target}", "description": req.context}
    logger.info(f"Forwarded to ticketing system: {json.dumps(ticket_payload)}")
    
    return {"ticket_id": f"SEC-INC-{int(time.time())}", "status": "CREATED_SUCCESSFULLY"}

@app.get("/", response_class=FileResponse)
async def root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

